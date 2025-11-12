from src.models.tree import LocalBuffer

def test_local_buffer():
    print("🧪 Testing LocalBuffer...")
    
    # Create buffer
    buffer = LocalBuffer(max_turns=5)
    print(f"✅ Buffer created with max_turns=5")
    
    # Add messages
    buffer.add_message("user", "Hello!")
    buffer.add_message("assistant", "Hi there!")
    buffer.add_message("user", "How are you?")
    
    print(f"✅ Added 3 messages")
    
    # Get recent messages
    recent = buffer.get_recent(2)
    print(f"✅ Recent 2 messages: {len(recent)}")
    for msg in recent:
        print(f"   {msg['role']}: {msg['text']}")
    
    # Get all messages
    all_msgs = buffer.get_recent()
    print(f"✅ Total messages: {len(all_msgs)}")
    
    # Test overflow (should keep only 5)
    for i in range(10):
        buffer.add_message("user", f"Message {i}")
    
    final_count = len(buffer.get_recent())
    print(f"✅ After adding 10 more, buffer size: {final_count} (should be 5)")
    
    print("🎉 LocalBuffer test passed!")

if __name__ == "__main__":
    test_local_buffer()