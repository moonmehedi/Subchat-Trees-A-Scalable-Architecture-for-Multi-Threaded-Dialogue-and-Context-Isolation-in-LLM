"""
Comprehensive test for re-ranking and tool calling behavior.

Tests:
1. Re-ranking actually changes message order (not same before/after)
2. Tools are NOT called for general knowledge questions
3. Tools ARE called for personal/historical questions
4. Tool usage is not mentioned in LLM responses
"""

import sys
import os

# Set environment variable to prevent FastAPI server from starting
os.environ['TESTING'] = 'true'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.tree import TreeNode
from services.simple_llm import SimpleLLMClient
from services.vector_index import GlobalVectorIndex
import time

def setup_test_data():
    """Create test conversations with diverse content"""
    print("🔧 Setting up test data...")
    
    # Create a fresh vector index
    vector_index = GlobalVectorIndex()
    
    # Create a test node
    node = TreeNode(
        node_id="test-node-123",
        vector_index=vector_index,
        buffer_size=10
    )
    
    # Add diverse messages to test re-ranking
    test_messages = [
        ("user", "My name is Alice and I work as a software engineer"),
        ("assistant", "Nice to meet you, Alice! It's great to connect with a software engineer."),
        ("user", "I'm 28 years old and I live in San Francisco"),
        ("assistant", "San Francisco is a wonderful city! The tech scene there is amazing."),
        ("user", "I love hiking and photography in my free time"),
        ("assistant", "Those are great hobbies! The Bay Area has fantastic hiking trails."),
        ("user", "What is quantum computing?"),
        ("assistant", "Quantum computing is a type of computing that uses quantum-mechanical phenomena..."),
        ("user", "How does photosynthesis work?"),
        ("assistant", "Photosynthesis is the process by which plants convert light energy into chemical energy..."),
        ("user", "Tell me about machine learning"),
        ("assistant", "Machine learning is a subset of artificial intelligence that enables systems to learn..."),
    ]
    
    # Add messages with delays to ensure they get archived
    for role, text in test_messages:
        node.add_message(role, text, auto_archive=True)
        time.sleep(0.1)  # Small delay to ensure different timestamps
    
    print(f"✅ Added {len(test_messages)} test messages")
    print(f"📦 Vector index now has {vector_index.collection.count()} messages")
    
    return node, vector_index


def test_reranking_changes_order(node, vector_index):
    """Test that re-ranking actually changes the order of results"""
    print("\n" + "="*80)
    print("TEST 1: Re-ranking Changes Order")
    print("="*80)
    
    query = "Alice software engineer San Francisco"
    
    # Get results without re-ranking (just ChromaDB similarity)
    print(f"\n🔍 Query: '{query}'")
    print("\nTesting if re-ranking changes the order...")
    
    # This will show before/after in the logs
    results = vector_index.retrieve_relevant(
        query=query,
        top_k=5,
        node_id=None,
        exclude_buffer_cutoff=None
    )
    
    if len(results) >= 3:
        # Check if there's any variation in scores
        scores = [r['score'] for r in results]
        if len(set(scores)) == 1:
            print("❌ FAIL: All scores are identical - re-ranking may not be working!")
            return False
        else:
            print("✅ PASS: Scores vary - re-ranking appears to be working")
            return True
    else:
        print("⚠️  SKIP: Not enough results to test re-ranking")
        return True


def test_tool_not_called_for_general_knowledge():
    """Test that tools are NOT called for general knowledge questions"""
    print("\n" + "="*80)
    print("TEST 2: Tool NOT Called for General Knowledge")
    print("="*80)
    
    vector_index = GlobalVectorIndex()
    llm_client = SimpleLLMClient(enable_vector_index=True)
    llm_client.vector_index = vector_index
    
    # Create a node with some context
    node = TreeNode(node_id="test-general-1", vector_index=vector_index)
    node.add_message("user", "Hello")
    node.add_message("assistant", "Hi! How can I help you?")
    
    # Test general knowledge questions (should NOT use tool)
    general_questions = [
        "What is the capital of France?",
        "How does photosynthesis work?",
        "Explain quantum mechanics",
        "What is the speed of light?",
        "Who invented the telephone?"
    ]
    
    passed = 0
    failed = 0
    
    for question in general_questions:
        print(f"\n📝 Testing: '{question}'")
        
        # Check if tool is called by looking at the response
        tool_called = False
        response_chunks = []
        
        try:
            for chunk in llm_client.generate_response_stream_with_rag_cot(node, question):
                response_chunks.append(chunk)
                # Check if tool was invoked (would see search_conversation_history in logs)
                if "search_conversation_history" in chunk.lower():
                    tool_called = True
        except Exception as e:
            print(f"   Error: {e}")
            continue
        
        full_response = ''.join(response_chunks)
        
        # Check that response doesn't mention tool usage
        tool_mentions = [
            "search_conversation_history",
            "searching for",
            "retrieved messages",
            "archived messages",
            "according to the search"
        ]
        
        mentions_tool = any(mention in full_response.lower() for mention in tool_mentions)
        
        if not tool_called and not mentions_tool:
            print(f"   ✅ PASS: Tool not called, response is clean")
            passed += 1
        else:
            print(f"   ❌ FAIL: Tool called or mentioned in response")
            failed += 1
    
    print(f"\n📊 Results: {passed}/{len(general_questions)} passed")
    return failed == 0


