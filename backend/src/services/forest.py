from typing import Dict,Optional,List
from .chat_manager import ChatGraphManager
from ..models.tree import TreeNode

class Forest:
    """Manage multiple root-level trees (e.g., multiple main conversation) """

    def __init__(self):
        # all roots are stored here tree head
        self.trees_map:Dict[str,TreeNode] = {}
        self.active_tree_id:Optional[str] = None

    def create_tree(self, title: str = "Root Conversations", chat_manager: Optional[ChatGraphManager] = None, buffer_size: int = 15) -> TreeNode:
        """ create new root-level conversation tree and coordinate with chat manager. """
        # Get vector_index and llm_client from chat_manager if available
        vector_index = chat_manager.vector_index if chat_manager else None
        llm_client = chat_manager.llm_client if chat_manager else None
        
        # 🔧 Pass buffer_size to TreeNode
        root = TreeNode(
            title=title, 
            vector_index=vector_index, 
            llm_client=llm_client,
            buffer_size=buffer_size  # ← NEW: Accept buffer_size parameter
        )
        
        self.trees_map[root.node_id] = root
        self.active_tree_id = root.node_id

        #auto-sync with chat manager if provided
        if chat_manager:
            chat_manager.node_map[root.node_id] = root
            chat_manager.active_node_id = root.node_id

        return root
    
    def switch_tree(self,tree_id:str)->TreeNode:
        """switch active tree"""
        if tree_id not in self.trees_map:
            raise KeyError(f' tree ID {tree_id} not found ')
        
        self.active_tree_id=tree_id
        return self.trees_map[tree_id]


    def get_active_tree(self)-> TreeNode:
        '''get currently active tree .'''
        if not self.active_tree_id:
            raise ValueError("No active tree selected ")
        return self.trees_map[self.active_tree_id]
    
    def set_title(self,tree_id:str,title:str):
        '''update tree title '''
        if tree_id not in self.trees_map:
            raise KeyError(f'Tree ID {tree_id} does not exist ')
        self.trees_map[tree_id].title = title

    def get_all_trees(self)->Dict[str,TreeNode]:
        """Get all trees"""
        return self.trees_map
    
    def get_tree_count(self)->int:
        """get total numbers of trees"""
        return len(self.trees_map)
    

    def delete_tree(self,tree_id:str):
        """delete a tree and set acitive tree as the first one in the tree map"""
        if tree_id not in self.trees_map:
            raise KeyError(f'Tree ID {tree_id} does not exist')
        
        # if deleteign active trees ,switch to anoterh tree if available

        if tree_id == self.active_tree_id:
            remaining_trees = [tid for tid in self.trees_map.keys() if tid!=tree_id]
            if remaining_trees:
                self.active_tree_id = remaining_trees[0]
            else:
                self.active_tree_id = None
        del self.trees_map[tree_id]


#-------------------------------------TESTS-----------------------------

def test_forest_creation():
    """Test Forest creation and basic functionality."""
    print("🧪 Testing Forest Creation...")
    
    forest = Forest()
    
    # Test initial state
    assert forest.get_tree_count() == 0, "Forest should start empty"
    assert forest.active_tree_id is None, "No active tree initially"
    print("✅ Forest starts empty")
    
    # Create first tree
    tree1 = forest.create_tree("Cooking Discussions")
    assert forest.get_tree_count() == 1, "Should have 1 tree"
    assert forest.active_tree_id == tree1.node_id, "First tree should be active"
    assert tree1.title == "Cooking Discussions", "Tree title should match"
    print("✅ First tree created and active")
    
    # Create second tree
    tree2 = forest.create_tree("Travel Planning")
    assert forest.get_tree_count() == 2, "Should have 2 trees"
    assert forest.active_tree_id == tree2.node_id, "Second tree should be active"
    print("✅ Second tree created and became active")
    
    # Test getting active tree
    active = forest.get_active_tree()
    assert active.node_id == tree2.node_id, "Active tree should match"
    print("✅ Active tree retrieval works")
    
    print("🎉 Forest creation test passed!")
    return True


