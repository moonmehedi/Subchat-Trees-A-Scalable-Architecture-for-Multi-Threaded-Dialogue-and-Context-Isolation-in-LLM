#!/usr/bin/env python3
"""
Dataset Execution Script - Two-Phase Approach

Phase 1: POPULATION (scenarios 01-10)
  - Just run conversations to populate vector store
  - Show progress bar
  - No validation

Phase 2: EVALUATION (scenarios 11-12)
  - Run retrieval and isolation tests
  - Dual evaluation: Keyword + AI
  - Comprehensive logging

Usage:
    python run_dataset.py                    # Run all scenarios
    python run_dataset.py --phase 1          # Just population
    python run_dataset.py --phase 2          # Just evaluation
    python run_dataset.py --skip-delay       # No delays
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from backend directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

import json
import time
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataset_logger import DatasetLogger
from ai_evaluator import AIEvaluator


class DatasetRunner:
    """Execute dataset scenarios with two-phase approach."""
    
    def __init__(self, base_url: str = "http://localhost:8000", delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        
        # Setup logs directory
        self.logs_dir = Path(__file__).parent / "logs" / "dataset-results"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = DatasetLogger()
        self.ai_evaluator = AIEvaluator()
        
        # Track state
        self.current_node_id = None
        self.node_map = {}  # Scenario-wise node tracking
        self.global_node_map = {}  # Cross-scenario node tracking for evaluation
        
        # Setup execution log in dataset logs directory
        self.exec_log = self.logs_dir / "EXECUTION.log"
        
        # Clear previous logs
        with open(self.exec_log, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write(f"DATASET EXECUTION LOG\n")
            f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
        
        # Clear AI evaluation log
        ai_eval_log = self.logs_dir / "AI_EVALUATION.log"
        with open(ai_eval_log, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write(f"AI EVALUATION LOG\n")
            f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
        
        # Clear component-testing logs (overwrite mode)
        component_log_dir = Path(__file__).parent.parent / "logs" / "component-testing"
        if component_log_dir.exists():
            for log_file in component_log_dir.glob("*.log"):
                with open(log_file, 'w') as f:
                    f.write(f"{'='*80}\n")
                    f.write(f"{log_file.stem} LOG\n")
                    f.write(f"Dataset Test Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"{'='*80}\n\n")
        
        # Clear component-testing-full logs (append mode)
        component_full_log_dir = Path(__file__).parent.parent / "logs" / "component-testing-full"
        if component_full_log_dir.exists():
            for log_file in ["VECTOR_STORE.log", "RETRIEVAL.log", "COT_THINKING.log", "BUFFER.log"]:
                log_path = component_full_log_dir / log_file
                if log_path.exists():
                    with open(log_path, 'w') as f:
                        f.write(f"{'='*80}\n")
                        f.write(f"{log_file.replace('.log', '')} LOG\n")
                        f.write(f"Dataset Test Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"{'='*80}\n\n")


        
    def load_scenario(self, scenario_file: Path) -> Dict[str, Any]:
        """Load scenario from JSON file."""
        with open(scenario_file, 'r') as f:
            return json.load(f)
    
    def _log(self, message: str, to_console: bool = False):
        """Log message to execution log file."""
        timestamp = time.strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {message}\n"
        
        with open(self.exec_log, 'a') as f:
            f.write(log_msg)
        
        if to_console:
            print(message)
    
    def send_message(self, message: str, node_id: Optional[str] = None, disable_rag: bool = False) -> Dict[str, Any]:
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
            "message": message,
            "disable_rag": disable_rag  # Pass the flag to skip RAG during population
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            result["node_id"] = target_node_id
            return result
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def create_conversation(self, title: str = "New Chat") -> Dict[str, Any]:
        """Create a new conversation."""
        url = f"{self.base_url}/api/conversations"
        
        try:
            response = requests.post(url, json={"title": title})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def create_subchat(self, parent_node_id: str, first_message: str) -> Dict[str, Any]:
        """Create a new subchat."""
        url = f"{self.base_url}/api/conversations/{parent_node_id}/subchats"
        
        try:
            # API expects "title" field, not "message"
            response = requests.post(url, json={"title": first_message[:50]})  # Use first 50 chars as title
            response.raise_for_status()
            subchat_data = response.json()
            
            # Send the first message
            new_node_id = subchat_data.get("node_id")
            message_result = self.send_message(first_message, new_node_id)
            
            return {
                "node_id": new_node_id,
                "response": message_result.get("response", ""),
                "subchat_data": subchat_data
            }
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def run_population_scenario(self, scenario_file: Path, scenario_num: int, total: int):
        """Run a population scenario (no tests, just conversations)."""
        scenario = self.load_scenario(scenario_file)
        
        print(f"\n{'='*80}")
        print(f"📦 [{scenario_num}/{total}] {scenario['scenario_name']}")
        print(f"{'='*80}")
        
        self._log(f"\n{'='*80}")
        self._log(f"SCENARIO {scenario_num}/{total}: {scenario['scenario_name']}")
        self._log(f"File: {scenario_file.name}")
        self._log(f"{'='*80}")
        
        # Reset state for new scenario
        self.current_node_id = None
        self.node_map = {"main": None}
        
        total_steps = len(scenario["conversations"])
        
        for i, conv in enumerate(scenario["conversations"], 1):
            step = conv["step"]
            action = conv["action"]
            message = conv["message"]
            
            # More detailed progress indicator
            progress = f"[{i}/{total_steps}]"
            message_preview = message[:50] + "..." if len(message) > 50 else message
            print(f"\n{progress} {action:15} | {message_preview}", flush=True)
            print(f"       → ", end="", flush=True)
            
            self._log(f"\nStep {step}/{total_steps}: {action}")
            self._log(f"  Message: {message}")
            
            if step > 1:
                time.sleep(self.delay)
            
            start_time = time.time()
            
            try:
                if action == "send_message":
                    node_type = conv.get("node_type", "main")
                    target_node = self._get_target_node(node_type)
                    
                    print(f"Sending to {node_type} [RAG:OFF]...", end="", flush=True)
                    self._log(f"  Target: {node_type} (node_id: {target_node or 'NEW'}) [RAG DISABLED]")
                    
                    # 🚀 POPULATION: Disable RAG for faster indexing
                    result = self.send_message(message, target_node, disable_rag=True)
                    elapsed = time.time() - start_time
                    
                    if step == 1:
                        self.current_node_id = result.get("node_id")
                        self.node_map["main"] = self.current_node_id
                        # Save to global map for evaluation phase
                        self._save_global_node(scenario_file.stem, "main", self.current_node_id)
                    
                    if "error" in result:
                        error_msg = result.get('error', 'Unknown')
                        print(f" ❌ Error: {error_msg} ({elapsed:.1f}s)")
                        self._log(f"  ❌ ERROR: {error_msg} ({elapsed:.1f}s)")
                    else:
                        response_preview = result.get("response", "")[:60]
                        print(f" ✅ OK ({elapsed:.1f}s) - Response: {response_preview}...")
                        self._log(f"  ✅ SUCCESS ({elapsed:.1f}s)")
                        # Log FULL response for detailed debugging
                        self._log(f"  Response (FULL):\n{result.get('response', '')}\n")

                
                elif action == "create_subchat":
                    parent = conv.get("parent_node", "main")
                    parent_id = self.node_map.get(parent)
                    
                    print(f"Creating subchat from {parent}...", end="", flush=True)
                    self._log(f"  Creating subchat from {parent} (parent_id: {parent_id})")
                    
                    result = self.create_subchat(parent_id, message)
                    elapsed = time.time() - start_time
                    
                    if "error" not in result:
                        # Track subchat
                        subchat_count = sum(1 for k in self.node_map if k.startswith("subchat_"))
                        subchat_key = f"subchat_{subchat_count + 1}"
                        self.node_map[subchat_key] = result["node_id"]
                        self.current_node_id = result["node_id"]
                        # Save to global map
                        self._save_global_node(scenario_file.stem, subchat_key, result["node_id"])
                        print(f" 🌿 Subchat created: {subchat_key} = {result['node_id'][:8]}... ({elapsed:.1f}s)")
                        self._log(f"  🌿 SUBCHAT CREATED: {subchat_key} = {result['node_id']} ({elapsed:.1f}s)")
                    else:
                        error_msg = result.get('error', 'Unknown')
                        print(f" ❌ Error: {error_msg} ({elapsed:.1f}s)")
                        self._log(f"  ❌ ERROR: {error_msg} ({elapsed:.1f}s)")
                
            except Exception as e:
                elapsed = time.time() - start_time
                print(f" ❌ Exception: {str(e)} ({elapsed:.1f}s)")
                self._log(f"  ❌ EXCEPTION: {str(e)} ({elapsed:.1f}s)")
        
        print(f"\n✅ Scenario Completed: {total_steps} steps")
        print(f"📊 Nodes created: {len(self.node_map)} ({', '.join(self.node_map.keys())})")
        
        self._log(f"\n✅ SCENARIO COMPLETED")
        self._log(f"Total steps: {total_steps}")
        self._log(f"Nodes created: {self.node_map}")
    
    def run_evaluation_scenario(self, scenario_file: Path):
        """Run an evaluation scenario (with tests)."""
        scenario = self.load_scenario(scenario_file)
        
        self.logger.start_scenario(
            scenario["scenario_name"],
            scenario["description"]
        )
        
        total_steps = len(scenario["conversations"])
        
        for conv in scenario["conversations"]:
            step = conv["step"]
            message = conv["message"]
            test_type = conv.get("test_type", "unknown")
            
            if step > 1:
                time.sleep(self.delay)
            
            try:
                # Handle node switching for isolation tests
                if conv.get("action") == "switch_to_node":
                    node_hint = conv.get("node_hint", "")
                    target_node = self._resolve_node_from_hint(node_hint)
                    if not target_node:
                        print(f"⚠️  Could not resolve node from hint: {node_hint}")
                        target_node = self.current_node_id
                else:
                    target_node = self.current_node_id
                
                # 🧪 EVALUATION: Enable RAG for testing retrieval
                result = self.send_message(message, target_node, disable_rag=False)
                
                if "error" in result:
                    self.logger.log_message(step, "main", message, f"ERROR: {result['error']}")
                    continue
                
                response = result.get("response", "")
                
                # Log message
                self.logger.log_message(step, "test", message, response)
                
                # Evaluate if this is a test
                if test_type in ["retrieval", "context_isolation"]:
                    self._evaluate_test(step, conv, response)
            
            except Exception as e:
                print(f"❌ Error in step {step}: {e}")
        
        # End scenario
        self.logger.end_scenario()
    
    def _evaluate_test(self, step: int, conv: Dict, response: str):
        """Evaluate a test using both keyword and AI methods."""
        test_type = conv.get("test_type")
        question = conv["message"]
        expected_info = conv.get("expected_info", "")
        expected_keywords = conv.get("expected_keywords", [])
        forbidden_keywords = conv.get("forbidden_keywords", [])
        
        # Use AI evaluator
        evaluation = self.ai_evaluator.evaluate_response(
            question=question,
            ai_response=response,
            expected_info=expected_info,
            expected_keywords=expected_keywords,
            forbidden_keywords=forbidden_keywords
        )
        
        # Log with dataset logger
        self.logger.validate_test(
            step=step,
            test_type=test_type,
            query=question,
            response=response,
            expected_contains=expected_keywords if evaluation["keyword_pass"] else None,
            should_not_contain=forbidden_keywords if evaluation["found_forbidden"] else None,
            expected_retrieval=[expected_info] if evaluation["ai_pass"] else None
        )
        
        # Override with AI evaluation result
        if self.logger.current_scenario and self.logger.current_scenario["tests"]:
            last_test = self.logger.current_scenario["tests"][-1]
            last_test["passed"] = evaluation["final_result"]
            last_test["ai_evaluation"] = {
                "ai_pass": evaluation["ai_pass"],
                "ai_reason": evaluation["ai_reason"],
                "keyword_pass": evaluation["keyword_pass"]
            }
    
    def _get_target_node(self, node_type: str) -> Optional[str]:
        """Get target node ID from node type."""
        if node_type == "main":
            return self.node_map.get("main")
        elif node_type.startswith("subchat_"):
            return self.node_map.get(node_type)
        return self.current_node_id
    
    def _save_global_node(self, scenario_key: str, node_type: str, node_id: str):
        """Save node mapping for cross-scenario access."""
        key = f"{scenario_key}_{node_type}"
        self.global_node_map[key] = node_id
    
    def _resolve_node_from_hint(self, hint: str) -> Optional[str]:
        """Resolve node ID from human-readable hint."""
        # Map hints to scenario keys
        hint_lower = hint.lower()
        
        mappings = {
            "python programming": "02_python_ambiguity_subchat_1",
            "python snake": "02_python_ambiguity_main",
            "python habitat": "02_python_ambiguity_subchat_2",
            "adhd personal": "04_adhd_support_subchat_1",
            "adhd main": "04_adhd_support_main",
            "italy": "05_travel_stories_subchat_1",
            "japan": "05_travel_stories_main",
            "databases": "08_tech_stack_subchat_1",
            "testing tools": "08_tech_stack_subchat_2",
            "tech main": "08_tech_stack_main",
            "career main": "10_career_goals_main",
            "side projects": "10_career_goals_subchat_2"
        }
        
        for hint_key, global_key in mappings.items():
            if hint_key in hint_lower:
                node_id = self.global_node_map.get(global_key)
                if node_id:
                    return node_id
        
        return None
    
    def run_all_scenarios(self, scenarios_dir: Path, phase: Optional[int] = None):
        """Run all scenarios in two phases."""
        scenario_files = sorted(scenarios_dir.glob("*.json"))
        
        # Separate by type
        # Population: 01, 02 (context isolation scenarios)
        # Evaluation: 04 (memory retrieval tests)
        population_scenarios = [f for f in scenario_files if f.stem[:2] in ["01", "02"]]
        evaluation_scenarios = [f for f in scenario_files if f.stem[:2] == "04"]
        
        print(f"\n{'='*80}")
        print(f"🚀 DATASET EXECUTION - Two-Phase Approach")
        print(f"{'='*80}")
        print(f"📦 Population scenarios: {len(population_scenarios)}")
        print(f"🧪 Evaluation scenarios: {len(evaluation_scenarios)}")
        print(f"🌐 API: {self.base_url}")
        print(f"⏱️  Delay: {self.delay}s between requests")
        print(f"{'='*80}\n")
        
        # Test API
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            print("✅ API connection successful\n")
        except:
            print("❌ Cannot connect to API!")
            return
        
        # Phase 1: Population
        if phase is None or phase == 1:
            print(f"\n{'🎯'*40}")
            print(f"📦 PHASE 1: POPULATION (Building Vector Store)")
            print(f"{'🎯'*40}\n")
            
            for i, scenario_file in enumerate(population_scenarios, 1):
                try:
                    self.run_population_scenario(scenario_file, i, len(population_scenarios))
                except Exception as e:
                    print(f"\n❌ Fatal error: {e}")
            
            print(f"\n✅ Phase 1 Complete! Vector store populated with {len(population_scenarios)} scenarios")
            print(f"💾 Total nodes created: {len(self.global_node_map)}")
        
        # Phase 2: Evaluation
        if phase is None or phase == 2:
            print(f"\n{'🎯'*40}")
            print(f"🧪 PHASE 2: EVALUATION (Testing RAG System)")
            print(f"{'🎯'*40}\n")
            
            for scenario_file in evaluation_scenarios:
                try:
                    self.run_evaluation_scenario(scenario_file)
                except Exception as e:
                    print(f"\n❌ Fatal error: {e}")
            
            # Generate reports
            print(f"\n{'='*80}")
            print(f"📊 Generating Reports...")
            print(f"{'='*80}\n")
            
            self.logger.generate_final_report()
            print("\n" + self.ai_evaluator.generate_summary())


def main():
    parser = argparse.ArgumentParser(description="Run dataset testing with two-phase approach")
    parser.add_argument("--phase", type=int, choices=[1, 2], help="Run specific phase (1=population, 2=evaluation)")
    parser.add_argument("--skip-delay", action="store_true", help="Skip delays between requests")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    delay = 0.0 if args.skip_delay else 1.0
    runner = DatasetRunner(base_url=args.base_url, delay=delay)
    
    scenarios_dir = Path(__file__).parent / "scenarios"
    runner.run_all_scenarios(scenarios_dir, phase=args.phase)


if __name__ == "__main__":
    main()
