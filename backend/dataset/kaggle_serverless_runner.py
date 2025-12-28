#!/usr/bin/env python3
"""
Kaggle SERVERLESS Test Runner
Uses DIRECT Python imports instead of HTTP requests
This allows the test to run in the same process as the loaded vLLM model
"""

import os
import sys
import json
import time
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Handle exec() case where __file__ is not defined
try:
    __file__
except NameError:
    __file__ = os.path.join(os.getcwd(), "dataset", "kaggle_serverless_runner.py")

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))  # backend/
sys.path.insert(0, str(Path(__file__).parent))  # dataset/

from context_classifier import ContextClassifier
from src.services.simple_llm import SimpleChat
from src.utils.debug_logger import set_log_directory


class ServerlessTestRunner:
    """
    Run tests using direct Python imports - NO SERVER NEEDED
    This runs in the same process as the vLLM model
    """
    
    def __init__(self, repo_branch: str = "kaggle-run"):
        self.repo_branch = repo_branch
        
        # Use SimpleChat core class (same as frontend/server)
        # This properly manages nodes via ChatGraphManager and Forest
        self.chat = SimpleChat(enable_rag=True)
        
        # Setup directories - ALL logs go to dataset/logs/
        # Always use path relative to this file (works both locally and on Kaggle)
        self.base_logs_dir = Path(__file__).parent / "logs"  # dataset/logs/
        
        self.base_logs_dir.mkdir(parents=True, exist_ok=True)
        self.main_log_file = self.base_logs_dir / "test_execution.log"
        
        self.current_buffer_size = None
        self.buffer_log_dir: Optional[Path] = None
        self.baseline_log_file: Optional[Path] = None
        self.system_log_file: Optional[Path] = None
        
        # Git configuration
        self.repo_root = Path(__file__).parent.parent.parent
        
        # Initialize classifier with logging callback (after log methods are defined)
        self.classifier = ContextClassifier(log_callback=self.log_judge)

    def setup_buffer_logs(self, buffer_size: int):
        """Setup buffer-specific log directory with ALL logs in one place"""
        self.current_buffer_size = buffer_size
        
        # All logs go to buffer_log_dir (e.g., dataset/logs/buffer_40/)
        self.buffer_log_dir = self.base_logs_dir / f"buffer_{buffer_size}"
        self.buffer_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Redirect DebugLogger to buffer-specific directory
        # This makes LocalBuffer and VectorIndex log detailed content here
        set_log_directory(str(self.buffer_log_dir))
        
        self.baseline_log_file = self.buffer_log_dir / "baseline_test.log"
        self.system_log_file = self.buffer_log_dir / "system_test.log"
        
        # Initialize test log files
        for log_file in [self.baseline_log_file, self.system_log_file]:
            with open(log_file, 'w') as f:
                f.write(f"{'='*80}\n")
                f.write(f"{'BASELINE' if 'baseline' in log_file.name else 'SYSTEM'} TEST LOG (Buffer Size: {buffer_size})\n")
                f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
        
        # Initialize component log files (summary + full pairs)
        components = ["BUFFER", "VECTOR_STORE", "RETRIEVAL", "COT_THINKING", "JUDGE"]
        for component in components:
            # Summary log
            summary_file = self.buffer_log_dir / f"{component}.log"
            with open(summary_file, 'w') as f:
                f.write(f"{'='*80}\n")
                f.write(f"{component} LOG - SUMMARY (Buffer Size: {buffer_size})\n")
                f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
            
            # Full/detailed log
            full_file = self.buffer_log_dir / f"{component}_full.log"
            with open(full_file, 'w') as f:
                f.write(f"{'='*80}\n")
                f.write(f"{component} LOG - DETAILED (Buffer Size: {buffer_size})\n")
                f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
        
        self.log(f"📁 Created buffer-specific log directory: {self.buffer_log_dir}")

    def log(self, message: str, level: str = "INFO", test_type: Optional[str] = None):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        
        if test_type == "baseline" and self.baseline_log_file:
            with open(self.baseline_log_file, 'a') as f:
                f.write(log_msg + "\n")
        elif test_type == "system" and self.system_log_file:
            with open(self.system_log_file, 'a') as f:
                f.write(log_msg + "\n")
        else:
            with open(self.main_log_file, 'a') as f:
                f.write(log_msg + "\n")

    def log_component(self, component: str, message: str, full: bool = False):
        """
        Log to component-specific log files in buffer directory.
        
        Args:
            component: One of 'BUFFER', 'VECTOR_STORE', 'RETRIEVAL', 'COT_THINKING'
            message: The message to log
            full: If True, log to {component}_full.log only (detailed info).
                  If False, log to both {component}.log (summary) and {component}_full.log (detailed).
        """
        if self.buffer_log_dir is None:
            return  # Buffer logs not set up yet
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        
        # Always log to full/detailed log
        full_log_file = self.buffer_log_dir / f"{component}_full.log"
        with open(full_log_file, 'a') as f:
            f.write(log_msg + "\n")
        
        # If not full-only, also log to summary log
        if not full:
            summary_log_file = self.buffer_log_dir / f"{component}.log"
            with open(summary_log_file, 'a') as f:
                f.write(log_msg + "\n")

    def log_buffer(self, message: str, full: bool = False):
        """Log buffer-related events"""
        self.log_component("BUFFER", message, full)

    def log_vector_store(self, message: str, full: bool = False):
        """Log vector store events"""
        self.log_component("VECTOR_STORE", message, full)

    def log_retrieval(self, message: str, full: bool = False):
        """Log retrieval events"""
        self.log_component("RETRIEVAL", message, full)

    def log_cot_thinking(self, message: str, full: bool = False):
        """Log chain-of-thought thinking events"""
        self.log_component("COT_THINKING", message, full)
    
    def log_judge(self, message: str, full: bool = False):
        """Log LLM judge decisions to buffer-specific JUDGE.log"""
        self.log_component("JUDGE", message, full)

    def clear_state(self):
        """Clear all nodes in memory for fresh test"""
        # Clear nodes from ChatGraphManager and Forest (using core classes)
        self.chat.chat_manager.node_map.clear()
        self.chat.forest.trees_map.clear()
        self.chat.chat_manager.active_node_id = None
        self.chat.forest.active_tree_id = None
        
        # Clear ChromaDB if it exists
        try:
            chroma_db_path = Path(__file__).parent.parent / "chroma_db"
            if chroma_db_path.exists():
                shutil.rmtree(chroma_db_path)
                self.log("🗑️  Cleared ChromaDB", "INFO")
        except Exception as e:
            self.log(f"⚠️  ChromaDB clear warning: {e}", "WARN")
    
    def create_conversation(self, title: str, buffer_size: int = 15) -> Optional[str]:
        """Create a new root conversation using SimpleChat core class"""
        try:
            # Use SimpleChat.start_new_conversation() - same as frontend/server
            # This uses Forest.create_tree() which properly sets up TreeNode with
            # vector_index and llm_client from ChatGraphManager
            node = self.chat.start_new_conversation(title, buffer_size=buffer_size)
            node_id = node.node_id
            
            # Log buffer creation
            self.log_buffer(f"🌳 Created root conversation node (id={node_id}, buffer_size={buffer_size})")
            self.log_buffer(f"   Title: {title}", full=True)
            if self.chat.llm.vector_index:
                self.log_vector_store(f"📊 Vector index attached to node {node_id}")
            
            return node_id
        except Exception as e:
            self.log(f"❌ Failed to create conversation: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return None
    
    def create_subchat(self, parent_id: str, title: str, selected_text: Optional[str] = None, buffer_size: int = 15) -> Optional[str]:
        """Create a subchat under a parent node using ChatGraphManager core class
        
        This uses ChatGraphManager.create_node() which:
        1. Creates TreeNode with proper parent reference
        2. COPIES PARENT BUFFER MESSAGES to child (lines 37-41 in chat_manager.py)
        3. Inherits parent's rolling summary
        4. Sets follow-up context properly via set_follow_up_context()
        """
        try:
            # Verify parent exists in ChatGraphManager
            parent = self.chat.chat_manager.node_map.get(parent_id)
            if not parent:
                self.log(f"❌ Parent node not found: {parent_id}", "ERROR")
                return None
            
            # Use ChatGraphManager.create_node() - same as endpoints.py (line 134)
            # This AUTOMATICALLY copies parent buffer messages to child!
            child = self.chat.chat_manager.create_node(
                title=title,
                parent_id=parent_id,
                selected_text=selected_text,
                context_type="follow_up",
                buffer_size=buffer_size
            )
            node_id = child.node_id
            
            # Log subchat creation
            self.log_buffer(f"🌿 Created subchat node (id={node_id}, parent={parent_id}, buffer_size={buffer_size})")
            self.log_buffer(f"   Title: {title}", full=True)
            
            # Log inherited context (parent messages are auto-copied by ChatGraphManager)
            parent_msg_count = len(parent.buffer.get_recent())
            self.log_buffer(f"   ✅ Inherited {parent_msg_count} messages from parent buffer", full=True)
            if selected_text:
                self.log_buffer(f"   Follow-up context: {selected_text}", full=True)
            if parent.buffer.summary:
                self.log_buffer(f"   ✅ Inherited parent summary ({len(parent.buffer.summary)} chars)", full=True)
            
            return node_id
        except Exception as e:
            self.log(f"❌ Failed to create subchat: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return None
    
    def send_message(self, node_id: str, message: str) -> Optional[Dict]:
        """Send message and get response using SimpleChat core class
        
        Uses SimpleChat.send_message() which:
        1. Adds user message to buffer
        2. Calls llm.generate_response() with proper context (including summary)
        3. Adds assistant response to buffer
        4. Auto-generates title if needed
        """
        try:
            # Get node from ChatGraphManager
            node = self.chat.chat_manager.node_map.get(node_id)
            if not node:
                self.log(f"❌ Node not found: {node_id}", "ERROR")
                return None
            
            start_time = time.time()
            
            # Switch to target node (required before send_message)
            self.chat.chat_manager.switch_node(node_id)
            
            # Log before sending
            self.log_buffer(f"📥 Sending message to node={node_id}")
            self.log_buffer(f"   Message: {message}", full=True)
            
            # Use SimpleChat.send_message() - same as endpoints.py
            # This handles: add user msg → generate response → add assistant msg
            response_text = self.chat.send_message(message)
            
            latency = time.time() - start_time
            
            # Log after response
            buffer_size = len(node.buffer.turns)
            self.log_buffer(f"📤 Response received (node={node_id}, buffer_size={buffer_size})")
            self.log_cot_thinking(f"🤖 Generated response for node={node_id}")
            self.log_cot_thinking(f"   Response: {response_text}", full=True)
            
            # Check if buffer triggered summarization
            if hasattr(node.buffer, 'messages_processed_count'):
                self.log_vector_store(f"📦 Messages processed: {node.buffer.messages_processed_count}")
                self.log_vector_store(f"   Node: {node_id}, Buffer max: {node.buffer.max_turns}", full=True)
            
            # Get usage from LLM client
            usage = self.chat.llm.get_last_usage()
            
            return {
                "response": response_text,
                "latency": latency,
                "usage": usage
            }
        except Exception as e:
            self.log(f"❌ Failed to send message: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return None

    def load_scenario(self, scenario_file: str) -> Optional[Dict]:
        """Load JSON scenario"""
        scenario_path = Path(__file__).parent / "scenarios" / scenario_file
        
        if not scenario_path.exists():
            self.log(f"❌ Scenario not found: {scenario_file}", "ERROR")
            return None
        
        if scenario_path.stat().st_size == 0:
            self.log(f"⚠️  Skipping empty file: {scenario_file}", "WARNING")
            return None
        
        try:
            with open(scenario_path, 'r') as f:
                scenario = json.load(f)
            
            # Extract unique topics from context field
            scenario['_extracted_topics'] = self._extract_topics(scenario)
            return scenario
        except json.JSONDecodeError as e:
            self.log(f"❌ Invalid JSON in {scenario_file}: {e}", "ERROR")
            return None

    def _extract_topics(self, scenario: Dict) -> List[str]:
        """
        Extract unique topic identifiers from the scenario's conversations.
        
        Topics are extracted from the 'context' field, normalized to base topic names.
        E.g., "by_length_step1", "by_length_step2" -> "by_length"
             "odd_count_intro" -> "odd_count"
             "by_length_final" -> "by_length"
             "personas_roleplay" -> "personas_roleplay"
        """
        topics = set()
        
        for step_data in scenario.get("conversations", []):
            context = step_data.get("context", "")
            if not context or context in ["intro", "step_1"]:
                continue
            
            # Extract base topic by removing common suffixes
            # Pattern: topic_name_suffix (e.g., by_length_step1, odd_count_intro, histogram_final)
            base_topic = context
            
            # Remove step/intro/final suffixes to get base topic
            for suffix_pattern in ["_step\\d+", "_intro", "_final", "_\\d+$"]:
                import re
                base_topic = re.sub(suffix_pattern, "", base_topic)
            
            # Clean up any trailing underscores
            base_topic = base_topic.rstrip("_")
            
            if base_topic and base_topic not in ["step", "intro"]:
                topics.add(base_topic)
        
        topic_list = sorted(list(topics))
        self.log(f"📋 Extracted {len(topic_list)} unique topics: {topic_list}", "INFO")
        return topic_list

    def _normalize_context_to_topic(self, context: str) -> str:
        """Normalize a context string to its base topic name."""
        if not context or context in ["intro", "step_1"]:
            return "general"
        
        base_topic = context
        for suffix_pattern in ["_step\\d+", "_intro", "_final", "_\\d+$"]:
            import re
            base_topic = re.sub(suffix_pattern, "", base_topic)
        
        return base_topic.rstrip("_") or "general"

    def _extract_topic_regex(self, response: str, valid_topics: List[str]) -> Dict:
        """Extract topic from response using pure regex (all datasets use 'topic_name:' prefix)."""
        import re
        
        if not response or not valid_topics:
            return {"detected_topic": "unknown", "method": "empty_input"}
        
        # All datasets use strict format: "topic_name: actual response"
        # Extract the prefix before the first colon
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:', response.strip())
        
        if not match:
            return {"detected_topic": "unknown", "method": "no_prefix_found"}
        
        extracted = match.group(1).strip().lower()
        
        # Check if extracted topic is in valid topics list
        for valid_topic in valid_topics:
            if extracted == valid_topic.lower():
                return {"detected_topic": valid_topic, "method": "regex_exact_match"}
        
        return {"detected_topic": "unknown", "method": "prefix_not_in_valid_topics"}

    def run_baseline_test(self, scenario: Dict, buffer_size: int = 15) -> List[Dict]:
        """
        BASELINE test: ONE conversation for ALL contexts (no subchats)
        Simulates traditional chatbots where all topics are mixed
        """
        self.log("="*80, "INFO", "baseline")
        self.log(f"🔵 BASELINE TEST: {scenario['scenario_name']} (buffer_size={buffer_size})", "INFO", "baseline")
        self.log("   Strategy: Single conversation for all topics (traditional chatbot)", "INFO", "baseline")
        self.log("="*80, "INFO", "baseline")
        
        results = []
        
        # Get available topics for this scenario
        available_topics = scenario.get('_extracted_topics', [])
        scenario_name = scenario.get('scenario_name', 'Unknown')
        
        # Create ONE conversation for all contexts
        main_node_id = self.create_conversation("Baseline - All Topics", buffer_size=buffer_size)
        if not main_node_id:
            self.log("❌ Failed to create baseline conversation", "ERROR", "baseline")
            return results
        
        self.log(f"  📝 Created single conversation for all topics", "INFO", "baseline")
        self.log(f"  📋 Available topics for detection: {available_topics}", "INFO", "baseline")
        
        tp_count = tn_count = fp_count = fn_count = 0
        
        for step_data in scenario["conversations"]:
            step = step_data["step"]
            context = step_data["context"]
            message = step_data["message"]
            expected = step_data["expected"]
            
            # Get expected topic from context
            expected_topic = self._normalize_context_to_topic(context)
            
            self.log(f"\n[Step {step}] Context: {context} (Topic: {expected_topic})", "INFO", "baseline")
            self.log(f"  💬 User: {message}", "INFO", "baseline")
            
            response = self.send_message(main_node_id, message)
            
            if not response:
                self.log("  ❌ No response received", "ERROR", "baseline")
                continue
            
            ai_message = response.get("response", "")
            
            if not ai_message:
                self.log("  ❌ Empty AI response", "ERROR", "baseline")
                continue
            
            self.log(f"  🤖 AI Response:", "INFO", "baseline")
            self.log(f"     {ai_message}", "INFO", "baseline")
            
            # Extract topic using pure regex (all datasets use 'topic_name:' prefix)
            topic_detection = self._extract_topic_regex(ai_message, available_topics)
            detected_topic = topic_detection["detected_topic"]
            
            # Determine if topic detection was correct
            is_correct_topic = (expected_topic == detected_topic)
            
            # Log to JUDGE
            judge_status = "✓ CORRECT" if is_correct_topic else "✗ INCORRECT"
            self.log_judge(f"[Step {step}] Expected: {expected_topic} | Detected: {detected_topic} | {judge_status}")
            
            # Log to COT_THINKING for reasoning
            self.log_cot_thinking(f"🧠 Topic detection for step {step}: {judge_status}")
            self.log_cot_thinking(f"   Expected: {expected_topic}, Detected: {detected_topic}, Method: {topic_detection['method']}", full=True)
            
            if is_correct_topic:
                self.log(f"  ✅ Topic Match: {detected_topic} (regex)", "INFO", "baseline")
            else:
                self.log(f"  ❌ Topic Mismatch: Expected {expected_topic}, Got {detected_topic} (regex)", "WARN", "baseline")
            
            results.append({
                "step": step,
                "context": context,
                "expected_topic": expected_topic,
                "detected_topic": detected_topic,
                "is_correct_topic": is_correct_topic,
                "topic_detection_method": topic_detection.get("method", "unknown"),
                "message": message,
                "response": ai_message,
                "input_tokens": response.get("usage", {}).get("prompt_tokens", 0),
                "output_tokens": response.get("usage", {}).get("completion_tokens", 0),
                "total_tokens": response.get("usage", {}).get("total_tokens", 0),
                "latency": response.get("latency", 0),
                "rag_used": False,
                "scenario_name": scenario_name
            })
            
            time.sleep(0.3)
        
        self.log("\n" + "="*80, "INFO", "baseline")
        self.log("📊 BASELINE TEST SUMMARY", "INFO", "baseline")
        self.log(f"   Total Steps: {len(results)}", "INFO", "baseline")
        self.log(f"   ✅ Correct (TP+TN): {tp_count + tn_count}", "INFO", "baseline")
        self.log(f"   ❌ Incorrect (FP+FN): {fp_count + fn_count}", "INFO", "baseline")
        if results:
            self.log(f"   Accuracy: {((tp_count + tn_count) / len(results) * 100):.1f}%", "INFO", "baseline")
        self.log("="*80, "INFO", "baseline")
        
        return results

    def run_system_test(self, scenario: Dict, buffer_size: int = 15) -> List[Dict]:
        """
        SYSTEM test: Main chat + subchats architecture (OUR SYSTEM)
        Uses Subchat Trees for context isolation
        """
        self.log("="*80, "INFO", "system")
        self.log(f"🟢 SYSTEM TEST: {scenario['scenario_name']} (buffer_size={buffer_size})", "INFO", "system")
        self.log("   Strategy: Main chat + subchats for topic isolation", "INFO", "system")
        self.log("="*80, "INFO", "system")
        
        results = []
        node_map = {}
        
        # Get available topics for this scenario
        available_topics = scenario.get('_extracted_topics', [])
        scenario_name = scenario.get('scenario_name', 'Unknown')
        
        tp_count = tn_count = fp_count = fn_count = 0
        
        # Create main conversation
        main_id = self.create_conversation("System Test - Main", buffer_size=buffer_size)
        if not main_id:
            self.log("❌ Failed to create main conversation", "ERROR", "system")
            return results
        
        node_map["main"] = main_id
        self.log(f"  📝 Created main conversation", "INFO", "system")
        self.log(f"  📋 Available topics for detection: {available_topics}", "INFO", "system")
        
        for step_data in scenario["conversations"]:
            step = step_data["step"]
            context = step_data["context"]
            message = step_data["message"]
            expected = step_data["expected"]
            node_type = step_data.get("node_type", "main")
            action = step_data.get("action", "")
            
            # Get expected topic from context
            expected_topic = self._normalize_context_to_topic(context)
            
            # Handle subchat creation
            if action == "create_subchat":
                subchat_title = step_data.get("subchat_title", f"{context} discussion")
                selected_text = step_data.get("selected_text")
                parent_node_type = step_data.get("parent_node_type", "main")
                parent_id = node_map.get(parent_node_type, main_id)
                
                subchat_id = self.create_subchat(parent_id, subchat_title, selected_text, buffer_size=buffer_size)
                
                if subchat_id:
                    node_map[node_type] = subchat_id
                    if selected_text:
                        self.log(f"  🌿 Created follow-up subchat: {node_type} under {parent_node_type} (selected: '{selected_text}')", "INFO", "system")
                    else:
                        self.log(f"  🌿 Created subchat: {node_type} under {parent_node_type}", "INFO", "system")
                else:
                    self.log(f"  ❌ Failed to create subchat: {node_type}", "ERROR", "system")
            
            target_node = node_map.get(node_type, main_id)
            
            self.log(f"\n[Step {step}] Context: {context} (Topic: {expected_topic}) | Node: {node_type}", "INFO", "system")
            self.log(f"  💬 User: {message}", "INFO", "system")
            
            response = self.send_message(target_node, message)
            
            if not response:
                self.log("  ❌ No response received", "ERROR", "system")
                continue
            
            ai_message = response.get("response", "")
            
            if not ai_message:
                self.log("  ❌ Empty AI response", "ERROR", "system")
                continue
            
            self.log(f"  🤖 AI Response:", "INFO", "system")
            self.log(f"     {ai_message}", "INFO", "system")
            
            # Extract topic using pure regex (all datasets use 'topic_name:' prefix)
            topic_detection = self._extract_topic_regex(ai_message, available_topics)
            detected_topic = topic_detection["detected_topic"]
            
            # Determine if topic detection was correct
            is_correct_topic = (expected_topic == detected_topic)
            
            # Log to JUDGE
            judge_status = "✓ CORRECT" if is_correct_topic else "✗ INCORRECT"
            self.log_judge(f"[Step {step}] Expected: {expected_topic} | Detected: {detected_topic} | {judge_status}")
            
            # Log to COT_THINKING for reasoning
            self.log_cot_thinking(f"🧠 System test topic detection for step {step}: {judge_status}")
            self.log_cot_thinking(f"   Node: {node_type}, Expected: {expected_topic}, Detected: {detected_topic}, Method: {topic_detection['method']}", full=True)
            
            if is_correct_topic:
                self.log(f"  ✅ Topic Match: {detected_topic} (regex)", "INFO", "system")
            else:
                self.log(f"  ❌ Topic Mismatch: Expected {expected_topic}, Got {detected_topic} (regex)", "WARN", "system")
            
            results.append({
                "step": step,
                "context": context,
                "expected_topic": expected_topic,
                "detected_topic": detected_topic,
                "is_correct_topic": is_correct_topic,
                "topic_detection_method": topic_detection.get("method", "unknown"),
                "node_type": node_type,
                "message": message,
                "response": ai_message,
                "input_tokens": response.get("usage", {}).get("prompt_tokens", 0),
                "output_tokens": response.get("usage", {}).get("completion_tokens", 0),
                "total_tokens": response.get("usage", {}).get("total_tokens", 0),
                "latency": response.get("latency", 0),
                "rag_used": False,
                "scenario_name": scenario_name
            })
            
            time.sleep(0.3)
        
        self.log("\n" + "="*80, "INFO", "system")
        self.log("📊 SYSTEM TEST SUMMARY", "INFO", "system")
        self.log(f"   Total Steps: {len(results)}", "INFO", "system")
        self.log(f"   ✅ Correct (TP+TN): {tp_count + tn_count}", "INFO", "system")
        self.log(f"   ❌ Incorrect (FP+FN): {fp_count + fn_count}", "INFO", "system")
        if results:
            self.log(f"   Accuracy: {((tp_count + tn_count) / len(results) * 100):.1f}%", "INFO", "system")
        self.log("="*80, "INFO", "system")
        
        return results

    def calculate_metrics(self, baseline_results: List[Dict], system_results: List[Dict]) -> Dict:
        """Calculate all metrics for tables including per-topic confusion matrix"""
        
        def calc_topic_confusion_matrix(results):
            """
            Build a per-topic confusion matrix from results.
            
            For each topic:
            - TP: expected_topic == detected_topic == topic
            - FP: expected_topic != topic but detected_topic == topic (false alarm)
            - FN: expected_topic == topic but detected_topic != topic (miss)
            
            Returns per-topic metrics and aggregated metrics.
            """
            # Get all unique topics from results
            all_topics = set()
            for r in results:
                exp = r.get("expected_topic", "general")
                det = r.get("detected_topic", "unknown")
                if exp and exp != "general":
                    all_topics.add(exp)
                if det and det not in ["unknown", "general"]:
                    all_topics.add(det)
            
            all_topics = sorted(list(all_topics))
            
            # Initialize per-topic counters
            topic_metrics = {}
            for topic in all_topics:
                topic_metrics[topic] = {"tp": 0, "fp": 0, "fn": 0, "support": 0}
            
            # Build confusion matrix
            for r in results:
                expected = r.get("expected_topic", "general")
                detected = r.get("detected_topic", "unknown")
                
                if expected in topic_metrics:
                    topic_metrics[expected]["support"] += 1
                    
                    if detected == expected:
                        # True positive for this topic
                        topic_metrics[expected]["tp"] += 1
                    else:
                        # False negative for expected topic (we missed it)
                        topic_metrics[expected]["fn"] += 1
                        
                        # False positive for detected topic (if it's a valid topic)
                        if detected in topic_metrics:
                            topic_metrics[detected]["fp"] += 1
            
            # Calculate per-topic precision, recall, F1
            for topic in topic_metrics:
                tm = topic_metrics[topic]
                precision = tm["tp"] / (tm["tp"] + tm["fp"]) if (tm["tp"] + tm["fp"]) > 0 else 0
                recall = tm["tp"] / (tm["tp"] + tm["fn"]) if (tm["tp"] + tm["fn"]) > 0 else 0
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                tm["precision"] = precision * 100
                tm["recall"] = recall * 100
                tm["f1"] = f1 * 100
            
            # Calculate macro and weighted averages
            if topic_metrics:
                macro_precision = sum(tm["precision"] for tm in topic_metrics.values()) / len(topic_metrics)
                macro_recall = sum(tm["recall"] for tm in topic_metrics.values()) / len(topic_metrics)
                macro_f1 = sum(tm["f1"] for tm in topic_metrics.values()) / len(topic_metrics)
                
                total_support = sum(tm["support"] for tm in topic_metrics.values())
                if total_support > 0:
                    weighted_precision = sum(tm["precision"] * tm["support"] for tm in topic_metrics.values()) / total_support
                    weighted_recall = sum(tm["recall"] * tm["support"] for tm in topic_metrics.values()) / total_support
                    weighted_f1 = sum(tm["f1"] * tm["support"] for tm in topic_metrics.values()) / total_support
                else:
                    weighted_precision = weighted_recall = weighted_f1 = 0
            else:
                macro_precision = macro_recall = macro_f1 = 0
                weighted_precision = weighted_recall = weighted_f1 = 0
            
            return {
                "per_topic": topic_metrics,
                "macro": {
                    "precision": macro_precision,
                    "recall": macro_recall,
                    "f1": macro_f1
                },
                "weighted": {
                    "precision": weighted_precision,
                    "recall": weighted_recall,
                    "f1": weighted_f1
                },
                "topics": all_topics
            }
        
        def calc_isolation_metrics(results):
            """Calculate basic isolation metrics (accuracy, pollution_rate) + topic-based precision/recall/F1"""
            # Calculate accuracy from is_correct_topic field (regex-based topic matching)
            correct = sum(1 for r in results if r.get("is_correct_topic", False))
            total = len(results)
            accuracy = (correct / total * 100) if total > 0 else 0
            pollution_rate = ((total - correct) / total * 100) if total > 0 else 0
            
            # NEW: Calculate topic-based confusion matrix metrics
            topic_cm = calc_topic_confusion_matrix(results)
            
            return {
                # Topic-based metrics (proper precision/recall/F1)
                "precision": topic_cm["weighted"]["precision"],
                "recall": topic_cm["weighted"]["recall"],
                "f1": topic_cm["weighted"]["f1"],
                "macro_precision": topic_cm["macro"]["precision"],
                "macro_recall": topic_cm["macro"]["recall"],
                "macro_f1": topic_cm["macro"]["f1"],
                # Legacy metrics (simplified - accuracy based on regex topic matching)
                "accuracy": accuracy,
                "pollution_rate": pollution_rate,
                "tp": correct, "tn": 0, "fp": total - correct, "fn": 0,
                # Per-topic breakdown
                "per_topic_metrics": topic_cm["per_topic"],
                "topics": topic_cm["topics"]
            }
        
        def calc_performance_metrics(results, isolation_metrics):
            """Calculate performance metrics including tokens, latency, and costs"""
            if not results:
                return {
                    "avg_input_tokens": 0,
                    "avg_output_tokens": 0,
                    "avg_total_tokens": 0,
                    "avg_latency": 0,
                    "token_compression_rate": 0,
                    "tokens_per_correct_answer": 0,
                    "cost_per_query": 0,
                    "cost_per_1m_queries": 0
                }
            
            # Calculate averages
            avg_input = sum(r.get("input_tokens", 0) for r in results) / len(results)
            avg_output = sum(r.get("output_tokens", 0) for r in results) / len(results)
            avg_total = avg_input + avg_output
            avg_latency = sum(r["latency"] for r in results) / len(results)
            
            # Calculate tokens per correct answer
            correct_count = sum(1 for r in results if r.get("is_correct_topic", False))
            total_tokens = sum(r.get("total_tokens", 0) for r in results)
            tokens_per_correct = (total_tokens / correct_count) if correct_count > 0 else 0
            
            # Cost calculation (Groq pricing: input $0.05/1M, output $0.08/1M tokens)
            input_cost = (avg_input / 1_000_000) * 0.05
            output_cost = (avg_output / 1_000_000) * 0.08
            cost_per_query = input_cost + output_cost
            cost_per_1m = cost_per_query * 1_000_000
            
            return {
                "avg_input_tokens": avg_input,
                "avg_output_tokens": avg_output,
                "avg_total_tokens": avg_total,
                "avg_latency": avg_latency,
                "token_compression_rate": 0,  # Will be calculated as improvement
                "tokens_per_correct_answer": tokens_per_correct,
                "cost_per_query": cost_per_query,
                "cost_per_1m_queries": cost_per_1m
            }
        
        baseline_isolation = calc_isolation_metrics(baseline_results)
        system_isolation = calc_isolation_metrics(system_results)
        
        baseline_performance = calc_performance_metrics(baseline_results, baseline_isolation)
        system_performance = calc_performance_metrics(system_results, system_isolation)
        
        def calc_improvement(baseline, system):
            if baseline == 0:
                return 0 if system == 0 else float('inf')
            return ((system - baseline) / baseline) * 100
        
        return {
            "table_1": {
                "baseline": baseline_isolation,
                "system": system_isolation,
                "improvements": {
                    k: calc_improvement(baseline_isolation.get(k, 0), system_isolation.get(k, 0))
                    for k in ["precision", "recall", "f1", "accuracy", "pollution_rate", "macro_precision", "macro_recall", "macro_f1"]
                }
            },
            "table_3": {
                "baseline": baseline_performance,
                "system": system_performance,
                "improvements": {
                    k: calc_improvement(baseline_performance.get(k, 0), system_performance.get(k, 0))
                    for k in baseline_performance.keys()
                }
            }
        }

    def generate_table(self, metrics: Dict):
        """Generate markdown tables in buffer-specific folder"""
        buffer_dir = self.base_logs_dir / "tables" / f"buffer_{self.current_buffer_size}"
        buffer_dir.mkdir(parents=True, exist_ok=True)
        
        table1 = metrics["table_1"]
        with open(buffer_dir / "TABLE_1_CONTEXT_ISOLATION.md", 'w') as f:
            f.write(f"# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: {self.current_buffer_size})\n\n")
            f.write("## Weighted Average Metrics (Per-Topic Confusion Matrix)\n\n")
            f.write("| Metric | Baseline System | Our System | Improvement |\n")
            f.write("|--------|----------------|------------|-------------|\n")
            
            for metric in ["precision", "recall", "f1", "accuracy", "pollution_rate"]:
                baseline_val = table1["baseline"].get(metric, 0)
                system_val = table1["system"].get(metric, 0)
                improvement = table1["improvements"].get(metric, 0)
                # Handle inf improvement gracefully
                if isinstance(improvement, float) and improvement == float('inf'):
                    imp_str = "**∞**"
                else:
                    imp_str = f"**{improvement:+.1f}%**"
                f.write(f"| **{metric.replace('_', ' ').title()}** | ")
                f.write(f"{baseline_val:.1f}% | {system_val:.1f}% | ")
                f.write(f"{imp_str} |\n")
            
            f.write(f"\n## Macro Average Metrics\n\n")
            f.write("| Metric | Baseline System | Our System | Improvement |\n")
            f.write("|--------|----------------|------------|-------------|\n")
            
            for metric in ["macro_precision", "macro_recall", "macro_f1"]:
                baseline_val = table1["baseline"].get(metric, 0)
                system_val = table1["system"].get(metric, 0)
                improvement = table1["improvements"].get(metric, 0)
                if isinstance(improvement, float) and improvement == float('inf'):
                    imp_str = "**∞**"
                else:
                    imp_str = f"**{improvement:+.1f}%**"
                display_name = metric.replace('_', ' ').title().replace("Macro ", "Macro ")
                f.write(f"| **{display_name}** | ")
                f.write(f"{baseline_val:.1f}% | {system_val:.1f}% | ")
                f.write(f"{imp_str} |\n")
            
            # Per-topic breakdown
            f.write(f"\n## Per-Topic Breakdown\n\n")
            
            for system_type, label in [("baseline", "Baseline"), ("system", "Our System")]:
                per_topic = table1[system_type].get("per_topic_metrics", {})
                if per_topic:
                    f.write(f"\n### {label} - Per-Topic Metrics\n\n")
                    f.write("| Topic | Precision | Recall | F1 | TP | FP | FN | Support |\n")
                    f.write("|-------|-----------|--------|----|----|----|----|--------|\n")
                    
                    for topic, tm in sorted(per_topic.items()):
                        f.write(f"| {topic} | {tm['precision']:.1f}% | {tm['recall']:.1f}% | {tm['f1']:.1f}% | ")
                        f.write(f"{tm['tp']} | {tm['fp']} | {tm['fn']} | {tm['support']} |\n")
            
            f.write(f"\n## Legacy Raw Counts (LLM Judge TP/FN)\n")
            f.write(f"- Baseline: TP={table1['baseline']['tp']}, TN={table1['baseline']['tn']}, FP={table1['baseline']['fp']}, FN={table1['baseline']['fn']}\n")
            f.write(f"- System: TP={table1['system']['tp']}, TN={table1['system']['tn']}, FP={table1['system']['fp']}, FN={table1['system']['fn']}\n")
        
        self.log(f"✅ Generated TABLE_1_CONTEXT_ISOLATION.md", "INFO")
        
        table3 = metrics["table_3"]
        with open(buffer_dir / "TABLE_3_SYSTEM_PERFORMANCE.md", 'w') as f:
            f.write(f"# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: {self.current_buffer_size})\n\n")
            f.write("| Metric | Baseline System | Our System | Improvement |\n")
            f.write("|--------|----------------|------------|-------------|\n")
            
            b = table3["baseline"]
            s = table3["system"]
            imp = table3["improvements"]
            
            # Token metrics
            f.write(f"| **Avg Input Tokens** | {b['avg_input_tokens']:.0f} | {s['avg_input_tokens']:.0f} | **{imp['avg_input_tokens']:+.1f}%** |\n")
            f.write(f"| **Avg Output Tokens** | {b['avg_output_tokens']:.0f} | {s['avg_output_tokens']:.0f} | **{imp['avg_output_tokens']:+.1f}%** |\n")
            f.write(f"| **Avg Total Tokens** | {b['avg_total_tokens']:.0f} | {s['avg_total_tokens']:.0f} | **{imp['avg_total_tokens']:+.1f}%** |\n")
            
            # Efficiency metrics
            f.write(f"| **Tokens Per Correct Answer** | {b['tokens_per_correct_answer']:.0f} | {s['tokens_per_correct_answer']:.0f} | **{imp['tokens_per_correct_answer']:+.1f}%** |\n")
            f.write(f"| **Avg Latency** | {b['avg_latency']:.2f}s | {s['avg_latency']:.2f}s | **{imp['avg_latency']:+.1f}%** |\n")
            
            # Compression rate (calculated from total tokens)
            if b['avg_total_tokens'] > 0:
                compression = (1 - s['avg_total_tokens'] / b['avg_total_tokens']) * 100
                compression_ratio = b['avg_total_tokens'] / s['avg_total_tokens'] if s['avg_total_tokens'] > 0 else 0
                f.write(f"| **Token Compression Rate** | 0% | {compression:.1f}% | **{compression_ratio:.2f}x compression** |\n")
            
            # Cost metrics
            f.write(f"| **Cost per Query** | ${b['cost_per_query']:.6f} | ${s['cost_per_query']:.6f} | **{imp['cost_per_query']:+.1f}%** |\n")
            f.write(f"| **Cost per 1M Queries** | ${b['cost_per_1m_queries']:.0f} | ${s['cost_per_1m_queries']:.0f} | **-${(b['cost_per_1m_queries'] - s['cost_per_1m_queries']):.0f} savings** |\n")
        
        self.log(f"✅ Generated TABLE_3_SYSTEM_PERFORMANCE.md", "INFO")

    def git_commit_and_push(self, files_to_add: List[str], commit_message: str) -> tuple:
        """Commit and push to GitHub"""
        try:
            original_cwd = os.getcwd()
            os.chdir(self.repo_root)
            
            self.log("="*80, "INFO")
            self.log("📤 GIT PUSH: Starting commit and push", "INFO")
            self.log("="*80, "INFO")
            
            for file_path in files_to_add:
                try:
                    rel_path = Path(file_path).relative_to(self.repo_root)
                except ValueError:
                    rel_path = Path(file_path)
                subprocess.run(["git", "add", str(rel_path)], capture_output=True)
                self.log(f"  ✅ Added: {rel_path}", "INFO")
            
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True, text=True
            )
            
            if commit_result.returncode != 0:
                if "nothing to commit" in commit_result.stdout.lower():
                    self.log("  ℹ️  No changes to commit", "INFO")
                    return True, "No changes"
                return False, f"Commit failed: {commit_result.stderr}"
            
            self.log(f"  ✅ Committed: {commit_message}", "INFO")
            
            if "GITHUB_TOKEN" not in os.environ:
                return False, "GITHUB_TOKEN not found"
            
            repo_url = f"https://{os.environ['GITHUB_TOKEN']}@github.com/moonmehedi/Subchat-Trees-A-Scalable-Architecture-for-Multi-Threaded-Dialogue-and-Context-Isolation-in-LLM.git"
            subprocess.run(["git", "remote", "set-url", "origin", repo_url], capture_output=True)
            
            push_result = subprocess.run(
                ["git", "push", "origin", self.repo_branch],
                capture_output=True, text=True
            )
            
            if push_result.returncode == 0:
                self.log("  ✅ Push successful!", "INFO")
                return True, "Push successful"
            else:
                return False, f"Push failed: {push_result.stderr}"
        except Exception as e:
            return False, f"Exception: {e}"
        finally:
            os.chdir(original_cwd)

    def push_buffer_results(self, buffer_size: int) -> bool:
        """Push results for completed buffer test"""
        self.log(f"\n📤 PUSHING RESULTS FOR BUFFER SIZE {buffer_size}", "INFO")
        
        buffer_dir = self.base_logs_dir / "tables" / f"buffer_{buffer_size}"
        files_to_push = []
        
        for f in buffer_dir.glob("*"):
            files_to_push.append(str(f))
        
        # Also add log files
        if self.baseline_log_file and self.baseline_log_file.exists():
            files_to_push.append(str(self.baseline_log_file))
        if self.system_log_file and self.system_log_file.exists():
            files_to_push.append(str(self.system_log_file))
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Kaggle SERVERLESS: Buffer {buffer_size} results - {timestamp}"
        
        success, message = self.git_commit_and_push(files_to_push, commit_msg)
        
        if success:
            self.log(f"✅ Pushed buffer {buffer_size} results", "INFO")
        else:
            self.log(f"❌ Push failed: {message}", "ERROR")
        
        return success

    def run_full_evaluation(self, scenario_files: List[str], buffer_size: int = 15):
        """Run complete evaluation for a buffer size"""
        self.setup_buffer_logs(buffer_size)
        
        test_mode = getattr(self, 'test_mode', 'both')
        
        self.log("="*80, "INFO")
        self.log(f"🚀 STARTING SERVERLESS EVALUATION (buffer_size={buffer_size})", "INFO")
        self.log(f"   Test mode: {test_mode.upper()}", "INFO")
        self.log("   ✅ No server needed - using direct Python imports", "INFO")
        self.log("="*80, "INFO")
        
        all_baseline_results = []
        all_system_results = []
        
        for scenario_file in scenario_files:
            scenario = self.load_scenario(scenario_file)
            if not scenario:
                continue
            
            # BASELINE TEST (only if mode is 'baseline' or 'both')
            if test_mode in ['baseline', 'both']:
                self.log(f"\n🔵 BASELINE TEST: {scenario_file}", "INFO")
                self.clear_state()
                baseline_results = self.run_baseline_test(scenario, buffer_size=buffer_size)
                all_baseline_results.extend(baseline_results)
            
            # SYSTEM TEST (only if mode is 'system' or 'both')
            if test_mode in ['system', 'both']:
                self.log(f"\n🟢 SYSTEM TEST: {scenario_file}", "INFO")
                self.clear_state()
                system_results = self.run_system_test(scenario, buffer_size=buffer_size)
                all_system_results.extend(system_results)
        
        # Calculate metrics
        self.log("\n📊 Calculating metrics...", "INFO")
        metrics = self.calculate_metrics(all_baseline_results, all_system_results)
        
        # Print summary
        self.log("\n" + "="*80, "INFO")
        self.log("📊 FINAL METRICS COMPARISON", "INFO")
        self.log("="*80, "INFO")
        
        iso_baseline = metrics["table_1"]["baseline"]
        iso_system = metrics["table_1"]["system"]
        
        self.log(f"\n🔵 BASELINE: Accuracy={iso_baseline['accuracy']:.1f}%, Pollution={iso_baseline['pollution_rate']:.1f}%", "INFO")
        self.log(f"🟢 SYSTEM:   Accuracy={iso_system['accuracy']:.1f}%, Pollution={iso_system['pollution_rate']:.1f}%", "INFO")
        
        # Generate tables
        self.generate_table(metrics)
        
        # Save raw results
        buffer_dir = self.base_logs_dir / "tables" / f"buffer_{self.current_buffer_size}"
        buffer_dir.mkdir(parents=True, exist_ok=True)
        
        with open(buffer_dir / "raw_metrics_baseline.json", 'w') as f:
            json.dump(all_baseline_results, f, indent=2)
        with open(buffer_dir / "raw_metrics_system.json", 'w') as f:
            json.dump(all_system_results, f, indent=2)
        with open(buffer_dir / "raw_metrics.json", 'w') as f:
            json.dump({"buffer_size": self.current_buffer_size, "metrics": metrics}, f, indent=2)
        
        self.log(f"\n✅ Results saved to: {buffer_dir}", "INFO")

    def generate_comparison_visualization(self, all_metrics: Dict[int, Dict]):
        """Generate HTML visualization comparing all buffer sizes"""
        viz_dir = self.base_logs_dir / "visualization"
        viz_dir.mkdir(exist_ok=True)
        
        html_file = viz_dir / "index.html"
        
        # Prepare data for charts
        buffer_sizes = sorted(all_metrics.keys())
        
        # Extract metrics
        baseline_precision = [all_metrics[bs]["table_1"]["baseline"]["precision"] for bs in buffer_sizes]
        system_precision = [all_metrics[bs]["table_1"]["system"]["precision"] for bs in buffer_sizes]
        
        baseline_recall = [all_metrics[bs]["table_1"]["baseline"]["recall"] for bs in buffer_sizes]
        system_recall = [all_metrics[bs]["table_1"]["system"]["recall"] for bs in buffer_sizes]
        
        baseline_f1 = [all_metrics[bs]["table_1"]["baseline"]["f1"] for bs in buffer_sizes]
        system_f1 = [all_metrics[bs]["table_1"]["system"]["f1"] for bs in buffer_sizes]
        
        baseline_accuracy = [all_metrics[bs]["table_1"]["baseline"]["accuracy"] for bs in buffer_sizes]
        system_accuracy = [all_metrics[bs]["table_1"]["system"]["accuracy"] for bs in buffer_sizes]
        
        baseline_pollution = [all_metrics[bs]["table_1"]["baseline"]["pollution_rate"] for bs in buffer_sizes]
        system_pollution = [all_metrics[bs]["table_1"]["system"]["pollution_rate"] for bs in buffer_sizes]
        
        # Generate HTML with Chart.js
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kaggle Serverless - Buffer Size Comparison</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .kaggle-badge {{
            background: #20BEFF;
            color: white;
            padding: 5px 15px;
            border-radius: 5px;
            display: inline-block;
            margin: 10px auto;
        }}
        .serverless-badge {{
            background: #10B981;
            color: white;
            padding: 5px 15px;
            border-radius: 5px;
            display: inline-block;
            margin: 10px;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Kaggle Serverless Buffer Size Comparison</h1>
        <p class="subtitle">Subchat Trees: Direct Python Imports - No Server Needed</p>
        <div style="text-align: center;">
            <span class="kaggle-badge">Tested on Kaggle GPUs</span>
            <span class="serverless-badge">Serverless Architecture</span>
        </div>
        
        <h2>📊 Context Isolation Metrics</h2>
        
        <div class="chart-container">
            <canvas id="accuracyChart"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="precisionChart"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="recallChart"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="f1Chart"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="pollutionChart"></canvas>
        </div>
    </div>
    
    <script>
        const bufferSizes = {json.dumps(buffer_sizes)};
        const baselineAccuracy = {json.dumps(baseline_accuracy)};
        const systemAccuracy = {json.dumps(system_accuracy)};
        const baselinePrecision = {json.dumps(baseline_precision)};
        const systemPrecision = {json.dumps(system_precision)};
        const baselineRecall = {json.dumps(baseline_recall)};
        const systemRecall = {json.dumps(system_recall)};
        const baselineF1 = {json.dumps(baseline_f1)};
        const systemF1 = {json.dumps(system_f1)};
        const baselinePollution = {json.dumps(baseline_pollution)};
        const systemPollution = {json.dumps(system_pollution)};
        
        const chartOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ position: 'top' }}
            }},
            scales: {{
                y: {{ beginAtZero: true }}
            }}
        }};
        
        new Chart(document.getElementById('accuracyChart'), {{
            type: 'line',
            data: {{
                labels: bufferSizes,
                datasets: [{{
                    label: 'Baseline Accuracy',
                    data: baselineAccuracy,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                }}, {{
                    label: 'System Accuracy',
                    data: systemAccuracy,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                }}]
            }},
            options: {{
                ...chartOptions,
                plugins: {{
                    ...chartOptions.plugins,
                    title: {{ display: true, text: 'Accuracy vs Buffer Size (%)' }}
                }}
            }}
        }});
        
        new Chart(document.getElementById('precisionChart'), {{
            type: 'line',
            data: {{
                labels: bufferSizes,
                datasets: [{{
                    label: 'Baseline Precision',
                    data: baselinePrecision,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                }}, {{
                    label: 'System Precision',
                    data: systemPrecision,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                }}]
            }},
            options: {{
                ...chartOptions,
                plugins: {{
                    ...chartOptions.plugins,
                    title: {{ display: true, text: 'Precision vs Buffer Size (%)' }}
                }}
            }}
        }});
        
        new Chart(document.getElementById('recallChart'), {{
            type: 'line',
            data: {{
                labels: bufferSizes,
                datasets: [{{
                    label: 'Baseline Recall',
                    data: baselineRecall,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                }}, {{
                    label: 'System Recall',
                    data: systemRecall,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                }}]
            }},
            options: {{
                ...chartOptions,
                plugins: {{
                    ...chartOptions.plugins,
                    title: {{ display: true, text: 'Recall vs Buffer Size (%)' }}
                }}
            }}
        }});
        
        new Chart(document.getElementById('f1Chart'), {{
            type: 'line',
            data: {{
                labels: bufferSizes,
                datasets: [{{
                    label: 'Baseline F1 Score',
                    data: baselineF1,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                }}, {{
                    label: 'System F1 Score',
                    data: systemF1,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                }}]
            }},
            options: {{
                ...chartOptions,
                plugins: {{
                    ...chartOptions.plugins,
                    title: {{ display: true, text: 'F1 Score vs Buffer Size (%)' }}
                }}
            }}
        }});
        
        new Chart(document.getElementById('pollutionChart'), {{
            type: 'line',
            data: {{
                labels: bufferSizes,
                datasets: [{{
                    label: 'Baseline Pollution Rate',
                    data: baselinePollution,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                }}, {{
                    label: 'System Pollution Rate',
                    data: systemPollution,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                }}]
            }},
            options: {{
                ...chartOptions,
                plugins: {{
                    ...chartOptions.plugins,
                    title: {{ display: true, text: 'Pollution Rate vs Buffer Size (%) - Lower is Better' }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
        
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        self.log(f"✅ Generated Kaggle Serverless visualization: {html_file}", "INFO")

    def run_buffer_comparison(self, scenario_files: List[str], buffer_sizes: List[int] = [5, 10, 20, 40]):
        """Run evaluation across multiple buffer sizes"""
        
        with open(self.main_log_file, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write("KAGGLE SERVERLESS BUFFER COMPARISON\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Buffer sizes: {buffer_sizes}\n")
            f.write(f"{'='*80}\n\n")
        
        self.log("="*80, "INFO")
        self.log("🚀 STARTING KAGGLE SERVERLESS MULTI-BUFFER COMPARISON", "INFO")
        self.log(f"   Buffer sizes: {buffer_sizes}", "INFO")
        self.log(f"   Scenarios: {scenario_files}", "INFO")
        self.log("   ✅ Using DIRECT Python imports - NO SERVER NEEDED", "INFO")
        self.log("="*80, "INFO")
        
        all_metrics = {}
        
        for buffer_size in buffer_sizes:
            self.log(f"\n{'='*80}", "INFO")
            self.log(f"📦 TESTING BUFFER SIZE: {buffer_size}", "INFO")
            self.log(f"{'='*80}", "INFO")
            
            self.run_full_evaluation(scenario_files, buffer_size=buffer_size)
            
            # Load the generated metrics from buffer-specific directory
            buffer_dir = self.base_logs_dir / "tables" / f"buffer_{buffer_size}"
            metrics_file = buffer_dir / "raw_metrics.json"
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    results = json.load(f)
                    all_metrics[buffer_size] = results["metrics"]
            
            # Push after each buffer
            push_success = self.push_buffer_results(buffer_size)
            
            if not push_success:
                self.log("❌ CRITICAL: Git push failed! Stopping.", "ERROR")
                return
            
            self.log(f"\n✅ Completed buffer size {buffer_size}", "INFO")
        
        # Generate comparison visualization
        self.log("\n📊 Generating final comparison visualization...", "INFO")
        self.generate_comparison_visualization(all_metrics)
        
        # Push final visualization
        viz_file = self.base_logs_dir / "visualization" / "index.html"
        if viz_file.exists():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"Kaggle Serverless: Final comparison visualization - {timestamp}"
            success, message = self.git_commit_and_push([str(viz_file)], commit_msg)
            
            if not success:
                # Log warning to both console AND file so it's visible in Kaggle logs
                warning_msg = f"⚠️  Warning: Could not push visualization: {message}"
                self.log(warning_msg, "WARN")
                # Also write to main log explicitly
                with open(self.main_log_file, 'a') as f:
                    f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] {warning_msg}\n")
        
        self.log("\n🎉 KAGGLE SERVERLESS MULTI-BUFFER COMPARISON COMPLETE!", "INFO")
        self.log(f"   All results pushed to branch: {self.repo_branch}", "INFO")
        self.log(f"   Results directory: {self.base_logs_dir / 'tables'}", "INFO")
        self.log(f"   Visualization: {self.base_logs_dir / 'visualization' / 'index.html'}", "INFO")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Kaggle Serverless Test Runner")
    parser.add_argument("--test", "-t", 
                        choices=["baseline", "system", "both"], 
                        default="both",
                        help="Which test to run: baseline, system, or both (default: both)")
    parser.add_argument("--buffer", "-b", 
                        type=int, 
                        nargs="+",
                        default=[5],
                        help="Buffer size(s) to test (default: 5). Example: --buffer 5 10 20 40")
    parser.add_argument("--scenario", "-s",
                        type=str,
                        nargs="+",
                        default=["06_lost_in_conversation_sharded_humaneval.json"],
                        help="Scenario file(s) to use. Example: --scenario file1.json file2.json OR --scenario all")
    
    args = parser.parse_args()
    
    runner = ServerlessTestRunner()
    
    # Store test mode for use in run methods
    runner.test_mode = args.test
    
    # Handle "all" keyword to run all scenarios
    if args.scenario == ["all"] or args.scenario == "all":
        import glob
        scenario_dir = Path(__file__).parent / "scenarios"
        scenario_files = [f.name for f in scenario_dir.glob("*.json")]
    else:
        scenario_files = args.scenario
    
    print(f"🚀 Running: {args.test.upper()} test(s)")
    print(f"📦 Buffer sizes: {args.buffer}")
    print(f"📄 Scenarios: {scenario_files}")
    
    runner.run_buffer_comparison(
        scenario_files,
        buffer_sizes=args.buffer
    )


# Usage examples:
# python kaggle_serverless_runner.py --test baseline --buffer 5
# python kaggle_serverless_runner.py --test system --buffer 10
# python kaggle_serverless_runner.py --test both --buffer 5 10 20 40
# python kaggle_serverless_runner.py -t system -b 5
# python kaggle_serverless_runner.py -t system -b 5 -s scenario1.json scenario2.json
# python kaggle_serverless_runner.py -t both -b 5 10 -s all  # Run all scenarios



# python kaggle_serverless_runner.py --test system --buffer 5 --scenario 06_lost_in_conversation_sharded_humaneval.json 22807e655dd042348cb0ee4023672e70_structured.json

# python kaggle_serverless_runner.py --test system --buffer 5 --scenario all

# python kaggle_serverless_runner.py --test both --buffer 5 10 20 40 --scenario all

# python kaggle_serverless_runner.py -t system -b 5 10 -s all