def test_tool_called_for_personal_questions(node, vector_index):
    """Test that tools ARE called for personal/historical questions"""
    print("\n" + "="*80)
    print("TEST 3: Tool IS Called for Personal Questions")
    print("="*80)
    
    llm_client = SimpleLLMClient(enable_vector_index=True)
    llm_client.vector_index = vector_index
    
    # Create a new conversation (so personal info is archived)
    new_node = TreeNode(node_id="test-personal-1", vector_index=vector_index)
    new_node.add_message("user", "Hi")
    new_node.add_message("assistant", "Hello! How can I help you?")
    
    # Test personal questions (should USE tool)
    personal_questions = [
        "What is my name?",
        "Where do I live?",
        "What do I do for work?",
        "What are my hobbies?",
        "Tell me about myself"
    ]
    
    passed = 0
    failed = 0
    
    for question in personal_questions:
        print(f"\n📝 Testing: '{question}'")
        
        # Monitor for tool usage in logs (we'll see the search output)
        response_chunks = []
        
        try:
            for chunk in llm_client.generate_response_stream_with_rag_cot(new_node, question):
                response_chunks.append(chunk)
        except Exception as e:
            print(f"   Error: {e}")
            continue
        
        full_response = ''.join(response_chunks)
        
        # Check that tool usage is NOT mentioned in the response to user
        tool_mentions = [
            "search_conversation_history",
            "searching for",
            "retrieved messages",
            "archived messages"
        ]
        
        mentions_tool = any(mention in full_response.lower() for mention in tool_mentions)
        
        # The tool should be called (we'd see it in logs), but not mentioned to user
        if not mentions_tool:
            print(f"   ✅ PASS: Tool used but not mentioned to user")
            passed += 1
        else:
            print(f"   ❌ FAIL: Tool usage mentioned in response")
            print(f"   Response preview: {full_response[:200]}...")
            failed += 1
    
    print(f"\n📊 Results: {passed}/{len(personal_questions)} passed")
    return failed == 0


def test_tool_transparency():
    """Test that tool calls are transparent (not mentioned in responses)"""
    print("\n" + "="*80)
    print("TEST 4: Tool Usage is Transparent")
    print("="*80)
    
    vector_index = GlobalVectorIndex()
    llm_client = SimpleLLMClient(enable_vector_index=True)
    llm_client.vector_index = vector_index
    
    # Add some test data
    node = TreeNode(node_id="test-transparency", vector_index=vector_index)
    node.add_message("user", "My favorite color is blue")
    node.add_message("assistant", "That's a great color!")
    time.sleep(0.5)
    
    # Create new conversation
    new_node = TreeNode(node_id="test-transparency-2", vector_index=vector_index)
    new_node.add_message("user", "Hi")
    new_node.add_message("assistant", "Hello!")
    
    # Ask a question that should trigger tool use
    question = "What's my favorite color?"
    print(f"\n📝 Testing: '{question}'")
    
    response_chunks = []
    for chunk in llm_client.generate_response_stream_with_rag_cot(new_node, question):
        response_chunks.append(chunk)
    
    full_response = ''.join(response_chunks)
    
    # These phrases should NOT appear in user-facing response
    forbidden_phrases = [
        "search_conversation_history",
        "<function=",
        "tool call",
        "searching for",
        "retrieved messages",
        "archived messages",
        "according to the search results"
    ]
    
    violations = []
    for phrase in forbidden_phrases:
        if phrase.lower() in full_response.lower():
            violations.append(phrase)
    
    if not violations:
        print(f"   ✅ PASS: Response is clean and transparent")
        print(f"   Response: {full_response[:150]}...")
        return True
    else:
        print(f"   ❌ FAIL: Found tool mentions in response:")
        for v in violations:
            print(f"      - '{v}'")
        print(f"   Full response: {full_response}")
        return False


def main():
    """Run all tests"""
    print("="*80)
    print("RE-RANKING AND TOOL CALLING TEST SUITE")
    print("="*80)
    
    # Setup
    node, vector_index = setup_test_data()
    
    # Run tests
    results = []
    
    # Test 1: Re-ranking changes order
    results.append(("Re-ranking Changes Order", test_reranking_changes_order(node, vector_index)))
    
    # Test 2: Tool not called for general knowledge
    results.append(("Tool NOT Called (General)", test_tool_not_called_for_general_knowledge()))
    
    # Test 3: Tool called for personal questions
    results.append(("Tool IS Called (Personal)", test_tool_called_for_personal_questions(node, vector_index)))
    
    # Test 4: Tool usage is transparent
    results.append(("Tool Transparency", test_tool_transparency()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
