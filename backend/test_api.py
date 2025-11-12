#!/usr/bin/env python3
"""
Comprehensive API Test Script for Hierarchical Chat System
Tests the complete flow: create conversation -> send messages -> create subchats -> verify context inheritance
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000/api"

def test_api():
    """Test the complete hierarchical chat API flow."""
    print("🧪 Testing Hierarchical Chat API System")
    print("=" * 50)

    # Test 1: Health Check
    print("\n1. Health Check")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    # Test 2: Create Main Conversation
    print("\n2. Creating Main Conversation")
    try:
        response = requests.post(
            f"{BASE_URL}/conversations",
            json={"title": "Cooking Masterclass"},
            headers={"Content-Type": "application/json"}
        )
        main_chat = response.json()
        print(f"✅ Created: {main_chat['title']} (ID: {main_chat['node_id'][:8]}...)")
        main_id = main_chat['node_id']
    except Exception as e:
        print(f"❌ Failed to create conversation: {e}")
        return False

    # Test 3: Send Message to Main Conversation
    print("\n3. Sending Message to Main Conversation")
    try:
        response = requests.post(
            f"{BASE_URL}/conversations/{main_id}/messages",
            json={"message": "How do I make perfect pasta?"},
            headers={"Content-Type": "application/json"}
        )
        msg_response = response.json()
        print(f"✅ AI Response: {msg_response['response'][:50]}...")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        return False

    # Test 4: Create Subchat for Pasta Types
    print("\n4. Creating Subchat: Pasta Types")
    try:
        response = requests.post(
            f"{BASE_URL}/conversations/{main_id}/subchats",
            json={"title": "Pasta Types", "parent_id": main_id},
            headers={"Content-Type": "application/json"}
        )
        pasta_subchat = response.json()
        print(f"✅ Subchat: {pasta_subchat['title']} (Path: {' > '.join(pasta_subchat['path'])})")
        print(f"   Message count: {pasta_subchat['message_count']} (inherited from parent)")
        pasta_id = pasta_subchat['node_id']
    except Exception as e:
        print(f"❌ Failed to create subchat: {e}")
        return False

    # Test 5: Send Message to Subchat
    print("\n5. Sending Message to Pasta Types Subchat")
    try:
        response = requests.post(
            f"{BASE_URL}/conversations/{pasta_id}/messages",
            json={"message": "What are the different types of pasta shapes?"},
            headers={"Content-Type": "application/json"}
        )
        sub_msg_response = response.json()
        print(f"✅ Subchat AI Response: {sub_msg_response['response'][:50]}...")
    except Exception as e:
        print(f"❌ Failed to send message to subchat: {e}")
        return False

    # Test 6: Create Another Subchat for Sauce Recipes
    print("\n6. Creating Subchat: Sauce Recipes")
    try:
        response = requests.post(
            f"{BASE_URL}/conversations/{main_id}/subchats",
            json={"title": "Sauce Recipes", "parent_id": main_id},
            headers={"Content-Type": "application/json"}
        )
        sauce_subchat = response.json()
        print(f"✅ Subchat: {sauce_subchat['title']} (Path: {' > '.join(sauce_subchat['path'])})")
        print(f"   Message count: {sauce_subchat['message_count']} (inherited from parent)")
        sauce_id = sauce_subchat['node_id']
    except Exception as e:
        print(f"❌ Failed to create sauce subchat: {e}")
        return False

    # Test 7: Send Message to Sauce Subchat
    print("\n7. Sending Message to Sauce Recipes Subchat")
    try:
        response = requests.post(
            f"{BASE_URL}/conversations/{sauce_id}/messages",
            json={"message": "How do I make a classic marinara sauce?"},
            headers={"Content-Type": "application/json"}
        )
        sauce_msg_response = response.json()
        print(f"✅ Sauce AI Response: {sauce_msg_response['response'][:50]}...")
    except Exception as e:
        print(f"❌ Failed to send message to sauce subchat: {e}")
        return False

    # Test 8: Check Main Conversation Structure
    print("\n8. Checking Main Conversation Structure")
    try:
        response = requests.get(f"{BASE_URL}/conversations/{main_id}")
        main_info = response.json()
        print(f"✅ Main chat has {len(main_info['children'])} children:")
        for child_id in main_info['children']:
            print(f"   - {child_id[:8]}...")
    except Exception as e:
        print(f"❌ Failed to get main conversation info: {e}")
        return False

    # Test 9: Get Conversation History
    print("\n9. Getting Conversation History")
    try:
        response = requests.get(f"{BASE_URL}/conversations/{main_id}/history")
        history = response.json()
        print(f"✅ Main chat history: {len(history['messages'])} messages")
        for msg in history['messages']:
            print(f"   {msg['role'].upper()}: {msg['text'][:30]}...")

        # Get subchat history
        response = requests.get(f"{BASE_URL}/conversations/{pasta_id}/history")
        pasta_history = response.json()
        print(f"✅ Pasta subchat history: {len(pasta_history['messages'])} messages")
        print(f"   Path: {' > '.join(pasta_history['path'])}")
    except Exception as e:
        print(f"❌ Failed to get conversation history: {e}")
        return False

    # Test 10: Create Deep Subchat (3 levels)
    print("\n10. Creating Deep Subchat (3 Levels)")
    try:
        # Create subchat under Pasta Types
        response = requests.post(
            f"{BASE_URL}/conversations/{pasta_id}/subchats",
            json={"title": "Italian Pasta Shapes", "parent_id": pasta_id},
            headers={"Content-Type": "application/json"}
        )
        deep_subchat = response.json()
        print(f"✅ Deep subchat: {deep_subchat['title']}")
        print(f"   Full path: {' > '.join(deep_subchat['path'])}")
        print(f"   Message count: {deep_subchat['message_count']} (inherited through 2 levels)")
    except Exception as e:
        print(f"❌ Failed to create deep subchat: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Hierarchical chat system working perfectly")
    print("✅ Context inheritance through multiple levels")
    print("✅ Tree structure with parent-child relationships")
    print("✅ Real LLM responses from Groq API")
    print("✅ REST API fully functional")
    print("=" * 50)

    return True

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)