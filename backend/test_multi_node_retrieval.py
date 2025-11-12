"""
Multi-Node Retrieval Test
Tests RAG system with MULTIPLE conversation nodes/trees.

Verifies:
1. Messages indexed from different conversations
2. Cross-conversation search works correctly
3. Node-specific filtering works
4. Context windows respect conversation boundaries
"""

import sys
import os
import time
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.vector_index import GlobalVectorIndex
from src.models.tree import LocalBuffer


class MockNode:
    """Mock node for testing"""
    def __init__(self, node_id: str, vector_index):
        self.id = node_id
        self.buffer = LocalBuffer(max_turns=10, vector_index=vector_index, node_id=node_id)
        self.vector_index = vector_index
    
    def add_message(self, text: str, role: str = "user", timestamp: float = None):
        """Add message directly to vector index (bypass buffer for testing)"""
        if timestamp is None:
            timestamp = time.time()
        
        # Add directly to vector index for testing
        self.vector_index.index_message(
            node_id=self.id,
            message=text,
            metadata={
                'role': role,
                'timestamp': timestamp,
                'archived': True
            }
        )


def test_multi_node_retrieval():
    """
    Test retrieval across multiple conversation nodes.
    
    Scenario:
    - Conversation 1: User talks about their name (Mehedi)
    - Conversation 2: User discusses quantum computing
    - Conversation 3: User asks "what have you told me about quantum computing?"
    
    Expected: System should find the quantum computing discussion from Conversation 2
    """
    
    print("="*80)
    print("🧪 MULTI-NODE RETRIEVAL TEST")
    print("="*80)
    
    # Clean slate
    test_dir = "./test_multi_node_chroma_db"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # Initialize vector index
    print("\n📦 Creating vector index...")
    vector_index = GlobalVectorIndex(persist_dir=test_dir)
    
    # Create 3 different conversation nodes
    print("\n🌳 Creating 3 conversation nodes...")
    
    conv1 = MockNode("conversation_1_intro", vector_index)
    conv2 = MockNode("conversation_2_quantum", vector_index)
    conv3 = MockNode("conversation_3_recall", vector_index)
    
    base_time = time.time() - 600  # 10 minutes ago
    
    # === CONVERSATION 1: Introduction ===
    print("\n💬 Conversation 1 (Introduction):")
    print("   User: Hi, how are you?")
    conv1.add_message(
        "Hi, how are you?",
        role="user",
        timestamp=base_time
    )
    
    print("   Assistant: I'm doing well, thanks!")
    conv1.add_message(
        "I'm doing well, thanks for asking. How can I assist you today?",
        role="assistant",
        timestamp=base_time + 2
    )
    
    print("   User: My name is Mehedi Hassan Moon")
    conv1.add_message(
        "my name is mehedi hassan moon",
        role="user",
        timestamp=base_time + 5
    )
    
    print("   Assistant: Nice to meet you, Mehedi!")
    conv1.add_message(
        "It's nice to know your name, Mehedi. How are you doing today?",
        role="assistant",
        timestamp=base_time + 7
    )
    
    # === CONVERSATION 2: Quantum Computing ===
    print("\n💬 Conversation 2 (Quantum Computing):")
    print("   User: Tell something about quantum computing")
    conv2.add_message(
        "tell something about quantum computhing",
        role="user",
        timestamp=base_time + 100
    )
    
    print("   Assistant: [Long explanation about quantum computing]")
    conv2.add_message(
        "Quantum computing is a fascinating field that's changing the way we think about computation. "
        "Unlike classical computers that use bits (0s and 1s), quantum computers use quantum bits or 'qubits'. "
        "These qubits can exist in multiple states simultaneously through a phenomenon called superposition. "
        "Additionally, qubits can be entangled, meaning the state of one qubit is dependent on the state of another, "
        "regardless of the distance between them. This allows quantum computers to solve certain problems "
        "exponentially faster than classical computers, particularly in areas like cryptography, optimization, "
        "and simulation of quantum systems. However, quantum computers are still in early stages of development "
        "and face challenges like maintaining quantum coherence and error correction.",
        role="assistant",
        timestamp=base_time + 102
    )
    
    # === CONVERSATION 3: Recall Query ===
    print("\n💬 Conversation 3 (Recall Test):")
    print("   User: What have you told me about quantum computing previously?")
    
    # For testing, we'll just use a cutoff timestamp
    # (messages before this should be searchable)
    buffer_cutoff = base_time + 200  # The query time
    
    print(f"\n🔍 Searching across all conversations...")
    print(f"   Buffer cutoff: {buffer_cutoff}")
    print(f"   Total messages in vector index: {vector_index.collection.count()}")
    
    # === TEST 1: Cross-conversation search ===
    print("\n" + "="*80)
    print("TEST 1: Cross-Conversation Search (no node_id filter)")
    print("="*80)
    
    results = vector_index.retrieve_with_multi_query(
        query="quantum computing",
        top_k=5,
        node_id=None,  # Search ALL conversations
        exclude_buffer_cutoff=buffer_cutoff
    )
    
    print(f"\n✅ Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Conversation: {result['metadata'].get('node_id', 'unknown')}")
        print(f"   Role: {result['metadata'].get('role', 'unknown')}")
        print(f"   Text: {result['text'][:100]}...")
    
    # Verify quantum computing message was found
    quantum_found = any("quantum" in r['text'].lower() for r in results)
    if quantum_found:
        print("\n✅ SUCCESS: Found quantum computing discussion from Conversation 2!")
    else:
        print("\n❌ FAILURE: Did NOT find quantum computing discussion!")
        print(f"   Expected to find messages with 'quantum' keyword")
        print(f"   But got: {[r['text'][:50] for r in results]}")
    
    # === TEST 2: Node-specific search ===
    print("\n" + "="*80)
    print("TEST 2: Node-Specific Search (filter to conversation_1_intro)")
    print("="*80)
    
    results_conv1 = vector_index.retrieve_with_multi_query(
        query="user name",
        top_k=5,
        node_id="conversation_1_intro",  # Only search Conversation 1
        exclude_buffer_cutoff=None
    )
    
    print(f"\n✅ Found {len(results_conv1)} results from Conversation 1:")
    for i, result in enumerate(results_conv1, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Conversation: {result['metadata'].get('node_id', 'unknown')}")
        print(f"   Text: {result['text'][:100]}...")
    
    # Verify only conv1 messages returned
    all_from_conv1 = all(r['metadata'].get('node_id') == 'conversation_1_intro' for r in results_conv1)
    if all_from_conv1 and results_conv1:
        print("\n✅ SUCCESS: Node filtering works correctly!")
    else:
        print("\n❌ FAILURE: Node filtering didn't work as expected!")
    
    # === TEST 3: Verify quantum NOT in conv1 ===
    print("\n" + "="*80)
    print("TEST 3: Isolation Check (quantum search in conversation_1_intro should fail)")
    print("="*80)
    
    results_quantum_conv1 = vector_index.retrieve_with_multi_query(
        query="quantum computing",
        top_k=5,
        node_id="conversation_1_intro",  # Search ONLY Conversation 1
        exclude_buffer_cutoff=None
    )
    
    print(f"\n✅ Found {len(results_quantum_conv1)} results:")
    quantum_in_conv1 = any("quantum" in r['text'].lower() for r in results_quantum_conv1)
    
    if not quantum_in_conv1:
        print("✅ SUCCESS: Quantum computing NOT found in Conversation 1 (correct isolation)!")
    else:
        print("❌ FAILURE: Quantum computing leaked into Conversation 1 search!")
    
    # === FINAL SUMMARY ===
    print("\n" + "="*80)
    print("📊 FINAL TEST SUMMARY")
    print("="*80)
    print(f"✅ Cross-conversation search: {'PASS' if quantum_found else 'FAIL'}")
    print(f"✅ Node-specific filtering: {'PASS' if all_from_conv1 and results_conv1 else 'FAIL'}")
    print(f"✅ Conversation isolation: {'PASS' if not quantum_in_conv1 else 'FAIL'}")
    
    overall = quantum_found and all_from_conv1 and results_conv1 and not quantum_in_conv1
    
    if overall:
        print("\n🎉 ALL MULTI-NODE TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED - Review output above")
        return False


if __name__ == "__main__":
    success = test_multi_node_retrieval()
    sys.exit(0 if success else 1)
