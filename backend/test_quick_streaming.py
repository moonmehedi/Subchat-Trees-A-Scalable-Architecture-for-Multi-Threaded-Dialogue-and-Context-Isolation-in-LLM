#!/usr/bin/env python3
"""
Quick test to verify streaming is working from frontend
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:9000"

def test_quick_streaming():
    """Quick test to verify streaming works"""
    print("🧪 Quick Streaming Test")
    print("=" * 40)
    
    # Test backend health
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print("✅ Backend healthy")
    except:
        print("❌ Backend not accessible")
        return
    
    # Test frontend
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        print("✅ Frontend accessible")
    except:
        print("❌ Frontend not accessible")
        return
    
    # Create conversation
    conv_response = requests.post(f"{BACKEND_URL}/api/conversations")
    if conv_response.status_code != 200:
        print("❌ Failed to create conversation")
        return
    
    conv_id = conv_response.json()["node_id"]
    print(f"✅ Conversation: {conv_id}")
    
    # Test streaming
    print("\n🔄 Testing streaming...")
    response = requests.post(
        f"{BACKEND_URL}/api/conversations/{conv_id}/messages/stream",
        headers={"Content-Type": "application/json"},
        json={"message": "Say hello!"},
        stream=True
    )
    
    if response.status_code == 200:
        print("✅ Streaming endpoint responding")
        chunk_count = 0
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if data['type'] == 'token':
                        chunk_count += 1
                        if chunk_count <= 5:  # Show first 5 chunks
                            print(f"   📡 Token {chunk_count}: '{data['content']}'")
                    elif data['type'] == 'done':
                        print(f"✅ Streaming complete! {chunk_count} tokens received")
                        break
                except:
                    pass
    else:
        print(f"❌ Streaming failed: {response.status_code}")
    
    print("\n🎯 To test in UI:")
    print(f"   • Open: {FRONTEND_URL}")
    print("   • Send a message")
    print("   • Watch for token-by-token streaming!")

if __name__ == "__main__":
    test_quick_streaming()