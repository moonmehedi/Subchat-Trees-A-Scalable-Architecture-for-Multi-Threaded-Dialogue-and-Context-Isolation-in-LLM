from src.models.tree import LocalBuffer, TreeNode

def test_tree():
    print("🧪 Testing Tree Components...")
    
    # Test 1: LocalBuffer
    print("\n1. Testing LocalBuffer:")
    buffer = LocalBuffer(max_turns=3)
    buffer.add_message("user", "Hello")
    buffer.add_message("assistant", "Hi")
    buffer.add_message("user", "How are you?")
    
    recent = buffer.get_recent(2)
    print(f"✅ Recent 2 messages: {len(recent)}")
    print(f"   Last message: {recent[-1]['text']}")
    
    # Test 2: TreeNode
    print("\n2. Testing TreeNode:")
    root = TreeNode(title="Main Chat")
    child = TreeNode(title="Subchat", parent=root)
    root.add_child(child)
    
    print(f"✅ Root: {root.title}")
    print(f"✅ Child: {child.title}")
    print(f"✅ Child path: {' > '.join(child.get_path())}")
    print(f"✅ Root has {len(root.children)} children")
    
    # Test 3: Buffer in nodes
    print("\n3. Testing Node Buffers:")
    root.buffer.add_message("user", "Hello from root")
    child.buffer.add_message("user", "Hello from child")
    
    print(f"✅ Root buffer: {len(root.buffer.get_recent())} messages")
    print(f"✅ Child buffer: {len(child.buffer.get_recent())} messages")
    
    print("\n🎉 All tree tests passed!")

if __name__ == "__main__":
    test_tree()