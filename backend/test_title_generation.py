#!/usr/bin/env python3
"""
Test script for title generation functionality.
Tests both the backend API and the title generation logic.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_QUESTIONS = [
    "What is artificial intelligence?",
    "How does machine learning work?", 
    "Explain quantum computing",
    "What are the benefits of renewable energy?",
    "How do neural networks function?",
    "What is the future of robotics?",
    "Explain blockchain technology",
    "How does photosynthesis work?"
]

def test_conversation_creation() -> str:
    """Test creating a new conversation with default title"""
    print("🧪 Testing conversation creation...")
    
    response = requests.post(f"{BACKEND_URL}/api/conversations", 
                           headers={"Content-Type": "application/json"},
                           json={"title": "New Chat"})
    
    if response.status_code == 200:
        data = response.json()
        conversation_id = data["node_id"]
        title = data["title"]
        
        print(f"✅ Conversation created successfully!")
        print(f"   ID: {conversation_id}")
        print(f"   Default Title: {title}")
        
        # Verify it has default title
        assert title == "New Chat", f"Expected 'New Chat', got '{title}'"
        return conversation_id
    else:
        print(f"❌ Failed to create conversation: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Conversation creation failed")

def test_first_message_title_generation(conversation_id: str, question: str) -> Dict[str, Any]:
    """Test sending first message and title generation"""
    print(f"\n🧪 Testing first message and title generation...")
    print(f"   Question: '{question}'")
    
    # Send first message
    message_data = {"message": question}
    response = requests.post(f"{BACKEND_URL}/api/conversations/{conversation_id}/messages",
                           headers={"Content-Type": "application/json"},
                           json=message_data)
    
    if response.status_code == 200:
        data = response.json()
        generated_title = data.get("conversation_title")
        
        print(f"✅ Message sent successfully!")
        print(f"   AI Response: {data['response'][:100]}...")
        print(f"   Generated Title: '{generated_title}'")
        
        # Verify title was generated and is not default
        assert generated_title is not None, "Title should not be None"
        assert generated_title != "New Chat", f"Title should be generated, not default: '{generated_title}'"
        assert generated_title != "Conversation", f"Title should be meaningful, not generic: '{generated_title}'"
        assert len(generated_title) > 0, "Title should not be empty"
        
        return data
    else:
        print(f"❌ Failed to send message: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Message sending failed")

def test_conversation_title_persistence(conversation_id: str, expected_title: str):
    """Test that the title persists in the conversation object"""
    print(f"\n🧪 Testing title persistence...")
    
    response = requests.get(f"{BACKEND_URL}/api/conversations/{conversation_id}")
    
    if response.status_code == 200:
        data = response.json()
        stored_title = data["title"]
        
        print(f"✅ Conversation retrieved successfully!")
        print(f"   Stored Title: '{stored_title}'")
        print(f"   Expected Title: '{expected_title}'")
        
        # Verify the title matches what was generated
        assert stored_title == expected_title, f"Stored title '{stored_title}' doesn't match expected '{expected_title}'"
        
        return data
    else:
        print(f"❌ Failed to retrieve conversation: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Conversation retrieval failed")

def test_second_message_no_title_change(conversation_id: str, current_title: str):
    """Test that sending a second message doesn't change the title"""
    print(f"\n🧪 Testing second message (title should not change)...")
    
    second_question = "Can you explain that in more detail?"
    message_data = {"message": second_question}
    
    response = requests.post(f"{BACKEND_URL}/api/conversations/{conversation_id}/messages",
                           headers={"Content-Type": "application/json"},
                           json=message_data)
    
    if response.status_code == 200:
        data = response.json()
        returned_title = data.get("conversation_title")
        
        print(f"✅ Second message sent successfully!")
        print(f"   Current Title: '{returned_title}'")
        
        # Verify title didn't change
        assert returned_title == current_title, f"Title should not change on second message. Was '{current_title}', now '{returned_title}'"
        
        return data
    else:
        print(f"❌ Failed to send second message: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Second message sending failed")

def run_title_generation_test(question: str) -> bool:
    """Run a complete title generation test cycle"""
    print(f"\n{'='*60}")
    print(f"🎯 TITLE GENERATION TEST")
    print(f"   Question: '{question}'")
    print(f"{'='*60}")
    
    try:
        # Step 1: Create conversation
        conversation_id = test_conversation_creation()
        
        # Step 2: Send first message and generate title
        first_response = test_first_message_title_generation(conversation_id, question)
        generated_title = first_response["conversation_title"]
        
        # Step 3: Verify title persistence
        test_conversation_title_persistence(conversation_id, generated_title)
        
        # Step 4: Send second message and verify title doesn't change
        test_second_message_no_title_change(conversation_id, generated_title)
        
        print(f"\n🎉 All tests PASSED for question: '{question}'")
        print(f"   Final Title: '{generated_title}'")
        return True
        
    except Exception as e:
        print(f"\n💥 Test FAILED for question: '{question}'")
        print(f"   Error: {str(e)}")
        return False

def test_health_check():
    """Test if backend is running"""
    print("🏥 Checking backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy!")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def main():
    """Run all title generation tests"""
    print("🚀 Starting Title Generation Test Suite")
    print(f"   Backend URL: {BACKEND_URL}")
    print(f"   Test Questions: {len(TEST_QUESTIONS)}")
    
    # Check if backend is running
    if not test_health_check():
        print("\n💥 Backend is not running. Please start the backend server first.")
        print("   Run: python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload")
        return False
    
    # Run tests for each question
    passed = 0
    failed = 0
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n📋 Test {i}/{len(TEST_QUESTIONS)}")
        
        if run_title_generation_test(question):
            passed += 1
        else:
            failed += 1
        
        # Small delay between tests
        time.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! Title generation is working correctly.")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please check the backend implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)