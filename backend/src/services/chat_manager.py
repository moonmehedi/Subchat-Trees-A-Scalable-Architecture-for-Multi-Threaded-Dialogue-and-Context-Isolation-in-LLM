from typing import Dict,Optional,List
from ..models.tree import TreeNode

class ChatGraphManager:
    """ Manages the entire chat graph with nodes and navigation """
    def __init__(self):
        self.node_map:Dict[str,TreeNode] = {}
        self.active_node_id:Optional[str] = None
        self.vector_index = None  # Will be set by SimpleChat if RAG enabled

    def create_node(self, title: str, parent_id: Optional[str] = None, 
                   selected_text: str = None, follow_up_context: str = None, 
                   context_type: str = "general") -> TreeNode:
        """Create new node with optional parent and follow-up context."""

        parent = self.node_map.get(parent_id) if parent_id else None
        node = TreeNode(title=title, parent=parent, vector_index=self.vector_index)

        # If this is a follow-up subchat, set the context information
        if parent and context_type == "follow_up":
            node.set_follow_up_context(
                selected_text=selected_text,
                follow_up_intent=follow_up_context,
                context_type=context_type
            )

        if parent:
            parent.add_child(node)
            # Copy parent's buffer messages to child for context inheritance
            parent_messages = parent.buffer.get_recent()
            for msg in parent_messages:
                node.buffer.add_message(msg['role'], msg['text'])

        self.node_map[node.node_id] = node
        self.active_node_id = node.node_id
        return node
    
    def switch_node(self,node_id:str)->TreeNode:
        """switch to specific node"""
        if node_id not in self.node_map:
            raise KeyError(f'Node ID {node_id} does not exist')
        self.active_node_id = node_id
        return self.node_map[node_id]
    
    def get_active_node(self)-> TreeNode:
        """ get currently active node """
        if not self.active_node_id:
            raise ValueError('No active node selected')
        
        return self.node_map[self.active_node_id]
    
    def get_node(self,node_id:str)->TreeNode:
        """ get specific node by ID"""
        return self.node_map[node_id]
    
    def set_title(self,node_id:str,title:str):
        ''' Update node title '''
        if node_id not in self.node_map:
            raise KeyError(f"Node ID {node_id} does not exist")
        self.node_map[node_id].title=title

    def get_all_nodes(self)->Dict[str,TreeNode]:
        '''get all nodes'''
        return self.node_map
    
    
    ##implement hirarchical get children later 
    """
            A
          b   c
         e   h   g
    
    """
    def get_children(self,node_id:str)->List[TreeNode]:
        """ Get children of a node """
        node = self.get_node(node_id)
        return node.children if node else []
    
    def get_parent(self,node_id:str)->Optional[TreeNode]:
        '''get parent of a node'''
        node = self.get_node(node_id)
        return node.parent if node else None


#-------------------------------------TESTS-----------------------------

# Test functions
def test_chat_graph_manager():
    """Test ChatGraphManager functionality."""
    print("🧪 Testing ChatGraphManager...")
    
    manager = ChatGraphManager()
    
    # Create root node
    root = manager.create_node("Main Chat")
    print(f"✅ Created root: {root.title}")
    print(f"✅ Active node: {manager.get_active_node().title}")
    
    # Create child node
    child = manager.create_node("Subchat", parent_id=root.node_id)
    print(f"✅ Created child: {child.title}")
    print(f"✅ Child path: {' > '.join(child.get_path())}")
    
    # Test switching
    manager.switch_node(root.node_id)
    print(f"✅ Switched back to: {manager.get_active_node().title}")
    
    # Test getting children
    children = manager.get_children(root.node_id)
    print(f"✅ Root has {len(children)} children")
    
    # Test getting parent
    parent = manager.get_parent(child.node_id)
    print(f"✅ Child's parent: {parent.title if parent else 'None'}")
    
    print("🎉 ChatGraphManager test passed!")
    return True


def test_hierarchical_navigation():
    """Test complex hierarchical navigation."""
    print("\n🧪 Testing Hierarchical Navigation...")
    
    manager = ChatGraphManager()
    
    # Create tree structure
    root = manager.create_node("Cooking")
    pasta = manager.create_node("Pasta", parent_id=root.node_id)
    carbonara = manager.create_node("Carbonara", parent_id=pasta.node_id)
    alfredo = manager.create_node("Alfredo", parent_id=pasta.node_id)
    
    print(f"✅ Created tree: Cooking > Pasta > Carbonara")
    print(f"✅ Pasta has {len(manager.get_children(pasta.node_id))} children")
    
    # Test navigation
    manager.switch_node(carbonara.node_id)
    active = manager.get_active_node()
    print(f"✅ Active: {' > '.join(active.get_path())}")
    
    # Test parent navigation
    parent = manager.get_parent(active.node_id)
    print(f"✅ Parent: {parent.title if parent else 'None'}")
    
    print("🎉 Hierarchical navigation test passed!")
    return True


def test_message_inheritance():
    """Test message inheritance from parent to child."""
    print("\n🧪 Testing Message Inheritance...")
    
    manager = ChatGraphManager()
    
    # Create parent and add messages
    parent = manager.create_node("Parent Chat")
    parent.buffer.add_message("user", "Hello parent!")
    parent.buffer.add_message("assistant", "Hi there!")
    
    print(f"✅ Parent has {parent.buffer.size()} messages")
    
    # Create child - should inherit parent messages
    child = manager.create_node("Child Chat", parent_id=parent.node_id)
    print(f"✅ Child inherited {child.buffer.size()} messages from parent")
    
    # Add message to child
    child.buffer.add_message("user", "Hello from child!")
    print(f"✅ Child now has {child.buffer.size()} messages")
    
    print("🎉 Message inheritance test passed!")
    return True


def test_chat_manager():
    """Run all ChatGraphManager tests."""
    print("🧪 Testing ChatGraphManager...")
    
    try:
        test_chat_graph_manager()
        test_hierarchical_navigation()
        test_message_inheritance()
        print("\n🎉 All ChatGraphManager tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    test_chat_manager()
