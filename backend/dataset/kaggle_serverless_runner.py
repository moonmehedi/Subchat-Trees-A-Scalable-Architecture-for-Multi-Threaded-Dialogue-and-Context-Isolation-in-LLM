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
from src.services.simple_llm import SimpleLLMClient
from src.models.tree import TreeNode


class ServerlessTestRunner:
    """
    Run tests using direct Python imports - NO SERVER NEEDED
    This runs in the same process as the vLLM model
    """
    
    def __init__(self, repo_branch: str = "kaggle-run"):
        self.classifier = ContextClassifier()
        self.repo_branch = repo_branch
        
        # Enable vector index for message archiving
        self.llm_client = SimpleLLMClient(enable_vector_index=True)
        
        # Track nodes in memory (no server/database)
        self.nodes: Dict[str, TreeNode] = {}
        
        # Setup directories - ALL logs go to dataset/logs/
        # Detect Kaggle environment
        if os.path.exists("/kaggle"):
            self.base_logs_dir = Path("/kaggle/working/logs")
        else:
            self.base_logs_dir = Path(__file__).parent / "logs"  # dataset/logs/
        
        self.base_logs_dir.mkdir(parents=True, exist_ok=True)
        self.main_log_file = self.base_logs_dir / "test_execution.log"
        
        self.current_buffer_size = None
        self.buffer_log_dir: Optional[Path] = None
        self.baseline_log_file: Optional[Path] = None
        self.system_log_file: Optional[Path] = None
        
        # Git configuration
        self.repo_root = Path(__file__).parent.parent.parent

    def setup_buffer_logs(self, buffer_size: int):
        """Setup buffer-specific log directory with ALL logs in one place"""
        self.current_buffer_size = buffer_size
        
        # All logs go to buffer_log_dir (e.g., dataset/logs/buffer_40/)
        self.buffer_log_dir = self.base_logs_dir / f"buffer_{buffer_size}"
        self.buffer_log_dir.mkdir(parents=True, exist_ok=True)
        
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
        components = ["BUFFER", "VECTOR_STORE", "RETRIEVAL", "COT_THINKING"]
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

    def clear_state(self):
        """Clear all nodes in memory for fresh test"""
        self.nodes.clear()
        
        # Clear ChromaDB if it exists
        try:
            chroma_db_path = Path(__file__).parent.parent / "chroma_db"
            if chroma_db_path.exists():
                shutil.rmtree(chroma_db_path)
                self.log("🗑️  Cleared ChromaDB", "INFO")
        except Exception as e:
            self.log(f"⚠️  ChromaDB clear warning: {e}", "WARN")
    
    def create_conversation(self, title: str, buffer_size: int = 15) -> Optional[str]:
        """Create a new root conversation (direct Python, no HTTP)"""
        import uuid
        node_id = str(uuid.uuid4())[:8]
        
        try:
            node = TreeNode(
                node_id=node_id,
                title=title,
                buffer_size=buffer_size,
                llm_client=self.llm_client,
                vector_index=self.llm_client.vector_index
            )
            self.nodes[node_id] = node
            
            # Log buffer creation
            self.log_buffer(f"🌳 Created root conversation node (id={node_id}, buffer_size={buffer_size})")
            self.log_buffer(f"   Title: {title}", full=True)
            if self.llm_client.vector_index:
                self.log_vector_store(f"📊 Vector index attached to node {node_id}")
            
            return node_id
        except Exception as e:
            self.log(f"❌ Failed to create conversation: {e}", "ERROR")
            return None
    
    def create_subchat(self, parent_id: str, title: str, selected_text: Optional[str] = None, buffer_size: int = 15) -> Optional[str]:
        """Create a subchat under a parent node (direct Python, no HTTP)"""
        import uuid
        
        parent = self.nodes.get(parent_id)
        if not parent:
            self.log(f"❌ Parent node not found: {parent_id}", "ERROR")
            return None
        
        node_id = str(uuid.uuid4())[:8]
        
        try:
            child = TreeNode(
                node_id=node_id,
                title=title,
                buffer_size=buffer_size,
                llm_client=self.llm_client,
                parent=parent,
                vector_index=self.llm_client.vector_index
            )
            
            # Log subchat creation
            self.log_buffer(f"🌿 Created subchat node (id={node_id}, parent={parent_id}, buffer_size={buffer_size})")
            self.log_buffer(f"   Title: {title}", full=True)
            
            # If selected_text provided, add as context
            if selected_text:
                child.buffer.add_message("system", f"Follow-up context: {selected_text}")
                self.log_buffer(f"   Context inherited: {selected_text}", full=True)
            
            parent.add_child(child)
            self.nodes[node_id] = child
            return node_id
        except Exception as e:
            self.log(f"❌ Failed to create subchat: {e}", "ERROR")
            return None
    
    def send_message(self, node_id: str, message: str) -> Optional[Dict]:
        """Send message and get response (direct Python, no HTTP)"""
        node = self.nodes.get(node_id)
        if not node:
            self.log(f"❌ Node not found: {node_id}", "ERROR")
            return None
        
        try:
            start_time = time.time()
            
            # Add user message to buffer
            node.buffer.add_message("user", message)
            buffer_size = len(node.buffer.turns)  # LocalBuffer uses 'turns' not 'messages'
            self.log_buffer(f"📥 Added user message to buffer (node={node_id}, buffer_size={buffer_size})")
            self.log_buffer(f"   Message: {message}", full=True)
            
            # Generate response using LLM
            response_text = self.llm_client.generate_response(node, message)
            self.log_cot_thinking(f"🤖 Generated response for node={node_id}")
            self.log_cot_thinking(f"   Response: {response_text}", full=True)
            
            # Add assistant response to buffer
            node.buffer.add_message("assistant", response_text)
            buffer_size = len(node.buffer.turns)  # LocalBuffer uses 'turns' not 'messages'
            self.log_buffer(f"📤 Added assistant response to buffer (node={node_id}, buffer_size={buffer_size})")
            
            # Check if buffer triggered eviction to vector store
            if hasattr(node.buffer, 'messages_processed_count'):
                self.log_vector_store(f"📦 Messages processed: {node.buffer.messages_processed_count}")
                self.log_vector_store(f"   Node: {node_id}, Buffer max: {node.buffer.max_turns}", full=True)
            
            latency = time.time() - start_time
            
            return {
                "response": response_text,
                "latency": latency,
                "usage": {
                    "prompt_tokens": 0,  # vLLM doesn't easily expose this
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
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
                return json.load(f)
        except json.JSONDecodeError as e:
            self.log(f"❌ Invalid JSON in {scenario_file}: {e}", "ERROR")
            return None

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
        
        # Create ONE conversation for all contexts
        main_node_id = self.create_conversation("Baseline - All Topics", buffer_size=buffer_size)
        if not main_node_id:
            self.log("❌ Failed to create baseline conversation", "ERROR", "baseline")
            return results
        
        self.log(f"  📝 Created single conversation for all topics", "INFO", "baseline")
        
        tp_count = tn_count = fp_count = fn_count = 0
        
        for step_data in scenario["conversations"]:
            step = step_data["step"]
            context = step_data["context"]
            message = step_data["message"]
            expected = step_data["expected"]
            
            self.log(f"\n[Step {step}] Context: {context}", "INFO", "baseline")
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
            
            # Classify response
            classification_details = self.classifier.get_classification_details(ai_message, expected)
            classification = classification_details["classification"]
            
            # Log to COT_THINKING for classification reasoning
            self.log_cot_thinking(f"🧠 Classification for step {step}: {classification}")
            self.log_cot_thinking(f"   Expected: {expected}", full=True)
            self.log_cot_thinking(f"   Method: {classification_details['method']}", full=True)
            
            if classification == "TP":
                tp_count += 1
            elif classification == "TN":
                tn_count += 1
            elif classification == "FP":
                fp_count += 1
            elif classification == "FN":
                fn_count += 1
            
            if classification in ["TP", "TN"]:
                self.log(f"  ✅ Classification: {classification} ({classification_details['method']})", "INFO", "baseline")
            else:
                self.log(f"  ❌ Classification: {classification} ({classification_details['method']})", "WARN", "baseline")
            
            results.append({
                "step": step,
                "context": context,
                "message": message,
                "response": ai_message,
                "classification": classification,
                "classification_details": classification_details,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "latency": response.get("latency", 0),
                "rag_used": False
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
        
        tp_count = tn_count = fp_count = fn_count = 0
        
        # Create main conversation
        main_id = self.create_conversation("System Test - Main", buffer_size=buffer_size)
        if not main_id:
            self.log("❌ Failed to create main conversation", "ERROR", "system")
            return results
        
        node_map["main"] = main_id
        self.log(f"  📝 Created main conversation", "INFO", "system")
        
        for step_data in scenario["conversations"]:
            step = step_data["step"]
            context = step_data["context"]
            message = step_data["message"]
            expected = step_data["expected"]
            node_type = step_data.get("node_type", "main")
            action = step_data.get("action", "")
            
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
            
            self.log(f"\n[Step {step}] Context: {context} | Node: {node_type}", "INFO", "system")
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
            
            # Classify response
            classification_details = self.classifier.get_classification_details(ai_message, expected)
            classification = classification_details["classification"]
            
            # Log to COT_THINKING for classification reasoning
            self.log_cot_thinking(f"🧠 System test classification for step {step}: {classification}")
            self.log_cot_thinking(f"   Node type: {node_type}, Expected: {expected}", full=True)
            self.log_cot_thinking(f"   Method: {classification_details['method']}", full=True)
            
            if classification == "TP":
                tp_count += 1
            elif classification == "TN":
                tn_count += 1
            elif classification == "FP":
                fp_count += 1
            elif classification == "FN":
                fn_count += 1
            
            if classification in ["TP", "TN"]:
                self.log(f"  ✅ Classification: {classification} ({classification_details['method']})", "INFO", "system")
            else:
                self.log(f"  ❌ Classification: {classification} ({classification_details['method']})", "WARN", "system")
            
            results.append({
                "step": step,
                "context": context,
                "node_type": node_type,
                "message": message,
                "response": ai_message,
                "classification": classification,
                "classification_details": classification_details,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "latency": response.get("latency", 0),
                "rag_used": False
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
        """Calculate all metrics for tables"""
        
        def calc_isolation_metrics(results):
            tp = sum(1 for r in results if r["classification"] == "TP")
            tn = sum(1 for r in results if r["classification"] == "TN")
            fp = sum(1 for r in results if r["classification"] == "FP")
            fn = sum(1 for r in results if r["classification"] == "FN")
            total = len(results)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            accuracy = (tp + tn) / total if total > 0 else 0
            pollution_rate = (fp + fn) / total if total > 0 else 0
            
            return {
                "precision": precision * 100,
                "recall": recall * 100,
                "f1": f1 * 100,
                "accuracy": accuracy * 100,
                "pollution_rate": pollution_rate * 100,
                "tp": tp, "tn": tn, "fp": fp, "fn": fn
            }
        
        def calc_performance_metrics(results, isolation_metrics):
            if not results:
                return {"avg_latency": 0, "tokens_per_correct_answer": 0}
            
            avg_latency = sum(r["latency"] for r in results) / len(results)
            
            accuracy = isolation_metrics.get("accuracy", 0)
            if accuracy > 0:
                tokens_per_correct = 0  # We don't have token counts from vLLM
            else:
                tokens_per_correct = 0
            
            return {
                "avg_input_tokens": 0,
                "avg_output_tokens": 0,
                "avg_total_tokens": 0,
                "avg_latency": avg_latency,
                "buffer_hit_rate": 0,
                "archive_hit_rate": 0,
                "tokens_per_correct_answer": tokens_per_correct
            }
        
        baseline_isolation = calc_isolation_metrics(baseline_results)
        system_isolation = calc_isolation_metrics(system_results)
        
        baseline_performance = calc_performance_metrics(baseline_results, baseline_isolation)
        system_performance = calc_performance_metrics(system_results, system_isolation)
        
        def calc_improvement(baseline, system):
            if baseline == 0:
                return 0
            return ((system - baseline) / baseline) * 100
        
        return {
            "table_1": {
                "baseline": baseline_isolation,
                "system": system_isolation,
                "improvements": {
                    k: calc_improvement(baseline_isolation.get(k, 0), system_isolation.get(k, 0))
                    for k in ["precision", "recall", "f1", "accuracy", "pollution_rate"]
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
        buffer_dir = self.logs_dir / "tables" / f"buffer_{self.current_buffer_size}"
        buffer_dir.mkdir(parents=True, exist_ok=True)
        
        table1 = metrics["table_1"]
        with open(buffer_dir / "TABLE_1_CONTEXT_ISOLATION.md", 'w') as f:
            f.write(f"# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: {self.current_buffer_size})\n\n")
            f.write("| Metric | Baseline System | Our System | Improvement |\n")
            f.write("|--------|----------------|------------|-------------|\n")
            
            for metric in ["precision", "recall", "f1", "accuracy", "pollution_rate"]:
                baseline_val = table1["baseline"][metric]
                system_val = table1["system"][metric]
                improvement = table1["improvements"][metric]
                f.write(f"| **{metric.replace('_', ' ').title()}** | ")
                f.write(f"{baseline_val:.1f}% | {system_val:.1f}% | ")
                f.write(f"**{improvement:+.1f}%** |\n")
            
            f.write(f"\n## Raw Counts\n")
            f.write(f"- Baseline: TP={table1['baseline']['tp']}, TN={table1['baseline']['tn']}, FP={table1['baseline']['fp']}, FN={table1['baseline']['fn']}\n")
            f.write(f"- System: TP={table1['system']['tp']}, TN={table1['system']['tn']}, FP={table1['system']['fp']}, FN={table1['system']['fn']}\n")
        
        self.log(f"✅ Generated TABLE_1_CONTEXT_ISOLATION.md", "INFO")
        
        table3 = metrics["table_3"]
        with open(buffer_dir / "TABLE_3_SYSTEM_PERFORMANCE.md", 'w') as f:
            f.write(f"# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: {self.current_buffer_size})\n\n")
            f.write("| Metric | Baseline System | Our System | Improvement |\n")
            f.write("|--------|----------------|------------|-------------|\n")
            
            baseline_lat = table3["baseline"]["avg_latency"]
            system_lat = table3["system"]["avg_latency"]
            lat_improvement = table3["improvements"]["avg_latency"]
            f.write(f"| **Avg Latency** | {baseline_lat:.2f}s | {system_lat:.2f}s | **{lat_improvement:+.1f}%** |\n")
        
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
        
        buffer_dir = self.logs_dir / "tables" / f"buffer_{buffer_size}"
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
        
        self.log("="*80, "INFO")
        self.log(f"🚀 STARTING SERVERLESS EVALUATION (buffer_size={buffer_size})", "INFO")
        self.log("   ✅ No server needed - using direct Python imports", "INFO")
        self.log("="*80, "INFO")
        
        all_baseline_results = []
        all_system_results = []
        
        for scenario_file in scenario_files:
            scenario = self.load_scenario(scenario_file)
            if not scenario:
                continue
            
            # BASELINE TEST
            self.log(f"\n🔵 BASELINE TEST: {scenario_file}", "INFO")
            self.clear_state()
            baseline_results = self.run_baseline_test(scenario, buffer_size=buffer_size)
            all_baseline_results.extend(baseline_results)
            
            # SYSTEM TEST
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
        buffer_dir = self.logs_dir / "tables" / f"buffer_{self.current_buffer_size}"
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
        viz_dir = self.logs_dir / "visualization"
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
            buffer_dir = self.logs_dir / "tables" / f"buffer_{buffer_size}"
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
        viz_file = self.logs_dir / "visualization" / "index.html"
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
        self.log(f"   Results directory: {self.logs_dir / 'tables'}", "INFO")
        self.log(f"   Visualization: {self.logs_dir / 'visualization' / 'index.html'}", "INFO")


if __name__ == "__main__":
    runner = ServerlessTestRunner()
    
    runner.run_buffer_comparison(
        ["06_lost_in_conversation_sharded_humaneval.json"],
        buffer_sizes=[5]
    )
