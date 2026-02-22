#!/usr/bin/env python3
"""
Debug test for RAG pipeline logging.

Runs the full pipeline (buffer overflow → archive → retrieval decision → retrieval)
with mocked LLM responses to verify RAG_PIPELINE.log is written correctly.

Usage:
    cd backend
    python3 -m dataset.debug_rag_pipeline
    # Or with real Groq:
    GROQ_API_KEY=gsk_xxx python3 -m dataset.debug_rag_pipeline
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# ── Environment setup (must happen before any project imports) ────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
USE_REAL_LLM = bool(GROQ_API_KEY) and GROQ_API_KEY != "dummy"

os.environ.setdefault("LLM_BACKEND", "groq")
os.environ.setdefault("GROQ_API_KEY", GROQ_API_KEY or "gsk_dummy_for_mock_testing")
os.environ.setdefault("MODEL_BASE", "llama-3.1-8b-instant")
os.environ.setdefault("VLLM_MODEL_PATH", "/kaggle/input/model")

print("=" * 70)
print("🧪 RAG PIPELINE DEBUG TEST")
print("=" * 70)
print(f"   LLM mode: {'REAL Groq' if USE_REAL_LLM else 'MOCKED (no API key)'}")
print(f"   GROQ_API_KEY: {'set (' + GROQ_API_KEY[:8] + '...)' if GROQ_API_KEY else 'NOT SET → mock mode'}")
print("=" * 70)

# ── Counters for mock responses ───────────────────────────────────────────────
_mock_call_count = 0


def mock_llm_call(messages, max_tokens=500, temperature=0.0):
    """Fake LLM that returns realistic Phase 1 decisions or answers."""
    global _mock_call_count
    _mock_call_count += 1

    # Phase 1 call: max_tokens=80, so return JSON decision
    if max_tokens <= 80:
        # Check if the conversation has enough context to decide retrieval needed
        content_str = " ".join(m.get("content", "") for m in messages)
        if "pizza" in content_str.lower() or "remember" in content_str.lower() or "earlier" in content_str.lower():
            decision = '{"retrieve": true, "query": "pizza preferences earlier conversation"}'
        else:
            decision = '{"retrieve": false}'
        usage = {"prompt_tokens": 150, "completion_tokens": 10, "total_tokens": 160}
        return decision, usage

    # Phase 2 call: answer
    answer = "Based on your earlier conversation, you mentioned you enjoy pepperoni pizza and hate mushrooms."
    usage = {"prompt_tokens": 300, "completion_tokens": 30, "total_tokens": 330}
    return answer, usage


def run_test(log_dir: str):
    """Core test: build a conversation with buffer overflow then trigger retrieval."""
    from src.utils.debug_logger import set_log_directory, get_debug_logger
    from src.services.simple_llm import SimpleLLMClient
    from src.models.tree import TreeNode

    # Point ALL debug loggers at our test log dir
    set_log_directory(log_dir)
    print(f"\n📁 Log directory: {log_dir}")

    # ── Create LLM client with vector index enabled ───────────────────────────
    llm = SimpleLLMClient(enable_vector_index=True)
    print(f"✅ SimpleLLMClient created (vector_index: {llm.vector_index is not None})")
    if llm.vector_index is None:
        print("❌ vector_index is None — RAG disabled! Check GlobalVectorIndex init errors above.")
        return False

    # ── Create the tree node (small buffer so archiving triggers quickly) ─────
    node = TreeNode(
        node_id="debug_node_1",
        title="Pizza Preferences Chat",
        buffer_size=3,        # 3-turn buffer → archiving triggers fast
        llm_client=llm,
    )
    print(f"✅ TreeNode created (buffer_size=3)")

    # ── Patch or use real LLM ─────────────────────────────────────────────────
    patch_target = "src.services.simple_llm.SimpleLLMClient._llm_call"

    def run_pipeline():
        # Build conversation: 4 turns to overflow the 3-turn buffer
        # First 2 turns: establish pizza facts (these will be archived)
        conversation = [
            ("user", "Hi! I love pepperoni pizza and hate mushrooms."),
            ("assistant", "Great to know! Pepperoni and no mushrooms noted."),
            ("user", "Also, my favourite drink is cold lemonade."),
            ("assistant", "Lemonade — noted too!"),
            # These 2 go into buffer after overflow
            ("user", "What's the capital of France?"),
            ("assistant", "Paris is the capital of France."),
        ]

        print("\n── Populating buffer (causes archiving) ──")
        for role, text in conversation:
            node.buffer.add_message(role, text)
            print(f"   + [{role}] {text[:60]}")

        archived = llm.vector_index.collection.count()
        print(f"\n   Vector store now has {archived} archived messages")
        if archived == 0:
            print("   ⚠️  No messages archived yet — buffer may not be full enough")

        # ── Phase 1 & 2: send a recall query ─────────────────────────────────
        recall_query = "Do you remember what I said earlier about pizza?"
        print(f"\n── Sending recall query (should trigger retrieval) ──")
        print(f"   Query: {recall_query}")

        response, rag_meta = llm.generate_response_with_rag(node, recall_query)
        print(f"\n── RAG result ──────────────────────────────────────")
        print(f"   decision : {rag_meta.get('rag_decision')}")
        print(f"   retrieve : {rag_meta.get('rag_used')}")
        print(f"   results  : {rag_meta.get('rag_results_count')}")
        print(f"   response : {str(response)[:120]}")
        return True

    if USE_REAL_LLM:
        print("\n🔗 Using REAL Groq API...\n")
        success = run_pipeline()
    else:
        print("\n🤖 Using MOCKED LLM responses...\n")
        with patch(patch_target, side_effect=mock_llm_call):
            # Also patch the summarizer so buffer overflow doesn't call LLM
            with patch.object(llm, "_summarize_buffer", return_value="Summary of pizza chat"):
                success = run_pipeline()

    return success


def check_logs(log_dir: str):
    """Verify the expected log files exist and have the right content."""
    print("\n" + "=" * 70)
    print("🔍 LOG FILE CHECK")
    print("=" * 70)

    expected = [
        "RAG_PIPELINE.log",
        "RAG_PIPELINE_full.log",
    ]
    found_all = True
    for fname in expected:
        fpath = Path(log_dir) / fname
        if fpath.exists():
            size = fpath.stat().st_size
            print(f"   ✅ {fname}  ({size} bytes)")
        else:
            print(f"   ❌ {fname}  — MISSING")
            found_all = False

    # Print full content of RAG_PIPELINE.log
    rag_log = Path(log_dir) / "RAG_PIPELINE.log"
    if rag_log.exists():
        print("\n" + "=" * 70)
        print("📄 RAG_PIPELINE.log CONTENT:")
        print("=" * 70)
        print(rag_log.read_text(encoding="utf-8"))

        # Basic assertions
        content = rag_log.read_text(encoding="utf-8")
        checks = [
            ("RAG PIPELINE RUN", "header present"),
            ("PHASE 1", "Phase 1 section present"),
            ("PARSED DECISION", "parsed decision present"),
            ("PHASE 2", "Phase 2 section present"),
        ]
        print("── Content assertions ──")
        for needle, desc in checks:
            ok = needle in content
            print(f"   {'✅' if ok else '❌'} {desc}")
            if not ok:
                found_all = False

    print("\n" + "=" * 70)
    print(f"{'✅ All log checks passed!' if found_all else '❌ Some checks FAILED — see above'}")
    print("=" * 70)
    return found_all


def main():
    with tempfile.TemporaryDirectory(prefix="debug_rag_") as log_dir:
        success = run_test(log_dir)
        if success:
            check_logs(log_dir)
        else:
            print("\n⚠️  Pipeline did not complete — fix the errors above first.")


if __name__ == "__main__":
    main()