def test_forest_navigation():
    """Test Forest navigation between trees."""
    print("\n🧪 Testing Forest Navigation...")
    
    forest = Forest()
    
    # Create multiple trees
    cooking = forest.create_tree("Cooking")
    travel = forest.create_tree("Travel")
    coding = forest.create_tree("Coding")
    
    assert forest.get_tree_count() == 3, "Should have 3 trees"
    
    # Test switching to specific tree
    forest.switch_tree(cooking.node_id)
    active = forest.get_active_tree()
    assert active.node_id == cooking.node_id, "Should switch to cooking tree"
    assert active.title == "Cooking", "Active tree title should match"
    print("✅ Tree switching works")
    
    # Test switching to another tree
    forest.switch_tree(travel.node_id)
    active = forest.get_active_tree()
    assert active.node_id == travel.node_id, "Should switch to travel tree"
    print("✅ Multiple tree switches work")
    
    # Test invalid tree switch
    try:
        forest.switch_tree("invalid-id")
        assert False, "Should raise KeyError for invalid tree ID"
    except KeyError:
        print("✅ Invalid tree ID properly rejected")
    
    print("🎉 Forest navigation test passed!")
    return True


def test_forest_with_chat_manager():
    """Test Forest integration with ChatGraphManager."""
    print("\n🧪 Testing Forest + ChatGraphManager Integration...")
    
    from .chat_manager import ChatGraphManager
    
    forest = Forest()
    chat_manager = ChatGraphManager()
    
    # Create tree through forest
    tree = forest.create_tree("Integrated Chat", chat_manager=chat_manager)
    
    # Verify sync
    assert tree.node_id in chat_manager.node_map, "Tree should be in chat manager"
    assert chat_manager.active_node_id == tree.node_id, "Chat manager should have same active node"
    print("✅ Forest-ChatManager sync works")
    
    # Create subchat through chat manager
    subchat = chat_manager.create_node("Subtopic", parent_id=tree.node_id)
    
    # Verify hierarchy
    assert len(tree.children) == 1, "Tree should have 1 child"
    assert tree.children[0].node_id == subchat.node_id, "Child should match subchat"
    assert subchat.parent.node_id == tree.node_id, "Subchat parent should be tree"
    print("✅ Hierarchical chat creation works")
    
    # Test path
    path = subchat.get_path()
    assert path == ["Integrated Chat", "Subtopic"], f"Path should be correct, got {path}"
    print(f"✅ Path navigation: {' > '.join(path)}")
    
    print("🎉 Forest-ChatManager integration test passed!")
    return True


def test_forest_operations():
    """Test Forest operations like deletion and title updates."""
    print("\n🧪 Testing Forest Operations...")
    
    forest = Forest()
    
    # Create trees
    tree1 = forest.create_tree("Original Title")
    tree2 = forest.create_tree("Second Tree")
    tree3 = forest.create_tree("Third Tree")
    
    assert forest.get_tree_count() == 3, "Should have 3 trees"
    
    # Test title update
    forest.set_title(tree1.node_id, "Updated Title")
    # Get the specific tree we updated, not the active one
    updated_tree = forest.trees_map[tree1.node_id]
    assert updated_tree.title == "Updated Title", "Title should be updated"
    print("✅ Title update works")
    
    # Test deletion (non-active tree)
    forest.delete_tree(tree2.node_id)
    assert forest.get_tree_count() == 2, "Should have 2 trees after deletion"
    assert tree2.node_id not in forest.trees_map, "Deleted tree should not exist"
    print("✅ Tree deletion works")
    
    # Test deletion of active tree
    active_before = forest.active_tree_id
    forest.delete_tree(active_before)
    assert forest.get_tree_count() == 1, "Should have 1 tree after deleting active"
    assert forest.active_tree_id != active_before, "Active tree should change after deletion"
    print("✅ Active tree deletion and auto-switch works")
    
    # Test deleting last tree
    last_tree_id = list(forest.trees_map.keys())[0]
    forest.delete_tree(last_tree_id)
    assert forest.get_tree_count() == 0, "Should have 0 trees"
    assert forest.active_tree_id is None, "No active tree when empty"
    print("✅ Last tree deletion works")
    
    print("🎉 Forest operations test passed!")
    return True


def test_forest():
    """Run all Forest tests."""
    print("🧪 Testing Forest (Multiple Conversation Trees)...")
    
    try:
        test_forest_creation()
        test_forest_navigation()
        test_forest_with_chat_manager()
        test_forest_operations()
        print("\n🎉 All Forest tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_forest()



    