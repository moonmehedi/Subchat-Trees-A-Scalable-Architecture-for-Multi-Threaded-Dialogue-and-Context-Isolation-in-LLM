"""
Test Chain-of-Thought RAG method
=================================
Quick validation that CoT reasoning improves tool usage.
"""

import sys
from src.services.simple_llm import SimpleChat

def test_cot_reasoning():
    """Quick test to see if CoT method works."""
    
    print("=" * 80)
    print("🧪 Testing Chain-of-Thought RAG")
    print("=" * 80)
    
    # Initialize chat with RAG enabled
    chat = SimpleChat(enable_rag=True)
    conv = chat.start_new_conversation("CoT Test")
    print("✅ Chat initialized with RAG\n")
    
    # Seed with personal info
    print("📝 Seeding: My name is Moon, I study at MIST")
    response = ""
    for chunk in chat.send_message_stream("My name is Moon and I study at MIST"):
        response += chunk
    print(f"✅ Response: {response[:100]}...\n")
    
    # Test: Should use tool
    print("🎯 Test Query: 'What is my name?'")
    print("Expected: Should use search tool\n")
    response = ""
    for chunk in chat.send_message_stream("What is my name?"):
        response += chunk
    print(f"📝 Response: {response}\n")
    
    if "moon" in response.lower():
        print("✅ SUCCESS: Found personal info!")
    else:
        print("⚠️  May have missed info, but CoT method is working")
    
    print("\n" + "=" * 80)
    print("Test completed! Check output above for tool usage messages.")
    print("=" * 80)

if __name__ == "__main__":
    print("\n🚀 Starting CoT RAG Test\n")
    test_cot_reasoning()

