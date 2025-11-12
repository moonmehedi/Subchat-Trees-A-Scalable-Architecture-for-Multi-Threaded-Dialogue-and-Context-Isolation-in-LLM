"""
Test script to verify cross-encoder re-ranking is working.
This will show BEFORE and AFTER re-ranking to prove scores change.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.reranker import get_reranker
import chromadb
from chromadb.config import Settings
import time


def test_reranker_changes_scores():
    """
    Test that the cross-encoder re-ranker actually changes the order
    and scores of retrieved documents.
    """
    print("="*80)
    print("CROSS-ENCODER RE-RANKING TEST")
    print("="*80)
    
    # Initialize re-ranker
    print("\n🔄 Loading cross-encoder re-ranker...")
    reranker = get_reranker()
    
    if not reranker.enabled:
        print("❌ FAIL: Re-ranker is not enabled!")
        return False
    
    print(f"✅ Re-ranker loaded and enabled")
    
    # Create test documents with varying relevance
    test_documents = [
        {
            "text": "Hi, how are you?",
            "score": 0.8,
            "metadata": {"role": "user", "timestamp": time.time()}
        },
        {
            "text": "My name is Alice and I'm a software engineer at Google",
            "score": 0.75,
            "metadata": {"role": "user", "timestamp": time.time() + 1}
        },
        {
            "text": "I work in Mountain View, California",
            "score": 0.7,
            "metadata": {"role": "user", "timestamp": time.time() + 2}
        },
        {
            "text": "The weather is nice today",
            "score": 0.65,
            "metadata": {"role": "user", "timestamp": time.time() + 3}
        },
        {
            "text": "Python is a programming language",
            "score": 0.6,
            "metadata": {"role": "assistant", "timestamp": time.time() + 4}
        }
    ]
    
    # Query that should rank Alice's introduction highly
    query = "What is my name and where do I work?"
    
    print(f"\n🔍 Query: '{query}'")
    print(f"📊 Initial documents (by ChromaDB similarity):")
    
    for i, doc in enumerate(test_documents, 1):
        print(f"   {i}. [Score: {doc['score']:.3f}] {doc['text'][:60]}")
    
    # Apply re-ranking
    print(f"\n🔄 Applying cross-encoder re-ranking...")
    reranked = reranker.rerank(query, test_documents, top_k=5)
    
    print(f"\n✅ After re-ranking (top {len(reranked)}):")
    for i, doc in enumerate(reranked, 1):
        print(f"   {i}. [Score: {doc['score']:.3f}] {doc['text'][:60]}")
    
    # Verify that re-ranking changed the order
    original_order = [doc['text'] for doc in test_documents[:5]]
    reranked_order = [doc['text'] for doc in reranked]
    
    if original_order != reranked_order:
        print(f"\n✅ SUCCESS: Re-ranking changed the document order!")
        print(f"   Original top doc: {original_order[0][:40]}...")
        print(f"   Re-ranked top doc: {reranked_order[0][:40]}...")
        return True
    else:
        print(f"\n⚠️  WARNING: Order unchanged (may still have different scores)")
        
        # Check if scores changed even if order didn't
        original_scores = [doc['score'] for doc in test_documents[:5]]
        reranked_scores = [doc['score'] for doc in reranked]
        
        if original_scores != reranked_scores:
            print(f"✅ But scores changed - re-ranker is working!")
            return True
        else:
            print(f"❌ FAIL: Scores and order unchanged!")
            return False


def test_reranker_with_real_query():
    """
    Test re-ranker with a realistic personal information query.
    """
    print("\n" + "="*80)
    print("REAL-WORLD QUERY TEST")
    print("="*80)
    
    reranker = get_reranker()
    
    # Simulate documents from a conversation
    documents = [
        {
            "text": "I'm just a language model, I don't have feelings or emotions like humans do.",
            "score": 0.65,
            "metadata": {"role": "assistant"}
        },
        {
            "text": "hi how are you?",
            "score": 0.60,
            "metadata": {"role": "user"}
        },
        {
            "text": "My name is Moon, I'm 22 years old, I study at MIST and I like cricket",
            "score": 0.55,
            "metadata": {"role": "user"}
        },
        {
            "text": "Nice to meet you, Moon! That's great that you study at MIST.",
            "score": 0.50,
            "metadata": {"role": "assistant"}
        },
        {
            "text": "What is quantum computing?",
            "score": 0.45,
            "metadata": {"role": "user"}
        }
    ]
    
    query = "What is my name and what do I study?"
    
    print(f"\n🔍 Query: '{query}'")
    print(f"\n📊 BEFORE re-ranking:")
    for i, doc in enumerate(documents, 1):
        print(f"   {i}. [Score: {doc['score']:.3f}] [{doc['metadata']['role'].upper()}]")
        print(f"      {doc['text'][:80]}")
    
    # Re-rank
    reranked = reranker.rerank(query, documents, top_k=3)
    
    print(f"\n✅ AFTER re-ranking (top 3):")
    for i, doc in enumerate(reranked, 1):
        print(f"   {i}. [Score: {doc['score']:.3f}] [{doc['metadata']['role'].upper()}]")
        print(f"      {doc['text'][:80]}")
    
    # Check if the user introduction is now top-ranked
    top_doc = reranked[0]['text']
    if "Moon" in top_doc and "MIST" in top_doc:
        print(f"\n✅ SUCCESS: User introduction ranked #1!")
        print(f"   Re-ranker correctly identified the most relevant message.")
        return True
    else:
        print(f"\n❌ FAIL: User introduction not top-ranked")
        print(f"   Top document: {top_doc[:60]}...")
        return False


def test_score_transformation():
    """
    Show how re-ranker transforms scores.
    """
    print("\n" + "="*80)
    print("SCORE TRANSFORMATION TEST")
    print("="*80)
    
    reranker = get_reranker()
    
    # Documents with similar ChromaDB scores
    documents = [
        {
            "text": "The weather is sunny today",
            "score": 0.70,
            "metadata": {"role": "user"}
        },
        {
            "text": "My favorite color is blue and I love painting",
            "score": 0.68,
            "metadata": {"role": "user"}
        },
        {
            "text": "I like pizza for dinner",
            "score": 0.65,
            "metadata": {"role": "user"}
        }
    ]
    
    query = "What is my favorite color?"
    
    print(f"\n🔍 Query: '{query}'")
    print(f"\n📊 ChromaDB scores (similar values):")
    for doc in documents:
        print(f"   Score: {doc['score']:.3f} - {doc['text']}")
    
    # Re-rank
    reranked = reranker.rerank(query, documents, top_k=3)
    
    print(f"\n✅ Cross-encoder scores (differentiated):")
    for doc in reranked:
        print(f"   Score: {doc['score']:.3f} - {doc['text']}")
    
    # Calculate score spread
    chroma_scores = [d['score'] for d in documents]
    reranked_scores = [d['score'] for d in reranked]
    
    chroma_spread = max(chroma_scores) - min(chroma_scores)
    reranked_spread = max(reranked_scores) - min(reranked_scores)
    
    print(f"\n📊 Score spread analysis:")
    print(f"   ChromaDB spread: {chroma_spread:.3f}")
    print(f"   Re-ranked spread: {reranked_spread:.3f}")
    
    # Re-ranker success means it dramatically changes scores
    if reranked_spread > 5.0:  # Large spread indicates good differentiation
        print(f"   ✅ Re-ranker created strong differentiation (spread: {reranked_spread:.1f})")
        return True
    elif reranked_spread > chroma_spread:
        print(f"   ✅ Re-ranker increased score differentiation by {((reranked_spread/chroma_spread - 1) * 100):.1f}%")
        return True
    else:
        print(f"   ⚠️  Re-ranker did not increase differentiation significantly")
        return False


def main():
    """Run all re-ranking tests"""
    print("\n" + "="*80)
    print("🧪 RE-RANKING VERIFICATION TEST SUITE")
    print("="*80)
    print("\nThis test will prove that cross-encoder re-ranking is working")
    print("by showing BEFORE and AFTER scores and document order.\n")
    
    results = []
    
    # Test 1: Basic re-ranking
    try:
        result1 = test_reranker_changes_scores()
        results.append(("Basic Re-ranking", result1))
    except Exception as e:
        print(f"❌ Test 1 failed with error: {e}")
        results.append(("Basic Re-ranking", False))
    
    # Test 2: Real-world query
    try:
        result2 = test_reranker_with_real_query()
        results.append(("Real-world Query", result2))
    except Exception as e:
        print(f"❌ Test 2 failed with error: {e}")
        results.append(("Real-world Query", False))
    
    # Test 3: Score transformation
    try:
        result3 = test_score_transformation()
        results.append(("Score Transformation", result3))
    except Exception as e:
        print(f"❌ Test 3 failed with error: {e}")
        results.append(("Score Transformation", False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS! Re-ranking is working correctly!")
        print("\n📝 What this means:")
        print("   - Cross-encoder re-ranker is loaded and active")
        print("   - Scores are being recalculated based on semantic relevance")
        print("   - Document order changes to prioritize most relevant results")
        print("   - Your RAG system should retrieve better context!")
    elif passed > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {passed}/{total} tests passed")
        print("   Re-ranker is working but may need tuning")
    else:
        print("\n❌ FAILURE: Re-ranking is not working")
        print("\n🔧 Possible issues:")
        print("   - Re-ranker model not loaded")
        print("   - Model path incorrect")
        print("   - Dependencies missing")
    
    print("="*80)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
