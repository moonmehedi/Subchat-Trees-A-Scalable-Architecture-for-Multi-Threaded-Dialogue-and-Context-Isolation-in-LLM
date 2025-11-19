"""
Debug Logger for Component Testing
Writes detailed logs to separate files for easy analysis.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class DebugLogger:
    """
    Writes component logs to separate files for debugging.
    Supports both overwrite and append modes.
    """
    
    def __init__(self, log_dir: str = "./logs/component-testing", append_mode: bool = False):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.append_mode = append_mode  # If True, append instead of overwrite
        
        # File paths
        self.vector_store_log = self.log_dir / "VECTOR_STORE.log"
        self.retrieval_log = self.log_dir / "RETRIEVAL.log"
        self.buffer_log = self.log_dir / "BUFFER.log"
        self.cot_thinking_log = self.log_dir / "COT_THINKING.log"
    
    def log_vector_store(self, messages_by_node: Dict[str, List[Dict[str, Any]]], total_count: int):
        """
        Log all messages in the vector store.
        """
        mode = 'a' if self.append_mode else 'w'
        with open(self.vector_store_log, mode, encoding='utf-8') as f:
            if self.append_mode:
                f.write("\n" + "="*80 + "\n")
                f.write("NEW ENTRY\n")
                f.write("="*80 + "\n")
            
            f.write("="*80 + "\n")
            f.write(f"INDEXED MESSAGES IN VECTOR STORE ({total_count} total)\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            if total_count == 0:
                f.write("📭 Vector store is EMPTY - no messages indexed yet\n")
                return
            
            for node_id, messages in messages_by_node.items():
                f.write(f"\n{'='*80}\n")
                f.write(f"🗂️  Conversation: {node_id} ({len(messages)} messages)\n")
                f.write(f"{'='*80}\n\n")
                
                for i, msg in enumerate(messages, 1):
                    role = msg['metadata'].get('role', 'unknown').upper()
                    timestamp = msg['metadata'].get('timestamp', 0)
                    text = msg['text']
                    
                    f.write(f"{i}. [{role}] @ {timestamp:.2f}\n")
                    f.write(f"   FULL TEXT: {text}\n")
                    f.write(f"   {'-'*76}\n\n")
            
            f.write(f"\n{'='*80}\n")
            f.write(f"✅ Total: {total_count} messages across {len(messages_by_node)} conversations\n")
            f.write(f"{'='*80}\n")
    
    def log_retrieval(
        self,
        query: str,
        intent: str,
        sub_queries: List[str],
        sub_query_results: Dict[str, List[Dict[str, Any]]],  # NEW: detailed results per sub-query
        retrieved_results: List[Dict[str, Any]],
        node_id: Optional[str] = None
    ):
        """
        Log RAG retrieval details including sub-queries and results.
        """
        mode = 'a' if self.append_mode else 'w'
        with open(self.retrieval_log, mode, encoding='utf-8') as f:
            if self.append_mode:
                f.write("\n" + "="*80 + "\n")
                f.write("NEW ENTRY\n")
                f.write("="*80 + "\n")
            
            f.write("="*80 + "\n")
            f.write(f"RETRIEVAL FROM RAG\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"🔍 ORIGINAL QUERY: {query}\n")
            f.write(f"🎯 INTENT CLASSIFICATION: {intent}\n")
            if node_id:
                f.write(f"📍 NODE FILTER: {node_id}\n")
            else:
                f.write(f"📍 NODE FILTER: None (searching ALL conversations)\n")
            f.write(f"\n{'='*80}\n")
            
            # Sub-queries with detailed results
            f.write(f"\n📋 SUB-QUERIES AND THEIR RESULTS ({len(sub_queries)} total):\n")
            f.write(f"{'='*80}\n\n")
            
            for i, sq in enumerate(sub_queries, 1):
                f.write(f"{i}. SUB-QUERY: {sq}\n")
                f.write(f"   {'-'*76}\n")
                
                # Get results for this sub-query
                sq_results = sub_query_results.get(sq, [])
                if sq_results:
                    f.write(f"   ✓ Found {len(sq_results)} results:\n\n")
                    for j, result in enumerate(sq_results, 1):
                        score = result.get('score', 0)
                        text = result.get('text', '')
                        text_preview = text[:100] + ('...' if len(text) > 100 else '')
                        f.write(f"      {j}. [Score: {score:.3f}] {text_preview}\n")
                    f.write(f"\n")
                else:
                    f.write(f"   ✗ No results found\n\n")
            
            # Re-ranking and final selection
            f.write(f"\n{'='*80}\n")
            f.write(f"🎯 RE-RANKING AND FINAL SELECTION:\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Total unique messages from all sub-queries: {len(set(r.get('text', '') for sq_res in sub_query_results.values() for r in sq_res))}\n")
            f.write(f"After deduplication and re-ranking: {len(retrieved_results)} results\n\n")
            
            # Retrieved results
            f.write(f"{'='*80}\n")
            f.write(f"✅ FINAL RETRIEVED RESULTS ({len(retrieved_results)} total):\n")
            f.write(f"{'='*80}\n\n")
            
            if not retrieved_results:
                f.write("⚠️  No results retrieved!\n")
            else:
                for i, result in enumerate(retrieved_results, 1):
                    score = result.get('score', 0)
                    role = result.get('metadata', {}).get('role', 'unknown').upper()
                    conv_id = result.get('metadata', {}).get('node_id', 'unknown')
                    timestamp = result.get('metadata', {}).get('timestamp', 0)
                    text = result.get('text', '')
                    
                    context_tag = " [CONTEXT]" if result.get('from_context_window', False) else ""
                    
                    f.write(f"{i}. [Score: {score:.3f}] [{role}]{context_tag}\n")
                    f.write(f"   Conversation: {conv_id}\n")
                    f.write(f"   Timestamp: {timestamp:.2f}\n")
                    f.write(f"   FULL TEXT:\n")
                    f.write(f"   {text}\n")
                    f.write(f"   {'-'*76}\n\n")
    
    def log_buffer(self, node_id: str, buffer_messages: List[Dict[str, Any]], max_turns: int, summary: str = ""):
        """
        Log all messages currently in the buffer plus rolling summary.
        """
        mode = 'a' if self.append_mode else 'w'
        with open(self.buffer_log, mode, encoding='utf-8') as f:
            if self.append_mode:
                f.write("\n" + "="*80 + "\n")
                f.write("NEW ENTRY\n")
                f.write("="*80 + "\n")
            
            f.write("="*80 + "\n")
            f.write(f"BUFFER MESSAGES\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"📍 NODE: {node_id}\n")
            f.write(f"📊 BUFFER SIZE: {len(buffer_messages)}/{max_turns}\n")
            
            # Add summary section if exists
            if summary:
                f.write(f"\n{'='*80}\n")
                f.write(f"📝 ROLLING SUMMARY ({len(summary)} chars):\n")
                f.write(f"{'='*80}\n")
                f.write(f"{summary}\n")
            
            f.write(f"\n{'='*80}\n")
            f.write(f"ALL BUFFER MESSAGES ({len(buffer_messages)} total):\n")
            f.write(f"{'='*80}\n\n")
            
            if not buffer_messages:
                f.write("📭 Buffer is EMPTY\n")
            else:
                for i, msg in enumerate(buffer_messages, 1):
                    role = msg.get('role', 'unknown').upper()
                    timestamp = msg.get('timestamp', 0)
                    text = msg.get('text', '')
                    
                    f.write(f"{i}. [{role}] @ {timestamp:.2f}\n")
                    f.write(f"   FULL TEXT: {text}\n")
                    f.write(f"   {'-'*76}\n\n")
            
            f.write(f"\n{'='*80}\n")
            f.write(f"✅ Total: {len(buffer_messages)} messages in buffer\n")
            f.write(f"{'='*80}\n")
    
    def log_cot_thinking(
        self,
        query: str,
        reasoning: str,
        decision: str,
        search_query: Optional[str] = None
    ):
        """
        Log LLM's Chain-of-Thought reasoning process.
        """
        mode = 'a' if self.append_mode else 'w'
        with open(self.cot_thinking_log, mode, encoding='utf-8') as f:
            if self.append_mode:
                f.write("\n" + "="*80 + "\n")
                f.write("NEW ENTRY\n")
                f.write("="*80 + "\n")
            
            f.write("="*80 + "\n")
            f.write(f"LLM CHAIN-OF-THOUGHT REASONING\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"❓ USER QUERY:\n")
            f.write(f"{query}\n\n")
            
            f.write(f"{'='*80}\n")
            f.write(f"🧠 LLM REASONING (Scratchpad):\n")
            f.write(f"{'='*80}\n")
            f.write(f"{reasoning}\n\n")
            
            f.write(f"{'='*80}\n")
            f.write(f"✅ FINAL DECISION:\n")
            f.write(f"{'='*80}\n")
            f.write(f"{decision}\n")
            
            if search_query:
                f.write(f"\n🔍 SEARCH QUERY EXTRACTED:\n")
                f.write(f"{search_query}\n")


# Global singleton instances
_debug_logger = None
_debug_logger_append = None

def get_debug_logger(append_mode: bool = False) -> DebugLogger:
    """
    Get or create the debug logger instance.
    
    Args:
        append_mode: If True, use append-only logger (for full debugging)
                    If False, use overwrite logger (for user viewing)
    """
    global _debug_logger, _debug_logger_append
    
    if append_mode:
        if _debug_logger_append is None:
            _debug_logger_append = DebugLogger(
                log_dir="./logs/component-testing-full",
                append_mode=True
            )
        return _debug_logger_append
    else:
        if _debug_logger is None:
            _debug_logger = DebugLogger(
                log_dir="./logs/component-testing",
                append_mode=False
            )
        return _debug_logger
