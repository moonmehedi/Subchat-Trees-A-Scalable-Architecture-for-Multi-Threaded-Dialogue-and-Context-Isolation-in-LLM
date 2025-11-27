"""
Test script for conversation tree visualization.
Creates sample conversations and subchats to test the visualization.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.tree import TreeNode
from src.services.chat_manager import ChatGraphManager
from src.utils.tree_visualizer import get_tree_visualizer


def test_tree_visualization():
    """Test tree visualization with sample data."""
    print("🧪 Testing Conversation Tree Visualization\n")
    print("=" * 80)
    
    # Create chat manager
    manager = ChatGraphManager()
    
    # Create first conversation tree
    print("\n📝 Creating first conversation: 'Planning Weekend Trip'")
    root1 = manager.create_node("Planning Weekend Trip")
    
    # Add subchats
    print("  🌿 Adding subchat: 'Hotel Options Discussion'")
    hotel_chat = manager.create_node("Hotel Options Discussion", parent_id=root1.node_id)
    
    print("  🌿 Adding subchat: 'Budget Analysis'")
    budget_chat = manager.create_node("Budget Analysis", parent_id=root1.node_id)
    
    # Add nested subchats
    print("    🍃 Adding nested subchat: 'Flight Prices'")
    flight_chat = manager.create_node("Flight Prices", parent_id=budget_chat.node_id)
    
    print("    🍃 Adding nested subchat: 'Accommodation Costs'")
    accom_chat = manager.create_node("Accommodation Costs", parent_id=budget_chat.node_id)
    
    # Add deeply nested
    print("      🌱 Adding deeply nested: 'Splitting Expenses'")
    split_chat = manager.create_node("Splitting Expenses", parent_id=accom_chat.node_id)
    
    print("  🌿 Adding subchat: 'Activities'")
    activities_chat = manager.create_node("Activities", parent_id=root1.node_id)
    
    # Create second conversation tree
    print("\n💻 Creating second conversation: 'Python Code Review'")
    root2 = manager.create_node("Python Code Review")
    
    print("  🌿 Adding subchat: 'Django Migration Help'")
    django_chat = manager.create_node("Django Migration Help", parent_id=root2.node_id)
    
    # Create third conversation tree
    print("\n🔬 Creating third conversation: 'Research Paper Draft'")
    root3 = manager.create_node("Research Paper Draft")
    
    print("\n" + "=" * 80)
    
    # Get visualizer
    visualizer = get_tree_visualizer()
    
    # Get all root nodes
    all_roots = manager.get_all_roots()
    
    print(f"\n📊 Statistics:")
    print(f"   Total Conversations: {len(all_roots)}")
    total_nodes = sum(visualizer._count_nodes(root) for root in all_roots)
    print(f"   Total Nodes: {total_nodes}")
    
    # Generate and print ASCII tree
    print("\n" + "=" * 80)
    print("🌳 ASCII TREE VISUALIZATION")
    print("=" * 80 + "\n")
    
    for i, root in enumerate(all_roots, 1):
        print(f"\n{'─' * 80}")
        print(f"Conversation {i}: {root.title}")
        print("─" * 80)
        print(visualizer.generate_ascii_tree(root, show_stats=False))
    
    # Save to files
    print("\n" + "=" * 80)
    print("💾 Saving to files...")
    result = visualizer.save_all_trees(all_roots, mode='overwrite')
    print(f"   ✅ ASCII saved to: {result['ascii_file']}")
    print(f"   ✅ JSON saved to: {result['json_file']}")
    
    # Print stats for each tree
    print("\n" + "=" * 80)
    print("📈 Tree Statistics:")
    print("=" * 80)
    for root in all_roots:
        stats = visualizer.get_tree_stats(root)
        print(f"\n  🌳 {root.title}")
        print(f"     Total Nodes: {stats['total_nodes']}")
        print(f"     Max Depth: {stats['max_depth']}")
        print(f"     Direct Children: {stats['child_count']}")
    
    print("\n" + "=" * 80)
    print("✅ Test completed successfully!")
    print("=" * 80)
    print(f"\n📂 View files at: backend/logs/tree_visualization/")
    print(f"🌐 Start server and visit: http://localhost:8000/api/tree/visualization")
    print("\n")


if __name__ == "__main__":
    test_tree_visualization()
