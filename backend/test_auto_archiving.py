#!/usr/bin/env python3
"""
Test auto-archiving workflow:
1. Create conversation with small buffer (5 messages)
2. Add 15 messages (should trigger archiving of 10 oldest)
3. Verify buffer only has recent 5
4. Verify vector index has archived 10
5. Retrieve from archive successfully
"""

import sys
import time
from src.models.tree import TreeNode, LocalBuffer
from src.services.vector_index import GlobalVectorIndex

def test_auto_archiving():
    print("=" * 60)
    print("🧪 Testing Auto-Archiving Workflow")
    print("=" * 60)
    
    # Initialize vector index
    print("\n--- Step 1: Initialize System ---")
    vector_index = GlobalVectorIndex(persist_dir="./test_chroma_archive")
    vector_index.clear()  # Start fresh
    print("✅ Vector index initialized and cleared")
    
    # Create TreeNode with small buffer for testing
    print("\n--- Step 2: Create Conversation (Buffer Size = 5) ---")
    node = TreeNode(node_id="test_conversation", title="Python Discussion", vector_index=vector_index)
    node.buffer = LocalBuffer(max_turns=5, vector_index=vector_index, node_id=node.node_id)
    print(f"✅ Created conversation '{node.title}' with buffer size 5")
    
    # Add 15 messages (should archive 10 oldest)
    print("\n--- Step 3: Add 15 Messages (Trigger Archiving) ---")
    messages = [
        ("user", "What is Python?"),
        ("assistant", "Python is a high-level programming language."),
        ("user", "How do I install it?"),
        ("assistant", "You can download Python from python.org."),
        ("user", "What are variables?"),
        ("assistant", "Variables store data values in Python."),
        ("user", "How do loops work?"),
        ("assistant", "Python has for and while loops."),
        ("user", "What are functions?"),
        ("assistant", "Functions are reusable blocks of code."),
        ("user", "What is a class?"),
        ("assistant", "Classes define object blueprints in Python."),
        ("user", "What are decorators?"),
        ("assistant", "Decorators modify function behavior."),
        ("user", "Explain list comprehensions"),
        ("assistant", "List comprehensions create lists concisely."),
    ]
    
    for i, (role, text) in enumerate(messages, 1):
        node.buffer.add_message(role, text)
        buffer_size = node.buffer.size()
        print(f"  Message {i:02d}: Added ({role:9s}) - Buffer size: {buffer_size}")
        if buffer_size == 5 and i > 5:
            print(f"            ↳ 📦 Message {i-5} archived to vector storage")
        time.sleep(0.1)  # Small delay to ensure different timestamps
    
    # Verify buffer state
    print("\n--- Step 4: Verify Buffer State ---")
    buffer_messages = node.buffer.get_recent()
    print(f"✅ Buffer contains {len(buffer_messages)} messages (expected: 5)")
    print("\nRecent messages in buffer:")
    for i, msg in enumerate(buffer_messages, 1):
        print(f"  {i}. [{msg['role']:9s}] {msg['text'][:50]}...")
    
    # Verify vector index state
    print("\n--- Step 5: Verify Vector Archive ---")
    stats = vector_index.get_stats()
    archived_count = stats['total_archived_messages']
    print(f"✅ Vector index contains {archived_count} archived messages (expected: 10)")
    
    # Test retrieval
    print("\n--- Step 6: Test Retrieval from Archive ---")
    
    test_queries = [
        "How do I install Python?",
        "What are variables in Python?",
        "Tell me about loops"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = vector_index.retrieve_relevant(
            query=query,
            top_k=2,
            node_id=node.node_id
        )
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['text'][:60]}... (score: {result['score']:.3f})")
        else:
            print("  No results found")
    
    # Verify retrieval excludes buffer messages
    print("\n--- Step 7: Verify Buffer Exclusion ---")
    cutoff_timestamp = node.buffer.get_cutoff_timestamp(exclude_recent=5)
    print(f"Buffer cutoff timestamp: {cutoff_timestamp}")
    
    recent_query = "Explain list comprehensions"  # This is in buffer, not archive
    results = vector_index.retrieve_relevant(
        query=recent_query,
        top_k=3,
        node_id=node.node_id,
        exclude_buffer_cutoff=cutoff_timestamp
    )
    
    print(f"\nQuery for recent message: '{recent_query}'")
    if results:
        print(f"❌ ERROR: Found {len(results)} results (should be 0 - message is in buffer, not archived)")
        for result in results:
            print(f"  - {result['text'][:50]}... (timestamp: {result['metadata'].get('timestamp')})")
    else:
        print("✅ Correct: No results found (message is in buffer, not archived yet)")
    
    # Final statistics
    print("\n" + "=" * 60)
    print("📊 Final Statistics")
    print("=" * 60)
    print(f"Total messages added: {len(messages)}")
    print(f"Messages in buffer: {node.buffer.size()}")
    print(f"Messages in archive: {archived_count}")
    print(f"Expected in archive: {len(messages) - 5} (total - buffer_size)")
    
    # Cleanup
    vector_index.clear()
    print("\n🗑️  Cleaned up test data")
    
    # Validation
    if archived_count == len(messages) - 5 and node.buffer.size() == 5:
        print("\n✅ All auto-archiving tests passed!")
        return True
    else:
        print(f"\n❌ Test failed: Expected {len(messages) - 5} archived, {5} in buffer")
        print(f"   Got {archived_count} archived, {node.buffer.size()} in buffer")
        return False


if __name__ == "__main__":
    success = test_auto_archiving()
    sys.exit(0 if success else 1)
