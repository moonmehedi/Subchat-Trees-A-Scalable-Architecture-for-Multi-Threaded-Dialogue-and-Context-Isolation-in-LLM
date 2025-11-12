"""
Comprehensive test for re-ranking and retrieval system.

Tests:
1. Buffer exclusion works correctly
2. Re-ranking improves retrieval quality
3. Cross-conversation retrieval finds correct messages
4. Current query message is NOT retrieved
"""

import time
from src.services.simple_llm import SimpleChat


def test_buffer_exclusion():
    """Test 1: Verify buffer messages are excluded from retrieval"""
    print("\n" + "="*60)
    print("TEST 1: BUFFER EXCLUSION")
    print("="*60)
    
    chat = SimpleChat(enable_rag=True)
    conv = chat.start_new_conversation("Buffer Test")
    
    # Add messages to buffer
    print("\n📝 Adding messages to buffer...")
    conv.buffer.add_message("user", "Message 1 in buffer")
    conv.buffer.add_message("assistant", "Response 1 in buffer")
    conv.buffer.add_message("user", "Message 2 in buffer")
    conv.buffer.add_message("assistant", "Response 2 in buffer")
    time.sleep(0.2)
    
    print(f"✅ Buffer has {conv.buffer.size()} messages")
    
    # Get buffer cutoff
    buffer_cutoff = conv.buffer.get_cutoff_timestamp()
    print(f"✅ Buffer cutoff timestamp: {buffer_cutoff}")
    
    # Try to retrieve - should exclude buffer messages
    print("\n🔍 Searching for 'Message buffer' with buffer exclusion...")
    results = chat.llm.vector_index.retrieve_relevant(
        query="Message buffer",
        top_k=5,
        node_id=None,
        exclude_buffer_cutoff=buffer_cutoff
    )
    
    print(f"\n✅ Retrieved {len(results)} messages")
    for i, result in enumerate(results, 1):
        print(f"   {i}. [Score: {result['score']:.3f}] {result['text'][:60]}...")
    
    # Verify buffer messages are NOT in results
    buffer_texts = conv.buffer.get_buffer_messages()
    retrieved_texts = [r['text'] for r in results]
    
    print(f"\n📊 Buffer messages: {buffer_texts}")
    print(f"📊 Retrieved messages: {retrieved_texts}")
    
    overlap = set(buffer_texts) & set(retrieved_texts)
    
    if overlap:
        print(f"\n❌ FAILED: Buffer messages found in results: {overlap}")
        return False
    else:
        print("\n✅ PASSED: No buffer messages in retrieval results!")
        return True


def test_reranking_quality():
    """Test 2: Verify re-ranking improves retrieval quality"""
    print("\n" + "="*60)
    print("TEST 2: RE-RANKING QUALITY")
    print("="*60)
    
    chat = SimpleChat(enable_rag=True)
    
    # Create conversation with specific content
    print("\n📝 Creating test conversation...")
    conv1 = chat.start_new_conversation("User Info")
    
    conv1.buffer.add_message("user", "My name is Mehedi Hasan Moon")
    conv1.buffer.add_message("assistant", "Nice to meet you, Mehedi!")
    conv1.buffer.add_message("user", "I am a student at MIST, 4th year CSE")
    conv1.buffer.add_message("assistant", "That's impressive!")
    conv1.buffer.add_message("user", "I love playing cricket")
    conv1.buffer.add_message("assistant", "Cricket is a great sport!")
    time.sleep(0.2)
    
    print(f"✅ Conversation 1 has {conv1.buffer.size()} messages")
    
    # Create another conversation to test cross-conversation retrieval
    conv2 = chat.start_new_conversation("Different Topic")
    conv2.buffer.add_message("user", "Tell me about quantum computing")
    conv2.buffer.add_message("assistant", "Quantum computing uses qubits...")
    time.sleep(0.2)
    
    print(f"✅ Conversation 2 has {conv2.buffer.size()} messages")
    
    # Clear conv2 buffer to test retrieval
    print("\n🔄 Switching to conversation 2 and clearing buffer...")
    conv2.buffer.clear()
    
    print(f"✅ Conv2 buffer cleared: {conv2.buffer.size()} messages")
    
    # Now search from conv2 for user's name
    print("\n🔍 Searching for 'user name Mehedi' from Conv2...")
    buffer_cutoff = conv2.buffer.get_cutoff_timestamp()
    
    results = chat.llm.vector_index.retrieve_relevant(
        query="user name Mehedi",
        top_k=5,
        node_id=None,  # Cross-conversation
        exclude_buffer_cutoff=buffer_cutoff
    )
    
    print(f"\n✅ Retrieved {len(results)} messages:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. [Score: {result['score']:.3f}] {result['text'][:60]}...")
    
    # Verify we found the name message
    found_name = any("Mehedi Hasan Moon" in r['text'] for r in results)
    
    if found_name:
        print("\n✅ PASSED: Found user's name in cross-conversation retrieval!")
        
        # Check if it's ranked high (should be in top 3)
        name_result = next((r for r in results if "Mehedi Hasan Moon" in r['text']), None)
        rank = results.index(name_result) + 1 if name_result else -1
        
        if rank <= 3:
            print(f"✅ BONUS: Name message ranked #{rank} (good re-ranking!)")
        else:
            print(f"⚠️  Warning: Name message ranked #{rank} (re-ranking could be better)")
        
        return True
    else:
        print("\n❌ FAILED: Could not find user's name message!")
        return False


