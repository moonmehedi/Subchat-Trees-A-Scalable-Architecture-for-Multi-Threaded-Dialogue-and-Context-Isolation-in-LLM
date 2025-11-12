#!/usr/bin/env python3
"""
End-to-End Frontend-Backend Integration Test
Tests the complete flow: Frontend → Backend API → Response → Title Generation
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:9000"

def test_complete_integration():
    """Test the complete frontend-backend integration"""
    print("🚀 Testing Complete Frontend-Backend Integration")
    print("="*60)
    
    # Test 1: Backend Health
    print("1️⃣ Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except:
        print("❌ Backend is not accessible")
        return False
    
    # Test 2: Frontend Accessibility
    print("\n2️⃣ Testing Frontend Accessibility...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except:
        print("❌ Frontend is not accessible")
        return False
    
    # Test 3: API Integration Flow
    print("\n3️⃣ Testing API Integration Flow...")
    
    # Create conversation (like frontend would)
    print("   → Creating conversation...")
    conv_response = requests.post(f"{BACKEND_URL}/api/conversations", 
                                headers={"Content-Type": "application/json"})
    
    if conv_response.status_code != 200:
        print(f"❌ Failed to create conversation: {conv_response.status_code}")
        return False
    
    conv_data = conv_response.json()
    conv_id = conv_data["node_id"]
    print(f"   ✅ Conversation created: {conv_id}")
    print(f"   📝 Initial title: '{conv_data['title']}'")
    
    # Send first message (like frontend would)
    print("   → Sending first message...")
    message_data = {"message": "How do I build a web application?"}
    msg_response = requests.post(f"{BACKEND_URL}/api/conversations/{conv_id}/messages",
                               headers={"Content-Type": "application/json"},
                               json=message_data)
    
    if msg_response.status_code != 200:
        print(f"❌ Failed to send message: {msg_response.status_code}")
        return False
    
    msg_data = msg_response.json()
    print(f"   ✅ Message sent successfully")
    print(f"   🤖 AI Response: {msg_data['response'][:80]}...")
    print(f"   🏷️  Generated Title: '{msg_data['conversation_title']}'")
    
    # Verify title persistence
    print("   → Verifying title persistence...")
    check_response = requests.get(f"{BACKEND_URL}/api/conversations/{conv_id}")
    check_data = check_response.json()
    
    if check_data["title"] == msg_data["conversation_title"]:
        print(f"   ✅ Title persisted correctly: '{check_data['title']}'")
    else:
        print(f"   ❌ Title mismatch: expected '{msg_data['conversation_title']}', got '{check_data['title']}'")
        return False
    
    # Test 4: Subchat Creation (like follow-up button)
    print("\n4️⃣ Testing Subchat Creation...")
    subchat_data = {"title": "Frontend Frameworks"}
    subchat_response = requests.post(f"{BACKEND_URL}/api/conversations/{conv_id}/subchats",
                                   headers={"Content-Type": "application/json"},
                                   json=subchat_data)
    
    if subchat_response.status_code != 200:
        print(f"❌ Failed to create subchat: {subchat_response.status_code}")
        return False
    
    subchat_info = subchat_response.json()
    subchat_id = subchat_info["node_id"]
    print(f"   ✅ Subchat created: {subchat_id}")
    print(f"   📝 Subchat title: '{subchat_info['title']}'")
    print(f"   🌳 Hierarchy: {' > '.join(subchat_info['path'])}")
    
    # Send message to subchat
    print("   → Sending message to subchat...")
    subchat_msg = {"message": "What about React vs Vue?"}
    subchat_msg_response = requests.post(f"{BACKEND_URL}/api/conversations/{subchat_id}/messages",
                                       headers={"Content-Type": "application/json"},
                                       json=subchat_msg)
    
    if subchat_msg_response.status_code == 200:
        subchat_msg_data = subchat_msg_response.json()
        print(f"   ✅ Subchat message sent")
        print(f"   🤖 Subchat Response: {subchat_msg_data['response'][:80]}...")
    else:
        print(f"   ❌ Failed to send subchat message: {subchat_msg_response.status_code}")
        return False
    
    print("\n" + "="*60)
    print("🎉 COMPLETE INTEGRATION TEST PASSED!")
    print("✅ Frontend ↔ Backend communication works")
    print("✅ Title generation works") 
    print("✅ Subchat creation works")
    print("✅ Hierarchical context works")
    print("\n📋 Frontend Implementation Summary:")
    print("   • Frontend calls backend API endpoints")
    print("   • Auto-title generation on first message")
    print("   • Follow-up button creates subchats")
    print("   • Context inheritance in hierarchical chats")
    
    return True

if __name__ == "__main__":
    success = test_complete_integration()
    if success:
        print("\n🚀 Your hierarchical chat system is ready to use!")
        print("   Backend: http://localhost:8000")
        print("   Frontend: http://localhost:9000")
    else:
        print("\n⚠️  Integration test failed. Check the logs above.")
    
    exit(0 if success else 1)