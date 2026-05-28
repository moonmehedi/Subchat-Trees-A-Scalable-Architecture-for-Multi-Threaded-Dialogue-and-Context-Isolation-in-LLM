#!/usr/bin/env python3
"""
Kaggle SERVERLESS Test Runner
Uses DIRECT Python imports instead of HTTP requests
This allows the test to run in the same process as the loaded vLLM model
serverless
"""

import os
import re
import sys
import json
import time
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

# Recall probe scoring (ROUGE/BLEU)
try:
    from rouge_score import rouge_scorer as rouge_scorer_module
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False

try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    import nltk
    BLEU_AVAILABLE = True
except ImportError:
    BLEU_AVAILABLE = False

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
        
        # Initialize recall probe detail log
        recall_log = self.buffer_log_dir / "recall_probes_detail.log"
        with open(recall_log, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write(f"RECALL PROBES DETAIL LOG (Buffer Size: {buffer_size})\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")

        # Initialize RUNNER component log files (summary + full pairs)
        # These use RUNNER_ prefix to avoid colliding with DebugLogger files
        # (DebugLogger writes structured RAG pipeline logs to COT_THINKING.log, RETRIEVAL.log, etc.)
        components = ["BUFFER", "VECTOR_STORE", "RETRIEVAL", "COT_THINKING", "JUDGE"]
        for component in components:
            # Summary log
            summary_file = self.buffer_log_dir / f"RUNNER_{component}.log"
            with open(summary_file, 'w') as f:
                f.write(f"{'='*80}\n")
                f.write(f"RUNNER {component} LOG - SUMMARY (Buffer Size: {buffer_size})\n")
                f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
            
            # Full/detailed log
            full_file = self.buffer_log_dir / f"RUNNER_{component}_full.log"
            with open(full_file, 'w') as f:
                f.write(f"{'='*80}\n")
                f.write(f"RUNNER {component} LOG - DETAILED (Buffer Size: {buffer_size})\n")
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
        Log to RUNNER component-specific log files in buffer directory.
        Uses RUNNER_ prefix to avoid colliding with DebugLogger files.
        
        Args:
            component: One of 'BUFFER', 'VECTOR_STORE', 'RETRIEVAL', 'COT_THINKING', 'JUDGE'
            message: The message to log
            full: If True, log to RUNNER_{component}_full.log only (detailed info).
                  If False, log to both RUNNER_{component}.log (summary) and RUNNER_{component}_full.log (detailed).
        """
        if self.buffer_log_dir is None:
            return  # Buffer logs not set up yet
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        
        # Always log to full/detailed log (RUNNER_ prefix)
        full_log_file = self.buffer_log_dir / f"RUNNER_{component}_full.log"
        with open(full_log_file, 'a') as f:
            f.write(log_msg + "\n")
        
        # If not full-only, also log to summary log (RUNNER_ prefix)
        if not full:
            summary_log_file = self.buffer_log_dir / f"RUNNER_{component}.log"
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

    def _log_recall_probe_detail(
        self,
        topic: str,
        target_node: str,
        probe_message: str,
        llm_response: str,
        reference_text: str,
        scores: dict,
        mode: str,
        is_main_only: bool = False,
    ):
        """
        Write detailed recall probe information to recall_probes_detail.log.

        Logs: topic, target node, probe question, full LLM summary,
        the real reference (user questions + AI responses), and BLEU/ROUGE scores.
        """
        if self.buffer_log_dir is None:
            return

        log_file = self.buffer_log_dir / "recall_probes_detail.log"
        with open(log_file, "a") as f:
            f.write(f"{'='*80}\n")
            f.write(f"RECALL PROBE — [{mode.upper()}] Topic: {topic}\n")
            f.write(f"Target Node: {target_node}")
            if is_main_only:
                f.write(" (⚠️ main-only topic — no subchat exists)")
            f.write(f"\n")
            f.write(f"{'-'*80}\n")

            # 1. The probe question
            f.write(f"\n📝 PROBE QUESTION:\n")
            f.write(f"   {probe_message}\n")

            # 2. The LLM's summary response
            f.write(f"\n🤖 LLM SUMMARY RESPONSE:\n")
            for line in llm_response.split("\n"):
                f.write(f"   {line}\n")

            # 3. Reference text (real user questions + AI responses used for scoring)
            f.write(f"\n📚 REFERENCE (User Questions + Real AI Responses):\n")
            f.write(f"{'-'*60}\n")
            if reference_text:
                # Split by User:/Assistant: markers for readable display
                for segment in reference_text.split("User: "):
                    segment = segment.strip()
                    if not segment:
                        continue
                    if "Assistant: " in segment:
                        user_part, assistant_part = segment.split("Assistant: ", 1)
                        f.write(f"   👤 User: {user_part.strip()}\n")
                        f.write(f"   🤖 AI: {assistant_part.strip()[:300]}\n")
                        f.write(f"   ---\n")
                    else:
                        f.write(f"   👤 User: {segment}\n")
            else:
                f.write(f"   ⚠️ No reference data collected for this topic\n")
            f.write(f"{'-'*60}\n")

            # 4. Scores
            f.write(f"\n📊 SCORES:\n")
            f.write(f"   ROUGE-1 (F1): {scores.get('rouge1_f', 0):.4f}\n")
            f.write(f"   ROUGE-L (F1): {scores.get('rougeL_f', 0):.4f}\n")
            f.write(f"   BLEU-2:       {scores.get('bleu', 0):.4f}\n")

            # 5. Quick reference text length comparison
            ref_words = len(reference_text.split()) if reference_text else 0
            resp_words = len(llm_response.split()) if llm_response else 0
            f.write(f"\n   Reference length: {ref_words} words\n")
            f.write(f"   Response length:  {resp_words} words\n")
            f.write(f"{'='*80}\n\n")

    def clear_state(self):
        """Clear all nodes in memory for fresh test"""
        # Clear nodes from ChatGraphManager and Forest (using core classes)
        self.chat.chat_manager.node_map.clear()
        self.chat.forest.trees_map.clear()
        self.chat.chat_manager.active_node_id = None
        self.chat.forest.active_tree_id = None
        
        # Clear VectorIndex properly (in-memory collection + on-disk ChromaDB)
        try:
            if self.chat.llm.vector_index:
                self.chat.llm.vector_index.clear()
                self.log("🗑️  Cleared VectorIndex (collection reset)", "INFO")
            else:
                # Fallback: delete on-disk ChromaDB if no vector_index object
                chroma_db_path = Path(__file__).parent.parent / "chroma_db"
                if chroma_db_path.exists():
                    shutil.rmtree(chroma_db_path)
                    self.log("🗑️  Cleared ChromaDB (disk)", "INFO")
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
    
    def send_message(self, node_id: str, message: str, enable_rag: bool = True) -> Optional[Dict]:
        """Send message and get response using SimpleChat core class
        
        Uses SimpleChat.send_message() or send_message_with_rag() which:
        1. Adds user message to buffer
        2. Calls llm.generate_response() (or generate_response_with_rag()) with proper context
        3. Adds assistant response to buffer
        4. Auto-generates title if needed
        
        Args:
            node_id: Target conversation node ID
            message: User message text
            enable_rag: If True, use RAG pipeline (LLM decides retrieval)
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
            self.log_buffer(f"📥 Sending message to node={node_id} (rag={enable_rag})")
            self.log_buffer(f"   Message: {message}", full=True)
            
            # Choose RAG or baseline path
            rag_metadata = None
            if enable_rag:
                # RAG path — LLM decides whether to retrieve
                response_text, rag_metadata = self.chat.send_message_with_rag(message)
            else:
                # Baseline path — no RAG
                response_text = self.chat.send_message(message)
            
            latency = time.time() - start_time
            
            # Log after response
            buffer_size = len(node.buffer.turns)
            self.log_buffer(f"📤 Response received (node={node_id}, buffer_size={buffer_size})")
            self.log_cot_thinking(f"🤖 Generated response for node={node_id}")
            self.log_cot_thinking(f"   Response: {response_text}", full=True)
            
            # Log RAG decision if applicable
            if rag_metadata:
                self.log_cot_thinking(f"   RAG decision: {rag_metadata.get('rag_decision', 'unknown')}")
                if rag_metadata.get('rag_used'):
                    self.log_retrieval(f"🔍 Retrieval triggered for node={node_id}")
                    self.log_retrieval(f"   Query: {rag_metadata.get('rag_query', 'N/A')}")
                    self.log_retrieval(f"   Results: {rag_metadata.get('rag_results_count', 0)} messages")
            
            # Check if buffer triggered summarization
            if hasattr(node.buffer, 'messages_processed_count'):
                self.log_vector_store(f"📦 Messages processed: {node.buffer.messages_processed_count}")
                self.log_vector_store(f"   Node: {node_id}, Buffer max: {node.buffer.max_turns}", full=True)
            
            # Get usage — prefer rag_metadata (captured before title generation)
            # over get_last_usage() which could be overwritten by title gen
            if rag_metadata and "usage" in rag_metadata:
                usage = rag_metadata["usage"]
            else:
                usage = self.chat.llm.get_last_usage()
            
            result = {
                "response": response_text,
                "latency": latency,
                "usage": usage
            }
            
            # Merge RAG metadata into result
            if rag_metadata:
                result["rag_used"] = rag_metadata.get("rag_used", False)
                result["rag_query"] = rag_metadata.get("rag_query")
                result["rag_results_count"] = rag_metadata.get("rag_results_count", 0)
                result["rag_decision"] = rag_metadata.get("rag_decision", "unknown")
            else:
                result["rag_used"] = False
                result["rag_decision"] = "disabled"
            
            return result
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
            base_topic = re.sub(suffix_pattern, "", base_topic)
        
        return base_topic.rstrip("_") or "general"

    def _extract_topic_regex(self, response: str, valid_topics: List[str]) -> Dict:
        """Extract topic from response using pure regex (all datasets use 'topic_name:' prefix)."""
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
        
        recall_probe_results = []  # Collect inline recall probe results
        topic_responses = {}  # {topic: [(user_msg, ai_response), ...]} — collect real AI responses per topic
        
        for step_data in scenario["conversations"]:
            step = step_data["step"]
            context = step_data["context"]
            message = step_data["message"]
            expected = step_data["expected"]
            
            # ── RECALL PROBE HANDLING (baseline: everything goes to main) ──
            if step_data.get("is_recall_probe", False):
                probe_topic = step_data.get("probe_topic", context)
                self.log(f"\n🔬 [Recall Probe] Topic: {probe_topic} → main node", "INFO", "baseline")
                self.log(f"  💬 Probe: {message}", "INFO", "baseline")
                
                response = self.send_message(main_node_id, message, enable_rag=True)
                if not response or not response.get("response"):
                    self.log(f"  ❌ No response for recall probe '{probe_topic}'", "WARN", "baseline")
                    recall_probe_results.append({
                        "topic": probe_topic, "mode": "baseline",
                        "rouge1_f": 0.0, "rougeL_f": 0.0, "bleu": 0.0,
                        "summary_length": 0,
                        "reference_length": 0,
                        "summary": "", "probe_tokens": 0, "probe_latency": 0.0,
                        "rag_used": False,
                        "rag_query": None,
                        "rag_results_count": 0,
                        "rag_decision": "no_response",
                        "is_main_only": step_data.get("is_main_only_topic", False),
                        "target_node": "main",
                    })
                    continue
                
                ai_summary = response["response"]
                # Build reference from real user questions + AI responses collected during the test
                ref_text = self._build_recall_reference(probe_topic, topic_responses)
                scores = self._compute_recall_scores(ai_summary, ref_text)
                
                self.log(f"  🤖 Summary: {ai_summary[:200]}...", "INFO", "baseline")
                self.log(f"  📊 ROUGE-1={scores['rouge1_f']:.3f}  ROUGE-L={scores['rougeL_f']:.3f}  BLEU={scores['bleu']:.3f}", "INFO", "baseline")
                
                # Detailed log
                self._log_recall_probe_detail(
                    topic=probe_topic,
                    target_node="main",
                    probe_message=message,
                    llm_response=ai_summary,
                    reference_text=ref_text,
                    scores=scores,
                    mode="baseline",
                    is_main_only=step_data.get("is_main_only_topic", False),
                )
                
                recall_probe_results.append({
                    "topic": probe_topic, "mode": "baseline",
                    "rouge1_f": scores["rouge1_f"],
                    "rougeL_f": scores["rougeL_f"],
                    "bleu": scores["bleu"],
                    "summary_length": len(ai_summary.split()),
                    "reference_length": len(ref_text.split()) if ref_text else 0,
                    "summary": ai_summary[:500],
                    "probe_tokens": response.get("usage", {}).get("total_tokens", 0),
                    "probe_latency": response.get("latency", 0.0),
                    "rag_used": response.get("rag_used", False),
                    "rag_query": response.get("rag_query"),
                    "rag_results_count": response.get("rag_results_count", 0),
                    "rag_decision": response.get("rag_decision", "unknown"),
                    "is_main_only": step_data.get("is_main_only_topic", False),
                    "target_node": "main",
                })
                time.sleep(0.3)
                continue  # Skip normal judge/topic evaluation for probes
            
            # ── NORMAL CONVERSATION STEP ──
            # Get expected topic from context
            expected_topic = self._normalize_context_to_topic(context)
            
            self.log(f"\n[Step {step}] Context: {context} (Topic: {expected_topic})", "INFO", "baseline")
            self.log(f"  💬 User: {message}", "INFO", "baseline")
            
            response = self.send_message(main_node_id, message, enable_rag=True)
            
            if not response:
                self.log("  ❌ No response received", "ERROR", "baseline")
                continue
            
            ai_message = response.get("response", "")
            
            if not ai_message:
                self.log("  ❌ Empty AI response", "ERROR", "baseline")
                continue
            
            # Collect user question + AI response per topic for recall probe reference
            if context not in ["intro", "step_1"]:
                topic_responses.setdefault(expected_topic, []).append((message, ai_message))
            
            self.log(f"  🤖 AI Response:", "INFO", "baseline")
            self.log(f"     {ai_message}", "INFO", "baseline")
            
            # Skip topic-prefix detection for intro/step_1 (acknowledgment, no topic prefix expected)
            if context in ["intro", "step_1"]:
                is_correct_topic = bool(ai_message.strip())
                detected_topic = "general"
                topic_detection = {"method": "intro_skip", "detected_topic": "general"}
                self.log(f"  ℹ️ Intro step - skipping topic detection (non-empty response = correct)", "INFO", "baseline")
            else:
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
                # Preserve the real RAG decision metadata from the baseline run.
                # Baseline means "single linear conversation", not "RAG disabled".
                "rag_used": response.get("rag_used", False),
                "rag_query": response.get("rag_query"),
                "rag_results_count": response.get("rag_results_count", 0),
                "rag_decision": response.get("rag_decision", "disabled"),
                "scenario_name": scenario_name
            })
            
            time.sleep(0.3)
        
        # Store inline recall probe results for aggregation
        self._last_baseline_recall_probes = recall_probe_results
        
        self.log("\n" + "="*80, "INFO", "baseline")
        self.log("📊 BASELINE TEST SUMMARY", "INFO", "baseline")
        self.log(f"   Total Steps: {len(results)}", "INFO", "baseline")
        self.log(f"   Recall Probes: {len(recall_probe_results)}", "INFO", "baseline")
        if recall_probe_results:
            avg_r1 = sum(r["rouge1_f"] for r in recall_probe_results) / len(recall_probe_results)
            avg_bl = sum(r["bleu"] for r in recall_probe_results) / len(recall_probe_results)
            self.log(f"   Recall Avg ROUGE-1={avg_r1:.3f}  BLEU={avg_bl:.3f}", "INFO", "baseline")
        correct = sum(1 for r in results if r.get("is_correct_topic", False))
        incorrect = len(results) - correct
        self.log(f"   ✅ Correct: {correct}", "INFO", "baseline")
        self.log(f"   ❌ Incorrect: {incorrect}", "INFO", "baseline")
        if results:
            self.log(f"   Accuracy: {(correct / len(results) * 100):.1f}%", "INFO", "baseline")
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
        
        # Create main conversation
        main_id = self.create_conversation("System Test - Main", buffer_size=buffer_size)
        if not main_id:
            self.log("❌ Failed to create main conversation", "ERROR", "system")
            return results
        
        node_map["main"] = main_id
        self.log(f"  📝 Created main conversation", "INFO", "system")
        self.log(f"  📋 Available topics for detection: {available_topics}", "INFO", "system")
        
        recall_probe_results = []  # Collect inline recall probe results
        topic_responses = {}  # {topic: [(user_msg, ai_response), ...]} — collect real AI responses per topic
        
        for step_data in scenario["conversations"]:
            step = step_data["step"]
            context = step_data["context"]
            message = step_data["message"]
            expected = step_data["expected"]
            node_type = step_data.get("node_type", "main")
            action = step_data.get("action", "")
            
            # ── RECALL PROBE HANDLING (system: route to correct subchat) ──
            if step_data.get("is_recall_probe", False):
                probe_topic = step_data.get("probe_topic", context)
                target_node = node_map.get(node_type, main_id)
                is_main_only = step_data.get("is_main_only_topic", False)
                actual_target = node_type if node_type in node_map else "main (fallback)"
                
                self.log(f"\n🔬 [Recall Probe] Topic: {probe_topic} → Node: {actual_target}", "INFO", "system")
                self.log(f"  💬 Probe: {message}", "INFO", "system")
                
                response = self.send_message(target_node, message, enable_rag=True)
                if not response or not response.get("response"):
                    self.log(f"  ❌ No response for recall probe '{probe_topic}'", "WARN", "system")
                    recall_probe_results.append({
                        "topic": probe_topic, "mode": "system",
                        "rouge1_f": 0.0, "rougeL_f": 0.0, "bleu": 0.0,
                        "summary_length": 0,
                        "reference_length": 0,
                        "summary": "", "probe_tokens": 0, "probe_latency": 0.0,
                        "rag_used": False,
                        "rag_query": None,
                        "rag_results_count": 0,
                        "rag_decision": "no_response",
                        "is_main_only": is_main_only,
                        "target_node": actual_target,
                    })
                    continue
                
                ai_summary = response["response"]
                # Build reference from real user questions + AI responses collected during the test
                ref_text = self._build_recall_reference(probe_topic, topic_responses)
                scores = self._compute_recall_scores(ai_summary, ref_text)
                
                self.log(f"  🤖 Summary: {ai_summary[:200]}...", "INFO", "system")
                self.log(f"  📊 ROUGE-1={scores['rouge1_f']:.3f}  ROUGE-L={scores['rougeL_f']:.3f}  BLEU={scores['bleu']:.3f}", "INFO", "system")
                
                # Detailed log
                self._log_recall_probe_detail(
                    topic=probe_topic,
                    target_node=actual_target,
                    probe_message=message,
                    llm_response=ai_summary,
                    reference_text=ref_text,
                    scores=scores,
                    mode="system",
                    is_main_only=is_main_only,
                )
                
                recall_probe_results.append({
                    "topic": probe_topic, "mode": "system",
                    "rouge1_f": scores["rouge1_f"],
                    "rougeL_f": scores["rougeL_f"],
                    "bleu": scores["bleu"],
                    "summary_length": len(ai_summary.split()),
                    "reference_length": len(ref_text.split()) if ref_text else 0,
                    "summary": ai_summary[:500],
                    "probe_tokens": response.get("usage", {}).get("total_tokens", 0),
                    "probe_latency": response.get("latency", 0.0),
                    "rag_used": response.get("rag_used", False),
                    "rag_query": response.get("rag_query"),
                    "rag_results_count": response.get("rag_results_count", 0),
                    "rag_decision": response.get("rag_decision", "unknown"),
                    "is_main_only": is_main_only,
                    "target_node": actual_target,
                })
                time.sleep(0.3)
                continue  # Skip normal judge/topic evaluation for probes
            
            # ── NORMAL CONVERSATION STEP ──
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
            elif action == "switch_node" and node_type not in node_map and node_type != "main":
                self.log(f"  ⚠️ switch_node to unknown '{node_type}', falling back to main", "WARN", "system")
            
            target_node = node_map.get(node_type, main_id)
            
            self.log(f"\n[Step {step}] Context: {context} (Topic: {expected_topic}) | Node: {node_type}", "INFO", "system")
            self.log(f"  💬 User: {message}", "INFO", "system")
            
            response = self.send_message(target_node, message, enable_rag=True)
            
            if not response:
                self.log("  ❌ No response received", "ERROR", "system")
                continue
            
            ai_message = response.get("response", "")
            
            if not ai_message:
                self.log("  ❌ Empty AI response", "ERROR", "system")
                continue
            
            # Collect user question + AI response per topic for recall probe reference
            if context not in ["intro", "step_1"]:
                topic_responses.setdefault(expected_topic, []).append((message, ai_message))
            
            self.log(f"  🤖 AI Response:", "INFO", "system")
            self.log(f"     {ai_message}", "INFO", "system")
            
            # Log RAG decision
            if response.get("rag_used"):
                self.log(f"  🔍 RAG triggered: query='{response.get('rag_query', 'N/A')}', results={response.get('rag_results_count', 0)}", "INFO", "system")
            
            # Skip topic-prefix detection for intro/step_1 (acknowledgment, no topic prefix expected)
            if context in ["intro", "step_1"]:
                is_correct_topic = bool(ai_message.strip())
                detected_topic = "general"
                topic_detection = {"method": "intro_skip", "detected_topic": "general"}
                self.log(f"  ℹ️ Intro step - skipping topic detection (non-empty response = correct)", "INFO", "system")
            else:
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
                "rag_used": response.get("rag_used", False),
                "rag_query": response.get("rag_query"),
                "rag_results_count": response.get("rag_results_count", 0),
                "rag_decision": response.get("rag_decision", "disabled"),
                "scenario_name": scenario_name
            })
            
            time.sleep(0.3)
        
        # Store inline recall probe results for aggregation
        self._last_system_recall_probes = recall_probe_results
        
        # Calculate retrieval rate
        rag_triggered = sum(1 for r in results if r.get("rag_used", False))
        retrieval_rate = (rag_triggered / len(results) * 100) if results else 0
        
        self.log("\n" + "="*80, "INFO", "system")
        self.log("📊 SYSTEM TEST SUMMARY", "INFO", "system")
        self.log(f"   Total Steps: {len(results)}", "INFO", "system")
        self.log(f"   Recall Probes: {len(recall_probe_results)}", "INFO", "system")
        if recall_probe_results:
            avg_r1 = sum(r["rouge1_f"] for r in recall_probe_results) / len(recall_probe_results)
            avg_bl = sum(r["bleu"] for r in recall_probe_results) / len(recall_probe_results)
            self.log(f"   Recall Avg ROUGE-1={avg_r1:.3f}  BLEU={avg_bl:.3f}", "INFO", "system")
        correct = sum(1 for r in results if r.get("is_correct_topic", False))
        incorrect = len(results) - correct
        self.log(f"   ✅ Correct: {correct}", "INFO", "system")
        self.log(f"   ❌ Incorrect: {incorrect}", "INFO", "system")
        if results:
            self.log(f"   Accuracy: {(correct / len(results) * 100):.1f}%", "INFO", "system")
        self.log(f"   🔍 Retrieval Rate: {retrieval_rate:.1f}% ({rag_triggered}/{len(results)} steps triggered RAG)", "INFO", "system")
        self.log("="*80, "INFO", "system")
        
        return results

    # =========================================================================
    # RECALL PROBES: ROUGE/BLEU Scoring for Topic-Specific Context Retention
    # Probes are now embedded directly in the scenario JSON as is_recall_probe steps.
    # Detection & scoring happens inline in run_baseline_test() and run_system_test().
    # =========================================================================

    def _build_recall_reference(self, probe_topic: str, topic_responses: Dict[str, list]) -> str:
        """
        Build the reference text for recall scoring from real user questions + AI responses
        collected during the test run.
        
        Args:
            probe_topic: The topic being probed
            topic_responses: {topic: [(user_msg, ai_response), ...]} collected during test
            
        Returns:
            Combined reference string of user questions and real AI responses
        """
        if probe_topic not in topic_responses or not topic_responses[probe_topic]:
            self.log(f"  ⚠️ No collected responses for topic '{probe_topic}'", "WARN")
            return ""
        
        parts = []
        for user_msg, ai_resp in topic_responses[probe_topic]:
            parts.append(f"User: {user_msg}")
            parts.append(f"Assistant: {ai_resp}")
        
        return " ".join(parts)

    def _compute_recall_scores(self, summary: str, reference: str) -> Dict[str, float]:
        """
        Compute ROUGE-1, ROUGE-L, and BLEU scores between LLM summary and reference.
        
        Args:
            summary: The LLM-generated summary of a topic
            reference: The combined user questions + real AI responses for that topic
            
        Returns:
            Dict with rouge1_f, rougeL_f, bleu scores (0-1 scale)
        """
        scores = {"rouge1_f": 0.0, "rougeL_f": 0.0, "bleu": 0.0}
        
        if not summary or not reference:
            return scores
        
        # ROUGE scores
        if ROUGE_AVAILABLE:
            try:
                scorer = rouge_scorer_module.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
                rouge_results = scorer.score(reference, summary)
                scores["rouge1_f"] = rouge_results['rouge1'].fmeasure
                scores["rougeL_f"] = rouge_results['rougeL'].fmeasure
            except Exception as e:
                self.log(f"  ⚠️ ROUGE scoring error: {e}", "WARN")
        
        # BLEU score
        if BLEU_AVAILABLE:
            try:
                ref_tokens = reference.lower().split()
                hyp_tokens = summary.lower().split()
                if ref_tokens and hyp_tokens:
                    smoothing = SmoothingFunction().method1
                    scores["bleu"] = sentence_bleu(
                        [ref_tokens], hyp_tokens,
                        weights=(0.5, 0.5, 0, 0),  # BLEU-2 (unigram + bigram)
                        smoothing_function=smoothing
                    )
            except Exception as e:
                self.log(f"  ⚠️ BLEU scoring error: {e}", "WARN")
        
        return scores

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
                    "total_turns": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_tokens": 0,
                    "total_latency": 0,
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
            total_turns = len(results)
            total_input_tokens = sum(r.get("input_tokens", 0) for r in results)
            total_output_tokens = sum(r.get("output_tokens", 0) for r in results)
            total_tokens = sum(r.get("total_tokens", 0) for r in results)
            total_latency = sum(r["latency"] for r in results)
            avg_input = total_input_tokens / total_turns
            avg_output = total_output_tokens / total_turns
            avg_total = total_tokens / total_turns
            avg_latency = total_latency / total_turns
            
            # Calculate tokens per correct answer
            correct_count = sum(1 for r in results if r.get("is_correct_topic", False))
            tokens_per_correct = (total_tokens / correct_count) if correct_count > 0 else 0
            
            # Cost calculation (Groq pricing: input $0.05/1M, output $0.08/1M tokens)
            input_cost = (avg_input / 1_000_000) * 0.05
            output_cost = (avg_output / 1_000_000) * 0.08
            cost_per_query = input_cost + output_cost
            cost_per_1m = cost_per_query * 1_000_000
            
            return {
                "total_turns": total_turns,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_tokens,
                "total_latency": total_latency,
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
        
        # Calculate retrieval rate metrics
        def calc_retrieval_rate(results):
            """Calculate RAG decision breakdown across all turns"""
            total = len(results)
            rag_triggered = sum(1 for r in results if r.get("rag_decision") == "search_triggered")
            buffer_sufficient = sum(1 for r in results if r.get("rag_decision") == "no_retrieval_needed")
            disabled = sum(1 for r in results if r.get("rag_decision") == "disabled")
            errors = sum(1 for r in results if str(r.get("rag_decision", "")).startswith("error:"))
            no_vector = sum(1 for r in results if r.get("rag_decision") == "no_vector_index")
            rag_eligible = rag_triggered + buffer_sufficient  # turns where Phase 1 actually ran
            retrieval_rate = (rag_triggered / rag_eligible * 100) if rag_eligible > 0 else 0
            buffer_rate = (buffer_sufficient / rag_eligible * 100) if rag_eligible > 0 else 0
            return {
                "total_turns": total,
                "rag_eligible": rag_eligible,
                "rag_triggered": rag_triggered,
                "buffer_sufficient": buffer_sufficient,
                "rag_disabled": disabled,
                "errors": errors,
                "no_vector_index": no_vector,
                "retrieval_rate": retrieval_rate,
                "buffer_rate": buffer_rate,
            }
        
        baseline_retrieval = calc_retrieval_rate(baseline_results)
        system_retrieval = calc_retrieval_rate(system_results)
        
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
            },
            "retrieval": {
                "baseline": baseline_retrieval,
                "system": system_retrieval
            }
        }

    def _calculate_recall_metrics(
        self,
        baseline_probes: List[Dict],
        system_probes: List[Dict]
    ) -> Dict:
        """
        Aggregate per-topic recall probe results into summary metrics.
        
        Returns dict with baseline/system averages and per-topic breakdown,
        plus improvement calculations.
        """
        def _aggregate_probes(probes: List[Dict]) -> Dict:
            if not probes:
                return {
                    "avg_rouge1": 0.0, "avg_rougeL": 0.0, "avg_bleu": 0.0,
                    "num_topics_probed": 0, "total_probe_tokens": 0,
                    "avg_probe_tokens": 0.0, "total_probe_latency": 0.0,
                    "avg_probe_latency": 0.0, "rag_triggered": 0,
                    "buffer_sufficient": 0, "rag_eligible": 0,
                    "retrieval_rate": 0.0, "buffer_rate": 0.0,
                    "rag_disabled": 0, "errors": 0, "per_topic": {}
                }
            
            per_topic = {}
            for p in probes:
                topic = p["topic"]
                per_topic[topic] = {
                    "rouge1_f": p["rouge1_f"],
                    "rougeL_f": p["rougeL_f"],
                    "bleu": p["bleu"],
                    "summary_length": p["summary_length"],
                    "reference_length": p["reference_length"],
                    "probe_tokens": p.get("probe_tokens", 0),
                    "probe_latency": p.get("probe_latency", 0.0),
                    "rag_used": p.get("rag_used", False),
                    "rag_decision": p.get("rag_decision", "unknown")
                }
            
            n = len(probes)
            total_probe_tokens = sum(p.get("probe_tokens", 0) for p in probes)
            total_probe_latency = sum(p.get("probe_latency", 0.0) for p in probes)
            rag_triggered = sum(1 for p in probes if p.get("rag_decision") == "search_triggered" or p.get("rag_used", False))
            buffer_sufficient = sum(1 for p in probes if p.get("rag_decision") == "no_retrieval_needed")
            rag_disabled = sum(1 for p in probes if p.get("rag_decision") == "disabled")
            errors = sum(1 for p in probes if str(p.get("rag_decision", "")).startswith("error:"))
            rag_eligible = rag_triggered + buffer_sufficient
            return {
                "avg_rouge1": sum(p["rouge1_f"] for p in probes) / n,
                "avg_rougeL": sum(p["rougeL_f"] for p in probes) / n,
                "avg_bleu": sum(p["bleu"] for p in probes) / n,
                "num_topics_probed": n,
                "total_probe_tokens": total_probe_tokens,
                "avg_probe_tokens": total_probe_tokens / n,
                "total_probe_latency": total_probe_latency,
                "avg_probe_latency": total_probe_latency / n,
                "rag_triggered": rag_triggered,
                "buffer_sufficient": buffer_sufficient,
                "rag_eligible": rag_eligible,
                "retrieval_rate": (rag_triggered / rag_eligible * 100) if rag_eligible > 0 else 0,
                "buffer_rate": (buffer_sufficient / rag_eligible * 100) if rag_eligible > 0 else 0,
                "rag_disabled": rag_disabled,
                "errors": errors,
                "per_topic": per_topic
            }
        
        baseline_agg = _aggregate_probes(baseline_probes)
        system_agg = _aggregate_probes(system_probes)
        
        # Calculate improvements
        def _safe_improvement(baseline_val, system_val):
            if baseline_val == 0:
                return 0.0 if system_val == 0 else float('inf')
            return ((system_val - baseline_val) / baseline_val) * 100
        
        improvements = {}
        for metric_key in ["avg_rouge1", "avg_rougeL", "avg_bleu"]:
            improvements[metric_key] = _safe_improvement(
                baseline_agg[metric_key], system_agg[metric_key]
            )
        
        return {
            "baseline": baseline_agg,
            "system": system_agg,
            "improvements": improvements
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
            cost_delta = s['cost_per_1m_queries'] - b['cost_per_1m_queries']
            f.write(f"| **Cost per 1M Queries** | ${b['cost_per_1m_queries']:.0f} | ${s['cost_per_1m_queries']:.0f} | **${cost_delta:+.0f} ({imp['cost_per_1m_queries']:+.1f}%)** |\n")
            
            # Include recall/summarization probes as a separate operational-cost section.
            # These probes are not topic-prefix classification turns, so Table 1 remains unchanged.
            table2 = metrics.get("table_2", {})
            bl_probe = table2.get("baseline", {}) if table2 else {}
            sy_probe = table2.get("system", {}) if table2 else {}
            if bl_probe.get("num_topics_probed", 0) > 0 or sy_probe.get("num_topics_probed", 0) > 0:
                b_probe_tokens = bl_probe.get("total_probe_tokens", 0)
                s_probe_tokens = sy_probe.get("total_probe_tokens", 0)
                b_probe_count = bl_probe.get("num_topics_probed", 0)
                s_probe_count = sy_probe.get("num_topics_probed", 0)
                b_combined_calls = b.get("total_turns", 0) + b_probe_count
                s_combined_calls = s.get("total_turns", 0) + s_probe_count
                b_combined_tokens = b.get("total_tokens", 0) + b_probe_tokens
                s_combined_tokens = s.get("total_tokens", 0) + s_probe_tokens
                b_combined_avg = b_combined_tokens / b_combined_calls if b_combined_calls else 0
                s_combined_avg = s_combined_tokens / s_combined_calls if s_combined_calls else 0
                probe_token_delta = ((s_probe_tokens - b_probe_tokens) / b_probe_tokens * 100) if b_probe_tokens else 0
                combined_token_delta = ((s_combined_tokens - b_combined_tokens) / b_combined_tokens * 100) if b_combined_tokens else 0
                combined_avg_delta = ((s_combined_avg - b_combined_avg) / b_combined_avg * 100) if b_combined_avg else 0
                
                f.write("\n## Including Recall/Summarization Probes\n\n")
                f.write("Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.\n\n")
                f.write("| Metric | Baseline System | Our System | Difference |\n")
                f.write("|--------|----------------|------------|------------|\n")
                f.write(f"| **Normal Conversation Turns** | {b.get('total_turns', 0)} | {s.get('total_turns', 0)} | - |\n")
                f.write(f"| **Normal Conversation Total Tokens** | {b.get('total_tokens', 0):.0f} | {s.get('total_tokens', 0):.0f} | **{imp['avg_total_tokens']:+.1f}% avg/turn** |\n")
                f.write(f"| **Summarization Probe Calls** | {b_probe_count} | {s_probe_count} | - |\n")
                f.write(f"| **Summarization Probe Tokens** | {b_probe_tokens:.0f} | {s_probe_tokens:.0f} | **{probe_token_delta:+.1f}%** |\n")
                f.write(f"| **Avg Tokens per Summarization Probe** | {bl_probe.get('avg_probe_tokens', 0):.0f} | {sy_probe.get('avg_probe_tokens', 0):.0f} | - |\n")
                f.write(f"| **Combined Evaluated Calls** | {b_combined_calls} | {s_combined_calls} | - |\n")
                f.write(f"| **Combined Total Tokens** | {b_combined_tokens:.0f} | {s_combined_tokens:.0f} | **{combined_token_delta:+.1f}%** |\n")
                f.write(f"| **Combined Avg Tokens per Call** | {b_combined_avg:.0f} | {s_combined_avg:.0f} | **{combined_avg_delta:+.1f}%** |\n")
        
        self.log(f"✅ Generated TABLE_3_SYSTEM_PERFORMANCE.md", "INFO")
        
        # TABLE 2: RECALL PROBE SCORES (ROUGE/BLEU)
        table2 = metrics.get("table_2")
        if table2 and (table2.get("baseline", {}).get("num_topics_probed", 0) > 0 or
                       table2.get("system", {}).get("num_topics_probed", 0) > 0):
            with open(buffer_dir / "TABLE_2_RECALL_SCORES.md", 'w') as f:
                f.write(f"# TABLE 2: TOPIC RECALL SCORES (Buffer Size: {self.current_buffer_size})\n\n")
                f.write("Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.\n")
                f.write("Higher scores indicate better recall of topic content from conversation history.\n\n")
                
                f.write("## Aggregate Scores\n\n")
                f.write("| Metric | Baseline System | Our System | Improvement |\n")
                f.write("|--------|----------------|------------|-------------|\n")
                
                bl = table2.get("baseline", {})
                sy = table2.get("system", {})
                imp = table2.get("improvements", {})
                
                for metric_key, display_name in [
                    ("avg_rouge1", "Avg ROUGE-1 (F1)"),
                    ("avg_rougeL", "Avg ROUGE-L (F1)"),
                    ("avg_bleu", "Avg BLEU-2")
                ]:
                    bl_val = bl.get(metric_key, 0)
                    sy_val = sy.get(metric_key, 0)
                    imp_val = imp.get(metric_key, 0)
                    if isinstance(imp_val, float) and imp_val == float('inf'):
                        imp_str = "**∞**"
                    else:
                        imp_str = f"**{imp_val:+.1f}%**"
                    f.write(f"| **{display_name}** | {bl_val:.4f} | {sy_val:.4f} | {imp_str} |\n")
                
                f.write(f"\n## Summarization Probe Cost\n\n")
                f.write("| Metric | Baseline System | Our System | Difference |\n")
                f.write("|--------|----------------|------------|------------|\n")
                f.write(f"| **Topics Probed** | {bl.get('num_topics_probed', 0)} | {sy.get('num_topics_probed', 0)} | - |\n")
                f.write(f"| **Total Probe Tokens** | {bl.get('total_probe_tokens', 0)} | {sy.get('total_probe_tokens', 0)} | - |\n")
                f.write(f"| **Avg Tokens per Probe** | {bl.get('avg_probe_tokens', 0):.0f} | {sy.get('avg_probe_tokens', 0):.0f} | - |\n")
                f.write(f"| **Total Probe Latency** | {bl.get('total_probe_latency', 0):.1f}s | {sy.get('total_probe_latency', 0):.1f}s | - |\n")
                f.write(f"| **Avg Probe Latency** | {bl.get('avg_probe_latency', 0):.2f}s | {sy.get('avg_probe_latency', 0):.2f}s | - |\n")
                
                # Per-topic breakdown (side-by-side)
                f.write(f"\n## Per-Topic Breakdown\n\n")
                f.write("| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |\n")
                f.write("|-------|-----------|------------|-----------|------------|---------|--------|\n")
                
                bl_topics = bl.get("per_topic", {})
                sy_topics = sy.get("per_topic", {})
                all_probe_topics = sorted(set(list(bl_topics.keys()) + list(sy_topics.keys())))
                
                for topic in all_probe_topics:
                    bl_t = bl_topics.get(topic, {})
                    sy_t = sy_topics.get(topic, {})
                    f.write(f"| {topic} ")
                    f.write(f"| {bl_t.get('rouge1_f', 0):.4f} | {sy_t.get('rouge1_f', 0):.4f} ")
                    f.write(f"| {bl_t.get('rougeL_f', 0):.4f} | {sy_t.get('rougeL_f', 0):.4f} ")
                    f.write(f"| {bl_t.get('bleu', 0):.4f} | {sy_t.get('bleu', 0):.4f} |\n")
                
                # Topic winners summary
                f.write(f"\n## Topic Winners (System vs Baseline)\n\n")
                system_wins = 0
                baseline_wins = 0
                ties = 0
                for topic in all_probe_topics:
                    bl_r1 = bl_topics.get(topic, {}).get("rouge1_f", 0)
                    sy_r1 = sy_topics.get(topic, {}).get("rouge1_f", 0)
                    if sy_r1 > bl_r1 + 0.01:  # 0.01 threshold for meaningful win
                        system_wins += 1
                    elif bl_r1 > sy_r1 + 0.01:
                        baseline_wins += 1
                    else:
                        ties += 1
                
                f.write(f"- 🟢 **System wins**: {system_wins} topics\n")
                f.write(f"- 🔵 **Baseline wins**: {baseline_wins} topics\n")
                f.write(f"- 🟡 **Ties (±0.01)**: {ties} topics\n")
            
            self.log(f"✅ Generated TABLE_2_RECALL_SCORES.md", "INFO")
        else:
            self.log(f"ℹ️ Skipping TABLE_2 (no recall probe data available)", "INFO")
        
        # TABLE 4: RAG DECISION BREAKDOWN
        retrieval = metrics.get("retrieval")
        if retrieval:
            with open(buffer_dir / "TABLE_4_RAG_DECISIONS.md", 'w') as f:
                f.write(f"# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: {self.current_buffer_size})\n\n")
                f.write("Shows how the LLM's Phase 1 JSON decision split across all turns.\n")
                f.write("**RAG Triggered** = LLM decided archived context was needed.\n")
                f.write("**Buffer Sufficient** = LLM decided recent buffer had enough info.\n\n")
                
                bl = retrieval.get("baseline", {})
                sy = retrieval.get("system", {})
                
                f.write("| Metric | Baseline | System |\n")
                f.write("|--------|----------|--------|\n")
                f.write(f"| **Total Turns** | {bl.get('total_turns', 0)} | {sy.get('total_turns', 0)} |\n")
                f.write(f"| **RAG-Eligible Turns** | {bl.get('rag_eligible', 0)} | {sy.get('rag_eligible', 0)} |\n")
                f.write(f"| **RAG Triggered** | {bl.get('rag_triggered', 0)} | {sy.get('rag_triggered', 0)} |\n")
                f.write(f"| **Buffer Sufficient** | {bl.get('buffer_sufficient', 0)} | {sy.get('buffer_sufficient', 0)} |\n")
                f.write(f"| **Retrieval Rate** | {bl.get('retrieval_rate', 0):.1f}% | {sy.get('retrieval_rate', 0):.1f}% |\n")
                f.write(f"| **Buffer Rate** | {bl.get('buffer_rate', 0):.1f}% | {sy.get('buffer_rate', 0):.1f}% |\n")
                if bl.get('errors', 0) > 0 or sy.get('errors', 0) > 0:
                    f.write(f"| **Errors** | {bl.get('errors', 0)} | {sy.get('errors', 0)} |\n")
                if bl.get('rag_disabled', 0) > 0 or sy.get('rag_disabled', 0) > 0:
                    f.write(f"| **RAG Disabled** | {bl.get('rag_disabled', 0)} | {sy.get('rag_disabled', 0)} |\n")
                
                table2 = metrics.get("table_2", {})
                bl_probe = table2.get("baseline", {}) if table2 else {}
                sy_probe = table2.get("system", {}) if table2 else {}
                if bl_probe.get("num_topics_probed", 0) > 0 or sy_probe.get("num_topics_probed", 0) > 0:
                    f.write("\n## Recall/Summarization Probe RAG Decisions\n\n")
                    f.write("These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.\n\n")
                    f.write("| Metric | Baseline | System |\n")
                    f.write("|--------|----------|--------|\n")
                    f.write(f"| **Probe Turns** | {bl_probe.get('num_topics_probed', 0)} | {sy_probe.get('num_topics_probed', 0)} |\n")
                    f.write(f"| **RAG-Eligible Probe Turns** | {bl_probe.get('rag_eligible', 0)} | {sy_probe.get('rag_eligible', 0)} |\n")
                    f.write(f"| **Probe RAG Triggered** | {bl_probe.get('rag_triggered', 0)} | {sy_probe.get('rag_triggered', 0)} |\n")
                    f.write(f"| **Probe Buffer Sufficient** | {bl_probe.get('buffer_sufficient', 0)} | {sy_probe.get('buffer_sufficient', 0)} |\n")
                    f.write(f"| **Probe Retrieval Rate** | {bl_probe.get('retrieval_rate', 0):.1f}% | {sy_probe.get('retrieval_rate', 0):.1f}% |\n")
                    f.write(f"| **Probe Buffer Rate** | {bl_probe.get('buffer_rate', 0):.1f}% | {sy_probe.get('buffer_rate', 0):.1f}% |\n")
                    if bl_probe.get('errors', 0) > 0 or sy_probe.get('errors', 0) > 0:
                        f.write(f"| **Probe Errors** | {bl_probe.get('errors', 0)} | {sy_probe.get('errors', 0)} |\n")
            
            self.log(f"✅ Generated TABLE_4_RAG_DECISIONS.md", "INFO")

    def git_commit_and_push(self, files_to_add: List[str], commit_message: str) -> tuple:
        """Git push disabled - output is saved directly on Kaggle."""
        self.log("ℹ️  Git push disabled (output saved on Kaggle)", "INFO")
        return True, "Push disabled"

    def push_buffer_results(self, buffer_size: int) -> bool:
        """Git push disabled - output is saved directly on Kaggle."""
        self.log(f"ℹ️  Skipping push for buffer {buffer_size} (output saved on Kaggle)", "INFO")
        return True
        
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
        all_baseline_probe_results = []
        all_system_probe_results = []
        
        for scenario_file in scenario_files:
            scenario = self.load_scenario(scenario_file)
            if not scenario:
                continue
            
            # Check if scenario has embedded recall probes
            probe_count = sum(1 for s in scenario.get("conversations", []) if s.get("is_recall_probe"))
            self.log(f"  📋 Embedded recall probes: {probe_count}", "INFO")
            
            # BASELINE TEST (only if mode is 'baseline' or 'both')
            if test_mode in ['baseline', 'both']:
                self.log(f"\n🔵 BASELINE TEST: {scenario_file}", "INFO")
                self.clear_state()
                baseline_results = self.run_baseline_test(scenario, buffer_size=buffer_size)
                all_baseline_results.extend(baseline_results)
                
                # Collect inline recall probe results (stored by run_baseline_test)
                baseline_probes = getattr(self, '_last_baseline_recall_probes', [])
                all_baseline_probe_results.extend(baseline_probes)
            
            # SYSTEM TEST (only if mode is 'system' or 'both')
            if test_mode in ['system', 'both']:
                self.log(f"\n🟢 SYSTEM TEST: {scenario_file}", "INFO")
                self.clear_state()
                system_results = self.run_system_test(scenario, buffer_size=buffer_size)
                all_system_results.extend(system_results)
                
                # Collect inline recall probe results (stored by run_system_test)
                system_probes = getattr(self, '_last_system_recall_probes', [])
                all_system_probe_results.extend(system_probes)
        
        # Calculate metrics (including recall probes)
        self.log("\n📊 Calculating metrics...", "INFO")
        metrics = self.calculate_metrics(all_baseline_results, all_system_results)
        
        # Add recall probe metrics to the metrics dict
        recall_metrics = self._calculate_recall_metrics(
            all_baseline_probe_results, all_system_probe_results
        )
        metrics["table_2"] = recall_metrics
        
        # Print summary
        self.log("\n" + "="*80, "INFO")
        self.log("📊 FINAL METRICS COMPARISON", "INFO")
        self.log("="*80, "INFO")
        
        iso_baseline = metrics["table_1"]["baseline"]
        iso_system = metrics["table_1"]["system"]
        
        self.log(f"\n🔵 BASELINE: Accuracy={iso_baseline['accuracy']:.1f}%, Pollution={iso_baseline['pollution_rate']:.1f}%", "INFO")
        self.log(f"🟢 SYSTEM:   Accuracy={iso_system['accuracy']:.1f}%, Pollution={iso_system['pollution_rate']:.1f}%", "INFO")
        
        # Print recall probe summary
        if recall_metrics.get("baseline") and recall_metrics.get("system"):
            bl_r = recall_metrics["baseline"]
            sy_r = recall_metrics["system"]
            self.log(f"\n🔬 RECALL PROBES:", "INFO")
            self.log(f"🔵 BASELINE: ROUGE-1={bl_r['avg_rouge1']:.3f}  ROUGE-L={bl_r['avg_rougeL']:.3f}  BLEU={bl_r['avg_bleu']:.3f}", "INFO")
            self.log(f"🟢 SYSTEM:   ROUGE-1={sy_r['avg_rouge1']:.3f}  ROUGE-L={sy_r['avg_rougeL']:.3f}  BLEU={sy_r['avg_bleu']:.3f}", "INFO")
        
        # Generate tables
        self.generate_table(metrics)
        
        # Save raw results
        buffer_dir = self.base_logs_dir / "tables" / f"buffer_{self.current_buffer_size}"
        buffer_dir.mkdir(parents=True, exist_ok=True)
        
        with open(buffer_dir / "raw_metrics_baseline.json", 'w') as f:
            json.dump(all_baseline_results, f, indent=2)
        with open(buffer_dir / "raw_metrics_system.json", 'w') as f:
            json.dump(all_system_results, f, indent=2)
        with open(buffer_dir / "raw_recall_probes_baseline.json", 'w') as f:
            json.dump(all_baseline_probe_results, f, indent=2)
        with open(buffer_dir / "raw_recall_probes_system.json", 'w') as f:
            json.dump(all_system_probe_results, f, indent=2)
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
        
        # Extract recall probe metrics (safely, may not exist for all buffer sizes)
        baseline_rouge1 = [all_metrics[bs].get("table_2", {}).get("baseline", {}).get("avg_rouge1", 0) for bs in buffer_sizes]
        system_rouge1 = [all_metrics[bs].get("table_2", {}).get("system", {}).get("avg_rouge1", 0) for bs in buffer_sizes]
        baseline_rougeL = [all_metrics[bs].get("table_2", {}).get("baseline", {}).get("avg_rougeL", 0) for bs in buffer_sizes]
        system_rougeL = [all_metrics[bs].get("table_2", {}).get("system", {}).get("avg_rougeL", 0) for bs in buffer_sizes]
        baseline_bleu = [all_metrics[bs].get("table_2", {}).get("baseline", {}).get("avg_bleu", 0) for bs in buffer_sizes]
        system_bleu = [all_metrics[bs].get("table_2", {}).get("system", {}).get("avg_bleu", 0) for bs in buffer_sizes]
        has_recall_data = any(v > 0 for v in baseline_rouge1 + system_rouge1)
        
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
        
        {'<h2>🔬 Topic Recall Scores (ROUGE/BLEU)</h2>' if has_recall_data else ''}
        
        {'<div class="chart-container"><canvas id="rouge1Chart"></canvas></div>' if has_recall_data else ''}
        {'<div class="chart-container"><canvas id="rougeLChart"></canvas></div>' if has_recall_data else ''}
        {'<div class="chart-container"><canvas id="bleuChart"></canvas></div>' if has_recall_data else ''}
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
        
        // Recall Probe Charts (only if data available)
        const baselineRouge1 = {json.dumps(baseline_rouge1)};
        const systemRouge1 = {json.dumps(system_rouge1)};
        const baselineRougeL = {json.dumps(baseline_rougeL)};
        const systemRougeL = {json.dumps(system_rougeL)};
        const baselineBleu = {json.dumps(baseline_bleu)};
        const systemBleu = {json.dumps(system_bleu)};
        
        if (baselineRouge1.some(v => v > 0) || systemRouge1.some(v => v > 0)) {{
            new Chart(document.getElementById('rouge1Chart'), {{
                type: 'line',
                data: {{
                    labels: bufferSizes,
                    datasets: [{{
                        label: 'Baseline ROUGE-1',
                        data: baselineRouge1,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    }}, {{
                        label: 'System ROUGE-1',
                        data: systemRouge1,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    }}]
                }},
                options: {{
                    ...chartOptions,
                    plugins: {{
                        ...chartOptions.plugins,
                        title: {{ display: true, text: 'ROUGE-1 (F1) vs Buffer Size - Higher is Better' }}
                    }}
                }}
            }});
            
            new Chart(document.getElementById('rougeLChart'), {{
                type: 'line',
                data: {{
                    labels: bufferSizes,
                    datasets: [{{
                        label: 'Baseline ROUGE-L',
                        data: baselineRougeL,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    }}, {{
                        label: 'System ROUGE-L',
                        data: systemRougeL,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    }}]
                }},
                options: {{
                    ...chartOptions,
                    plugins: {{
                        ...chartOptions.plugins,
                        title: {{ display: true, text: 'ROUGE-L (F1) vs Buffer Size - Higher is Better' }}
                    }}
                }}
            }});
            
            new Chart(document.getElementById('bleuChart'), {{
                type: 'line',
                data: {{
                    labels: bufferSizes,
                    datasets: [{{
                        label: 'Baseline BLEU-2',
                        data: baselineBleu,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    }}, {{
                        label: 'System BLEU-2',
                        data: systemBleu,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    }}]
                }},
                options: {{
                    ...chartOptions,
                    plugins: {{
                        ...chartOptions.plugins,
                        title: {{ display: true, text: 'BLEU-2 Score vs Buffer Size - Higher is Better' }}
                    }}
                }}
            }});
        }}
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
            
            self.log(f"\n✅ Completed buffer size {buffer_size}", "INFO")
        
        # Generate comparison visualization
        self.log("\n📊 Generating final comparison visualization...", "INFO")
        self.generate_comparison_visualization(all_metrics)
        
        self.log("\n🎉 KAGGLE SERVERLESS MULTI-BUFFER COMPARISON COMPLETE!", "INFO")
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
