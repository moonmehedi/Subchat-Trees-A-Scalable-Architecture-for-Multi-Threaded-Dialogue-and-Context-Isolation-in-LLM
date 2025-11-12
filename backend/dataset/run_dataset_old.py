#!/usr/bin/env python3
"""
Dataset Execution Script

Runs all dataset scenarios sequentially, makes API calls,
validates responses, and generates comprehensive reports.

Usage:
    python run_dataset.py
    python run_dataset.py --scenario 02_python_ambiguity  # Run specific scenario
    python run_dataset.py --skip-delay  # Run without delays (faster but may hit rate limits)
"""

import json
import time
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataset_logger import DatasetLogger


class DatasetRunner:
    """Execute dataset scenarios and validate results."""
    
    def __init__(self, base_url: str = "http://localhost:8000", delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay  # Delay between API calls
        self.logger = DatasetLogger()
        
        # Track current state
        self.current_tree_id = None
        self.current_node_id = None
        self.node_map = {}  # Maps node names to IDs
        
    def load_scenario(self, scenario_file: Path) -> Dict[str, Any]:
        """Load scenario from JSON file."""
        with open(scenario_file, 'r') as f:
            return json.load(f)
    
    def send_message(self, message: str, node_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to the API."""
        target_node_id = node_id or self.current_node_id
        
        # If no node exists yet, create a new conversation
        if not target_node_id:
            conversation = self.create_conversation()
            if "error" in conversation:
                return conversation
            target_node_id = conversation.get("node_id")
            self.current_node_id = target_node_id
            self.node_map["main"] = target_node_id
        
        url = f"{self.base_url}/api/conversations/{target_node_id}/messages"
        
        payload = {
            "message": message
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            result["node_id"] = target_node_id  # Add node_id to response
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return {"error": str(e)}
    
    def create_conversation(self, title: str = "New Chat") -> Dict[str, Any]:
        """Create a new conversation."""
        url = f"{self.base_url}/api/conversations"
        
        payload = {
            "title": title
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return {"error": str(e)}
    
    def create_subchat(self, parent_node_id: str, first_message: str, subchat_name: str) -> Dict[str, Any]:
        """Create a new subchat."""
        url = f"{self.base_url}/api/conversations/{parent_node_id}/subchats"
        
        payload = {
            "message": first_message
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            subchat_data = response.json()
            
            # Send the first message to the new subchat
            new_node_id = subchat_data.get("node_id")
            message_result = self.send_message(first_message, new_node_id)
            
            # Combine results
            result = {
                "node_id": new_node_id,
                "response": message_result.get("response", ""),
                "subchat_data": subchat_data
            }
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return {"error": str(e)}
    
    def get_tree_structure(self) -> Dict[str, Any]:
        """Get current tree structure."""
        url = f"{self.base_url}/api/tree-structure"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return {"error": str(e)}
    
    def run_scenario(self, scenario_file: Path) -> bool:
        """
        Run a single scenario.
        
        Returns:
            True if all tests passed, False otherwise
        """
        scenario = self.load_scenario(scenario_file)
        
        # Start scenario
        self.logger.start_scenario(
            scenario["scenario_name"],
            scenario["description"]
        )
        
        # Reset state
        self.current_tree_id = None
        self.current_node_id = None
        self.node_map = {"main": None}  # Will be set on first message
        
        # Execute conversation steps
        for conv in scenario["conversations"]:
            step = conv["step"]
            action = conv["action"]
            
            # Add delay to avoid rate limits
            if step > 1:
                time.sleep(self.delay)
            
            try:
                if action == "send_message":
                    self._execute_message(step, conv)
                elif action == "create_subchat":
                    self._execute_create_subchat(step, conv)
                elif action == "switch_to_node":
                    self._execute_switch_node(step, conv)
                else:
                    print(f"⚠️  Unknown action: {action}")
            
            except Exception as e:
                print(f"❌ Error in step {step}: {e}")
                import traceback
                traceback.print_exc()
        
        # End scenario
        self.logger.end_scenario()
        
        # Return pass/fail
        if self.logger.test_results:
            last_scenario = self.logger.test_results[-1]
            return last_scenario["failed"] == 0
        return False
    
    def _execute_message(self, step: int, conv: Dict[str, Any]):
        """Execute a send_message action."""
        node_type = conv["node_type"]
        message = conv["message"]
        
        # Determine which node to use
        if node_type == "main":
            target_node_id = self.node_map.get("main")
        elif node_type.startswith("subchat_"):
            subchat_num = node_type.split("_")[1]
            target_node_id = self.node_map.get(f"subchat_{subchat_num}")
        else:
            target_node_id = self.current_node_id
        
        # Send message
        result = self.send_message(message, target_node_id)
        
        if "error" in result:
            self.logger.log_message(step, node_type, message, f"ERROR: {result['error']}")
            return
        
        response = result.get("response", "")
        
        # Update current node if this is first message
        if step == 1:
            self.current_node_id = result.get("node_id")
            self.node_map["main"] = self.current_node_id
        
        # Log message
        self.logger.log_message(step, node_type, message, response)
        
        # Validate if this is a test
        if conv.get("should_retrieve") or conv.get("expected_response_contains"):
            self.logger.validate_test(
                step=step,
                test_type="retrieval" if conv.get("should_retrieve") else "response_check",
                query=message,
                response=response,
                expected_contains=conv.get("expected_response_contains"),
                should_not_contain=conv.get("should_not_contain"),
                expected_retrieval=conv.get("expected_retrieval")
            )
    
    def _execute_create_subchat(self, step: int, conv: Dict[str, Any]):
        """Execute a create_subchat action."""
        parent_node = conv.get("parent_node", "main")
        subchat_name = conv["subchat_name"]
        message = conv["message"]
        
        parent_node_id = self.node_map.get(parent_node)
        
        self.logger.log_action(
            step,
            "CREATE_SUBCHAT",
            f"Creating subchat '{subchat_name}' from {parent_node}"
        )
        
        # Create subchat
        result = self.create_subchat(parent_node_id, message, subchat_name)
        
        if "error" in result:
            self.logger.log_message(step, "subchat", message, f"ERROR: {result['error']}")
            return
        
        response = result.get("response", "")
        new_node_id = result.get("node_id")
        
        # Track subchat node
        subchat_count = sum(1 for k in self.node_map.keys() if k.startswith("subchat_"))
        self.node_map[f"subchat_{subchat_count + 1}"] = new_node_id
        self.current_node_id = new_node_id
        
        # Log response
        self.logger.log_message(step, f"subchat_{subchat_count + 1}", message, response)
        
        # Validate if needed
        if conv.get("expected_response_contains"):
            self.logger.validate_test(
                step=step,
                test_type="subchat_creation",
                query=message,
                response=response,
                expected_contains=conv.get("expected_response_contains"),
                should_not_contain=conv.get("should_not_contain")
            )
    
    def _execute_switch_node(self, step: int, conv: Dict[str, Any]):
        """Execute a switch_to_node action."""
        node_type = conv["node_type"]
        message = conv["message"]
        
        # Get target node
        if node_type == "main":
            target_node_id = self.node_map.get("main")
        elif node_type.startswith("subchat_"):
            target_node_id = self.node_map.get(node_type)
        else:
            target_node_id = self.current_node_id
        
        self.logger.log_action(
            step,
            "SWITCH_NODE",
            f"Switching to {node_type}"
        )
        
        # Update current node
        self.current_node_id = target_node_id
        
        # Send message in new context
        result = self.send_message(message, target_node_id)
        
        if "error" in result:
            self.logger.log_message(step, node_type, message, f"ERROR: {result['error']}")
            return
        
        response = result.get("response", "")
        
        # Log message
        self.logger.log_message(step, node_type, message, response)
        
        # Validate (switch tests are critical for context isolation)
        if conv.get("should_retrieve") or conv.get("should_not_contain"):
            self.logger.validate_test(
                step=step,
                test_type="context_isolation",
                query=message,
                response=response,
                expected_contains=conv.get("expected_response_contains"),
                should_not_contain=conv.get("should_not_contain"),
                expected_retrieval=conv.get("expected_retrieval")
            )
    
    def run_all_scenarios(self, scenarios_dir: Path):
        """Run all scenarios in the directory."""
        scenario_files = sorted(scenarios_dir.glob("*.json"))
        
        print(f"\n🚀 Starting dataset execution...")
        print(f"📁 Found {len(scenario_files)} scenarios")
        print(f"🌐 API: {self.base_url}")
        print(f"⏱️  Delay: {self.delay}s between requests\n")
        
        # Test API connection
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            print("✅ API connection successful\n")
        except:
            print("❌ Cannot connect to API. Make sure the backend is running!")
            print(f"   Expected at: {self.base_url}")
            return
        
        # Run each scenario
        for scenario_file in scenario_files:
            try:
                self.run_scenario(scenario_file)
            except Exception as e:
                print(f"❌ Fatal error in scenario {scenario_file.name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Generate final report
        print("\n" + "="*80)
        print("📊 Generating final report...")
        print("="*80 + "\n")
        self.logger.generate_final_report()


def main():
    parser = argparse.ArgumentParser(description="Run dataset testing scenarios")
    parser.add_argument("--scenario", help="Run specific scenario file (e.g., 02_python_ambiguity.json)")
    parser.add_argument("--skip-delay", action="store_true", help="Skip delays between requests")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    delay = 0.0 if args.skip_delay else 1.0
    runner = DatasetRunner(base_url=args.base_url, delay=delay)
    
    scenarios_dir = Path(__file__).parent / "scenarios"
    
    if args.scenario:
        # Run specific scenario
        scenario_file = scenarios_dir / args.scenario
        if not scenario_file.exists():
            scenario_file = scenarios_dir / f"{args.scenario}.json"
        
        if not scenario_file.exists():
            print(f"❌ Scenario file not found: {args.scenario}")
            return
        
        print(f"🎯 Running specific scenario: {scenario_file.name}\n")
        runner.run_scenario(scenario_file)
        runner.logger.generate_final_report()
    else:
        # Run all scenarios
        runner.run_all_scenarios(scenarios_dir)


if __name__ == "__main__":
    main()
