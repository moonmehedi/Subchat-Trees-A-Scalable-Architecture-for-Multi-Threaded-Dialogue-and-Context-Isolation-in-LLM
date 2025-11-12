#!/usr/bin/env python3
"""
Test streaming endpoint with markdown formatting
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_streaming_endpoint():
    """Test the streaming endpoint with markdown content"""
    print("🧪 Testing Streaming Endpoint with Markdown")
    print("="*50)
    
    # Test 1: Create conversation
    print("1️⃣ Creating conversation...")
    conv_response = requests.post(f"{BACKEND_URL}/api/conversations")
    if conv_response.status_code != 200:
        print(f"❌ Failed to create conversation: {conv_response.status_code}")
        return False
    
    conv_data = conv_response.json()
    conv_id = conv_data["node_id"]
    print(f"✅ Conversation created: {conv_id}")
    
    # Test 2: Send message with streaming
    print("\n2️⃣ Testing streaming response...")
    message_data = {"message": "Write a 500-word essay about ### QUANTUM COMPUTING with **bold** text, `code examples`, and proper markdown formatting. Include multiple paragraphs and technical details."}
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/conversations/{conv_id}/messages/stream",
            json=message_data,
            headers={"Accept": "text/event-stream"},
            stream=True
        )
        
        if response.status_code != 200:
            print(f"❌ Streaming request failed: {response.status_code}")
            return False
        
        print("✅ Streaming response received:")
        print("-" * 30)
        
        full_content = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        if data['type'] == 'token':
                            full_content += data['content']
                            print(data['content'], end='', flush=True)
                        elif data['type'] == 'title':
                            print(f"\n\n🏷️ Generated title: {data['content']}")
                        elif data['type'] == 'done':
                            print(f"\n\n✅ Streaming completed!")
                            break
                        elif data['type'] == 'error':
                            print(f"\n❌ Error: {data['content']}")
                            return False
                    except json.JSONDecodeError:
                        continue
        
        print(f"\n📊 Total characters streamed: {len(full_content)}")
        
        # Test 3: Verify conversation history
        print("\n3️⃣ Verifying conversation history...")
        history_response = requests.get(f"{BACKEND_URL}/api/conversations/{conv_id}/history")
        if history_response.status_code == 200:
            history = history_response.json()
            print(f"✅ History retrieved: {len(history['messages'])} messages")
            print("✅ Streaming integration test PASSED!")
            return True
        else:
            print(f"❌ Failed to get history: {history_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_streaming_endpoint()
    if success:
        print("\n🎉 All streaming tests passed!")
    else:
        print("\n💥 Streaming tests failed!")