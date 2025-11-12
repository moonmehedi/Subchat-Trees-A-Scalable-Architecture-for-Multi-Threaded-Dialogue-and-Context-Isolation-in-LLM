"""
Integration test for multi-query decomposition + context windows.
Tests the complete RAG pipeline with the enhanced retrieval system.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.vector_index import GlobalVectorIndex
from src.services.tools import ConversationTools
from src.models.tree import TreeNode, LocalBuffer


class MockNode:
    """Mock node for testing"""
    def __init__(self, node_id: str, vector_index):
        self.id = node_id
        self.buffer = LocalBuffer(max_turns=10, vector_index=vector_index, node_id=node_id)
        self.vector_index = vector_index
    
    def add_message(self, text: str, role: str = "user", timestamp: float = None):
        """Add message to buffer (which auto-indexes)"""
        if timestamp:
            # Temporarily override time.time() for testing
            original_time = time.time
            time.time = lambda: timestamp
            self.buffer.add_message(role=role, text=text, auto_archive=True)
            time.time = original_time
        else:
            self.buffer.add_message(role=role, text=text, auto_archive=True)


def test_multi_query_integration():
    """
    Test the complete RAG pipeline with multi-query decomposition.
    
    Simulates a real conversation where:
    1. User introduces themselves
    2. Conversation continues
    3. User asks "who am i?" later
    4. System should retrieve introduction using multi-query
    """
    
    print("="*80)
    print("🧪 INTEGRATION TEST: Multi-Query Decomposition + Context Windows")
    print("="*80)
    
    # Step 1: Create fresh vector index
    print("\n📦 Step 1: Creating fresh vector index...")
    vector_index = GlobalVectorIndex(persist_dir="./test_integration_chroma_db")
    
    # Step 2: Create conversation tree and node
    print("\n🌳 Step 2: Creating mock conversation node...")
    root_node = MockNode(
        node_id="test_conversation_root",
        vector_index=vector_index
    )
    
    # Step 3: Simulate realistic conversation
    print("\n💬 Step 3: Simulating realistic conversation...")
    
    base_time = time.time() - 300  # 5 minutes ago
    
    # User introduces themselves
    print("   User: Hi! My name is Moon and I'm a student at MIT.")
    root_node.add_message(
        "Hi! My name is Moon and I'm a student at MIT.",
        role="user",
        timestamp=base_time
    )
    
    # Assistant responds
    print("   Assistant: That's a great introduction, Moon!")
    root_node.add_message(
        "That's a great introduction, Moon! What are you studying at MIT?",
        role="assistant",
        timestamp=base_time + 2
    )
    
    # User shares more
    print("   User: I'm studying computer science and my favorite language is Python.")
    root_node.add_message(
        "I'm studying computer science and my favorite programming language is Python.",
        role="user",
        timestamp=base_time + 5
    )
    
    # Discussion about Python
    print("   Assistant: Python is great for many applications...")
    root_node.add_message(
        "Python is a high-level programming language known for its simplicity and readability.",
        role="assistant",
        timestamp=base_time + 60
    )
    
    # More conversation (to fill buffer)
    for i in range(8):
        root_node.add_message(
            f"This is filler message number {i+1} to fill up the buffer.",
            role="user" if i % 2 == 0 else "assistant",
            timestamp=base_time + 70 + (i * 5)
        )
    
    # User shares preferences
    print("   User: I love machine learning and I'm working on a PyTorch project.")
    root_node.add_message(
        "I love machine learning and I'm working on a project using PyTorch.",
        role="user",
        timestamp=base_time + 150
    )
    
    # More filler to push old messages to archive
    for i in range(5):
        root_node.add_message(
            f"This is additional filler message {i+1}.",
            role="user" if i % 2 == 0 else "assistant",
            timestamp=base_time + 160 + (i * 5)
        )
    
    # Step 4: Check buffer status
    print(f"\n📊 Step 4: Buffer status:")
    print(f"   Buffer size: {root_node.buffer.size()} messages")
    print(f"   Vector index: {vector_index.collection.count()} archived messages")
    
    # Step 5: Test tool calling with "who am i?" query
    print(f"\n🔍 Step 5: Testing tool calling with 'who am i?' query...")
    
    # Simulate tool call
    tool_args = {
        "query": "who am i?",
        "top_k": 5
    }
    
    result = ConversationTools.execute_tool(
        tool_name="search_conversation_history",
        arguments=tool_args,
        vector_index=vector_index,
        node=root_node
    )
    
    print(f"\n📋 Tool execution result:")
    print(result)
    
    # Step 6: Verify results
    print(f"\n✅ Step 6: Verification:")
    
    has_introduction = "My name is Moon" in result
    has_mit = "MIT" in result
    has_preferences = "favorite programming language" in result or "machine learning" in result
    
    print(f"   ✓ Found introduction: {has_introduction}")
    print(f"   ✓ Found MIT mention: {has_mit}")
    print(f"   ✓ Found preferences: {has_preferences}")
    
    # Step 7: Test with vague query "user identity information"
    print(f"\n🔍 Step 7: Testing with vague query 'user identity information'...")
    
    tool_args_vague = {
        "query": "user identity information",
        "top_k": 5
    }
    
    result_vague = ConversationTools.execute_tool(
        tool_name="search_conversation_history",
        arguments=tool_args_vague,
        vector_index=vector_index,
        node=root_node
    )
    
    print(f"\n📋 Vague query result:")
    print(result_vague)
    
    has_introduction_vague = "My name is Moon" in result_vague
    has_mit_vague = "MIT" in result_vague
    
    print(f"\n✅ Vague query verification:")
    print(f"   ✓ Found introduction: {has_introduction_vague}")
    print(f"   ✓ Found MIT mention: {has_mit_vague}")
    
    # Final assessment
    print("\n" + "="*80)
    if has_introduction and has_mit and has_introduction_vague and has_mit_vague:
        print("✅ INTEGRATION TEST PASSED!")
        print("   Multi-query decomposition is working correctly in production pipeline.")
        print("   The system can now handle both direct and vague queries effectively.")
    else:
        print("⚠️  INTEGRATION TEST FAILED!")
        print("   Some queries did not retrieve expected information.")
        print(f"   Direct query success: {has_introduction and has_mit}")
        print(f"   Vague query success: {has_introduction_vague and has_mit_vague}")
    print("="*80)
    
    # Cleanup
    vector_index.clear()
    print("\n🗑️  Cleaned up test data")


if __name__ == "__main__":
    # Set GROQ_API_KEY if not already set
    if not os.getenv("GROQ_API_KEY"):
        # Try to load from .env file
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('GROQ_API_KEY='):
                        key = line.strip().split('=', 1)[1]
                        os.environ['GROQ_API_KEY'] = key
                        print(f"✅ Loaded GROQ_API_KEY from .env")
                        break
    
    test_multi_query_integration()