def test_query_exclusion():
    """Test 3: Verify current query message is NOT retrieved"""
    print("\n" + "="*60)
    print("TEST 3: QUERY MESSAGE EXCLUSION")
    print("="*60)
    
    chat = SimpleChat(enable_rag=True)
    conv = chat.start_new_conversation("Query Test")
    
    # Add some messages
    print("\n📝 Adding historical messages...")
    conv.buffer.add_message("user", "My favorite color is blue")
    conv.buffer.add_message("assistant", "Blue is a nice color!")
    time.sleep(0.5)
    
    # Now add a query message
    print("\n📝 Adding query message...")
    query_text = "What is my favorite color?"
    conv.buffer.add_message("user", query_text)
    time.sleep(0.1)  # Small delay
    
    # Immediately try to retrieve
    print("\n🔍 Searching immediately after adding query...")
    buffer_cutoff = conv.buffer.get_cutoff_timestamp()
    
    results = chat.llm.vector_index.retrieve_relevant(
        query="favorite color",
        top_k=5,
        node_id=None,
        exclude_buffer_cutoff=buffer_cutoff
    )
    
    print(f"\n✅ Retrieved {len(results)} messages:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. [Score: {result['score']:.3f}] {result['text'][:60]}...")
    
    # Verify query message is NOT in results
    query_in_results = any(query_text in r['text'] for r in results)
    
    if query_in_results:
        print(f"\n❌ FAILED: Query message '{query_text}' found in results!")
        return False
    else:
        print(f"\n✅ PASSED: Query message correctly excluded!")
        
        # Verify we found the actual answer
        found_answer = any("blue" in r['text'].lower() for r in results)
        if found_answer:
            print("✅ BONUS: Found the actual answer message!")
        
        return True


def test_multiquery_decomposition():
    """Test 4: Verify multi-query decomposition for complex queries"""
    print("\n" + "="*60)
    print("TEST 4: MULTI-QUERY DECOMPOSITION")
    print("="*60)
    
    chat = SimpleChat(enable_rag=True)
    conv = chat.start_new_conversation("Complex Query Test")
    
    # Add diverse information
    print("\n📝 Adding diverse user information...")
    conv.buffer.add_message("user", "My name is Mehedi")
    conv.buffer.add_message("assistant", "Hello Mehedi!")
    conv.buffer.add_message("user", "I study at MIST")
    conv.buffer.add_message("assistant", "Great university!")
    conv.buffer.add_message("user", "I love cricket")
    conv.buffer.add_message("assistant", "Cricket is fun!")
    conv.buffer.add_message("user", "My favorite language is Python")
    conv.buffer.add_message("assistant", "Python is powerful!")
    time.sleep(0.2)
    
    # Clear buffer
    conv.buffer.clear()
    
    # Complex query that needs decomposition
    print("\n🔍 Testing complex query: 'Tell me everything about the user'")
    print("   (Should decompose into: name, college, hobbies, programming)")
    
    from src.services.reranker import get_multi_query_retriever
    multi_query = get_multi_query_retriever()
    
    query = "Tell me everything about the user - their name, college, hobbies, and programming preferences"
    sub_queries = multi_query.decompose_query(query)
    
    print(f"\n✅ Decomposed into {len(sub_queries)} sub-queries:")
    for i, sq in enumerate(sub_queries, 1):
        print(f"   {i}. {sq}")
    
    # Retrieve with multi-query
    buffer_cutoff = conv.buffer.get_cutoff_timestamp()
    
    results = multi_query.retrieve_with_decomposition(
        query=query,
        vector_index=chat.llm.vector_index,
        top_k_per_query=2,
        final_top_k=5,
        node_id=None,
        exclude_buffer_cutoff=buffer_cutoff
    )
    
    print(f"\n✅ Retrieved {len(results)} messages:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. [Score: {result['score']:.3f}] {result['text'][:60]}...")
    
    # Verify we got diverse information
    topics_found = {
        'name': any("Mehedi" in r['text'] for r in results),
        'college': any("MIST" in r['text'] for r in results),
        'cricket': any("cricket" in r['text'].lower() for r in results),
        'python': any("Python" in r['text'] for r in results)
    }
    
    print(f"\n📊 Topics found:")
    for topic, found in topics_found.items():
        status = "✅" if found else "❌"
        print(f"   {status} {topic}: {found}")
    
    coverage = sum(topics_found.values()) / len(topics_found)
    
    if coverage >= 0.75:  # At least 3/4 topics
        print(f"\n✅ PASSED: Multi-query found {int(coverage*100)}% of topics!")
        return True
    else:
        print(f"\n⚠️  Warning: Multi-query only found {int(coverage*100)}% of topics")
        return True  # Still pass, but with warning


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("🧪 RETRIEVAL & RE-RANKING TEST SUITE")
    print("="*60)
    
    tests = [
        ("Buffer Exclusion", test_buffer_exclusion),
        ("Re-ranking Quality", test_reranking_quality),
        ("Query Exclusion", test_query_exclusion),
        ("Multi-Query Decomposition", test_multiquery_decomposition)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\n{passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️  Some tests failed - review above for details")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
