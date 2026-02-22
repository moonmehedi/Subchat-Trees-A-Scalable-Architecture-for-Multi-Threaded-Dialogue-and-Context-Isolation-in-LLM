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
        
        # File paths - append mode uses _full suffix in filename (same directory)
        suffix = "_full" if append_mode else ""
        self.vector_store_log = self.log_dir / f"VECTOR_STORE{suffix}.log"
        self.retrieval_log = self.log_dir / f"RETRIEVAL{suffix}.log"
        self.buffer_log = self.log_dir / f"BUFFER{suffix}.log"
        self.cot_thinking_log = self.log_dir / f"COT_THINKING{suffix}.log"
        self.rag_pipeline_log = self.log_dir / f"RAG_PIPELINE{suffix}.log"
    
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
                # Get conversation title from first message metadata
                conversation_title = messages[0]['metadata'].get('conversation_title', 'Untitled') if messages else 'Untitled'
                
                f.write(f"\n{'='*80}\n")
                f.write(f"🗂️  Conversation: {node_id} ({len(messages)} messages) - {conversation_title}\n")
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
    
    def log_buffer(self, node_id: str, buffer_messages: List[Dict[str, Any]], max_turns: int, summary: str = "", conversation_title: str = "Untitled"):
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
            f.write(f"💬 TITLE: {conversation_title}\n")
            f.write(f"📊 BUFFER SIZE: {len(buffer_messages)}/{max_turns}\n")
            
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

    def log_rag_pipeline(
        self,
        query: str,
        decision_messages: List[Dict[str, Any]],
        raw_llm_output: str,
        retrieve: bool,
        search_query: Optional[str],
        sub_queries: Optional[List[str]] = None,
        sub_query_results: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        final_results: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Single unified log for the ENTIRE RAG pipeline:
          Phase 1 decision (input messages, raw LLM JSON, parsed result)
          + Phase 2 retrieval (sub-queries, per-query results, re-ranked finals)
        All text shown in full — no truncation.
        """
        mode = 'a' if self.append_mode else 'w'
        with open(self.rag_pipeline_log, mode, encoding='utf-8') as f:
            if self.append_mode:
                f.write("\n" + "="*80 + "\n")
                f.write("NEW ENTRY\n")
                f.write("="*80 + "\n")

            f.write("="*80 + "\n")
            f.write(f"RAG PIPELINE RUN\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")

            # ── USER QUERY ──────────────────────────────────────────────────
            f.write("❓ USER QUERY:\n")
            f.write(f"{query}\n\n")

            # ── PHASE 1: DECISION ────────────────────────────────────────────
            f.write("="*80 + "\n")
            f.write("PHASE 1 — RETRIEVAL DECISION\n")
            f.write("="*80 + "\n\n")

            f.write(f"📨 INPUT MESSAGES FED TO DECISION LLM ({len(decision_messages)} messages):\n")
            f.write("-"*60 + "\n")
            for i, msg in enumerate(decision_messages):
                role = msg.get('role', '?').upper()
                content = msg.get('content', '')
                f.write(f"[{i}] {role}:\n{content}\n")
                f.write("-"*60 + "\n")

            f.write(f"\n📤 RAW LLM OUTPUT:\n")
            f.write(f"{raw_llm_output}\n\n")

            f.write(f"✅ PARSED DECISION:\n")
            f.write(f"  retrieve = {retrieve}\n")
            f.write(f"  search_query = {search_query!r}\n\n")

            # ── PHASE 2: RETRIEVAL ───────────────────────────────────────────
            f.write("="*80 + "\n")
            if retrieve:
                f.write("PHASE 2 — RETRIEVAL EXECUTED\n")
            else:
                f.write("PHASE 2 — NO RETRIEVAL (buffer context sufficient)\n")
            f.write("="*80 + "\n\n")

            if not retrieve or sub_queries is None:
                f.write("ℹ️  No retrieval performed — LLM used buffer context directly.\n")
            else:
                # Sub-queries
                f.write(f"🔍 SEARCH QUERY: {search_query}\n")
                f.write(f"📋 SUB-QUERIES ({len(sub_queries)} generated):\n")
                f.write("-"*60 + "\n")
                for i, sq in enumerate(sub_queries or [], 1):
                    f.write(f"  {i}. {sq}\n")
                f.write("\n")

                # Per sub-query results
                if sub_query_results:
                    f.write("📊 PER SUB-QUERY RESULTS:\n")
                    f.write("="*60 + "\n")
                    for sq, results in (sub_query_results or {}).items():
                        f.write(f"\nSUB-QUERY: {sq}\n")
                        f.write("-"*60 + "\n")
                        if not results:
                            f.write("  (no results)\n")
                        else:
                            for j, r in enumerate(results, 1):
                                score = r.get('score', 0)
                                role = r.get('metadata', {}).get('role', '?').upper()
                                node_id = r.get('metadata', {}).get('node_id', '?')
                                text = r.get('text', '')
                                f.write(f"  {j}. [score={score:.4f}] [{role}] node={node_id}\n")
                                f.write(f"     FULL TEXT:\n     {text}\n")
                                f.write("     " + "-"*56 + "\n")

                # Final re-ranked results
                f.write(f"\n{'='*80}\n")
                f.write(f"✅ FINAL RE-RANKED RESULTS ({len(final_results or [])} messages returned to LLM):\n")
                f.write("="*80 + "\n\n")
                if not final_results:
                    f.write("⚠️  NO RESULTS RETRIEVED\n")
                else:
                    for i, r in enumerate(final_results or [], 1):
                        score = r.get('score', 0)
                        role = r.get('metadata', {}).get('role', '?').upper()
                        node_id = r.get('metadata', {}).get('node_id', '?')
                        turn = r.get('metadata', {}).get('turn_number', '?')
                        text = r.get('text', '')
                        is_anchor = r.get('is_anchor', False)
                        tag = " [ANCHOR]" if is_anchor else " [context]"
                        f.write(f"{i}. [score={score:.4f}] [{role}]{tag}  node={node_id}  turn={turn}\n")
                        f.write(f"   FULL TEXT:\n   {text}\n")
                        f.write("   " + "-"*76 + "\n\n")

            f.write("="*80 + "\n")
            f.write("END OF RAG PIPELINE ENTRY\n")
            f.write("="*80 + "\n")


# Global singleton instances
_debug_logger = None
_debug_logger_append = None
_custom_log_dir = None  # Custom directory for buffer-specific logging


def set_log_directory(log_dir: str):
    """
    Redirect global debug loggers to a custom directory.
    Call this BEFORE any logging operations to use buffer-specific paths.
    
    Args:
        log_dir: Path to the buffer-specific log directory (e.g., "logs/buffer_10")
    
    Both summary and full logs will go to the same directory.
    """
    global _debug_logger, _debug_logger_append, _custom_log_dir
    
    _custom_log_dir = log_dir
    
    # Create new loggers - BOTH go to the same directory
    # Summary logger overwrites files each time
    _debug_logger = DebugLogger(
        log_dir=log_dir,
        append_mode=False
    )
    # Full logger appends to files (uses _full suffix in filenames, not directory)
    _debug_logger_append = DebugLogger(
        log_dir=log_dir,
        append_mode=True
    )


def get_debug_logger(append_mode: bool = False) -> DebugLogger:
    """
    Get or create the debug logger instance.
    
    Args:
        append_mode: If True, use append-only logger (for full debugging)
                    If False, use overwrite logger (for user viewing)
    """
    global _debug_logger, _debug_logger_append, _custom_log_dir
    
    if append_mode:
        if _debug_logger_append is None:
            # Use custom dir if set, otherwise default
            # Note: append_mode=True will add _full suffix to filenames
            log_dir = _custom_log_dir if _custom_log_dir else "./logs/component-testing"
            _debug_logger_append = DebugLogger(
                log_dir=log_dir,
                append_mode=True
            )
        return _debug_logger_append
    else:
        if _debug_logger is None:
            # Use custom dir if set, otherwise default
            log_dir = _custom_log_dir if _custom_log_dir else "./logs/component-testing"
            _debug_logger = DebugLogger(
                log_dir=log_dir,
                append_mode=False
            )
        return _debug_logger
