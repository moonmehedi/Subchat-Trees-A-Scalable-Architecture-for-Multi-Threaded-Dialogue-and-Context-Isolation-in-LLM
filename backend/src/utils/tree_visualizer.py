"""
Real-time conversation tree visualizer for research documentation and debugging.
Generates both ASCII art trees and JSON structures for web visualization.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class ConversationTreeVisualizer:
    """Visualize conversation tree structure in multiple formats."""
    
    def __init__(self, log_dir: str = None):
        """Initialize visualizer with log directory."""
        if log_dir is None:
            # Default to backend/logs/tree_visualization/
            backend_dir = Path(__file__).parent.parent.parent
            log_dir = backend_dir / "logs" / "tree_visualization"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.ascii_log_file = self.log_dir / "conversation_tree.log"
        self.json_log_file = self.log_dir / "tree_structure.json"
    
    def build_tree_structure(self, root_node) -> Dict[str, Any]:
        """
        Build hierarchical tree structure from TreeNode.
        
        Args:
            root_node: TreeNode object (can be main or any subchat)
        
        Returns:
            Dictionary with tree structure and metadata
        """
        def node_to_dict(node) -> Dict[str, Any]:
            """Recursively convert TreeNode to dictionary."""
            return {
                'id': node.node_id,
                'title': node.title,
                'depth': len(node.get_path()) - 1,
                'path': node.get_path(),
                'message_count': len(node.buffer.turns),
                'has_summary': bool(node.buffer.summary),
                'children': [node_to_dict(child) for child in node.children],
                'metadata': {
                    'created_at': node.metadata.get('created_at', 'unknown'),
                    'is_subchat': node.parent is not None,
                    'follow_up_context': node.follow_up_context if hasattr(node, 'follow_up_context') else None
                }
            }
        
        return {
            'tree': node_to_dict(root_node),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_nodes': self._count_nodes(root_node),
                'max_depth': self._get_max_depth(root_node),
                'root_id': root_node.node_id,
                'root_title': root_node.title
            }
        }
    
    def _count_nodes(self, node) -> int:
        """Count total nodes in tree."""
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count
    
    def _get_max_depth(self, node, current_depth: int = 0) -> int:
        """Get maximum depth of tree."""
        if not node.children:
            return current_depth
        return max(self._get_max_depth(child, current_depth + 1) for child in node.children)
    
    def generate_ascii_tree(self, root_node, show_stats: bool = True) -> str:
        """
        Generate beautiful ASCII tree visualization.
        
        Args:
            root_node: TreeNode object
            show_stats: Whether to show statistics header
        
        Returns:
            ASCII art string
        """
        lines = []
        
        if show_stats:
            # Header with statistics
            lines.append("═" * 80)
            lines.append("        🌳 CONVERSATION TREE STRUCTURE")
            lines.append(f"        Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("═" * 80)
            lines.append("")
            
            total_nodes = self._count_nodes(root_node)
            max_depth = self._get_max_depth(root_node)
            lines.append(f"📊 Total Nodes: {total_nodes}")
            lines.append(f"📈 Max Depth: {max_depth}")
            lines.append(f"🏠 Root: {root_node.title}")
            lines.append("")
            lines.append("─" * 80)
            lines.append("")
        
        # Generate tree
        def render_node(node, prefix: str = "", is_last: bool = True, is_root: bool = True):
            """Recursively render node and its children."""
            node_lines = []
            
            # Determine the connector
            if is_root:
                connector = "🌳 "
                new_prefix = ""
            else:
                connector = "└─ " if is_last else "├─ "
                new_prefix = prefix + ("   " if is_last else "│  ")
            
            # Get emoji based on depth
            emoji = self._get_node_emoji(node)
            
            # Build node line
            msg_count = len(node.buffer.turns)
            child_count = len(node.children)
            
            node_info = f"{emoji} {node.title}"
            if msg_count > 0:
                node_info += f" ({msg_count} msgs)"
            if child_count > 0:
                node_info += f" [{child_count} subchats]"
            
            node_lines.append(f"{prefix}{connector}{node_info}")
            
            # Render children
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                node_lines.extend(render_node(child, new_prefix, is_last_child, False))
            
            return node_lines
        
        tree_lines = render_node(root_node)
        lines.extend(tree_lines)
        
        return "\n".join(lines)
    
    def _get_node_emoji(self, node) -> str:
        """Get emoji based on node characteristics."""
        if node.parent is None:
            return "📝"  # Root conversation
        
        depth = len(node.get_path()) - 1
        
        # Different emojis for different depths
        emoji_map = {
            1: "🌿",  # First level subchat
            2: "🍃",  # Second level
            3: "🌱",  # Third level
            4: "💬",  # Fourth level
        }
        
        return emoji_map.get(depth, "💬")
    
    def generate_json_tree(self, root_node) -> str:
        """
        Generate JSON representation of tree.
        
        Args:
            root_node: TreeNode object
        
        Returns:
            JSON string
        """
        tree_structure = self.build_tree_structure(root_node)
        return json.dumps(tree_structure, indent=2)
    
    def save_ascii_tree(self, root_node, append: bool = False):
        """
        Save ASCII tree to log file.
        
        Args:
            root_node: TreeNode object
            append: Whether to append or overwrite
        """
        ascii_tree = self.generate_ascii_tree(root_node, show_stats=True)
        
        mode = 'a' if append else 'w'
        with open(self.ascii_log_file, mode, encoding='utf-8') as f:
            if append:
                f.write("\n" + "─" * 80 + "\n\n")
            f.write(ascii_tree)
            f.write("\n\n")
        
        return str(self.ascii_log_file)
    
    def save_json_tree(self, root_node):
        """
        Save JSON tree to file.
        
        Args:
            root_node: TreeNode object
        """
        json_tree = self.generate_json_tree(root_node)
        
        with open(self.json_log_file, 'w', encoding='utf-8') as f:
            f.write(json_tree)
        
        return str(self.json_log_file)
    
    def save_all_trees(self, root_nodes: List, mode: str = 'overwrite'):
        """
        Save multiple conversation trees.
        
        Args:
            root_nodes: List of TreeNode objects (root conversations)
            mode: 'overwrite' or 'append'
        """
        # Generate combined ASCII tree
        lines = []
        lines.append("═" * 80)
        lines.append("        🌳 ALL CONVERSATION TREES")
        lines.append(f"        Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("═" * 80)
        lines.append("")
        lines.append(f"📊 Total Conversations: {len(root_nodes)}")
        
        total_nodes = sum(self._count_nodes(node) for node in root_nodes)
        lines.append(f"📈 Total Nodes: {total_nodes}")
        lines.append("")
        lines.append("─" * 80)
        lines.append("")
        
        # Add each tree
        for i, root in enumerate(root_nodes, 1):
            lines.append(f"\n🌳 Conversation {i}: {root.title}")
            lines.append("─" * 80)
            tree_ascii = self.generate_ascii_tree(root, show_stats=False)
            lines.append(tree_ascii)
            lines.append("")
        
        # Save ASCII
        write_mode = 'w' if mode == 'overwrite' else 'a'
        with open(self.ascii_log_file, write_mode, encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        # Save JSON (all trees)
        all_trees = {
            'conversations': [self.build_tree_structure(root) for root in root_nodes],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_conversations': len(root_nodes),
                'total_nodes': total_nodes
            }
        }
        
        with open(self.json_log_file, 'w', encoding='utf-8') as f:
            json.dump(all_trees, f, indent=2)
        
        return {
            'ascii_file': str(self.ascii_log_file),
            'json_file': str(self.json_log_file)
        }
    
    def print_tree(self, root_node):
        """Print ASCII tree to console."""
        print(self.generate_ascii_tree(root_node))
    
    def get_tree_stats(self, root_node) -> Dict[str, Any]:
        """Get statistics about the tree."""
        return {
            'total_nodes': self._count_nodes(root_node),
            'max_depth': self._get_max_depth(root_node),
            'root_title': root_node.title,
            'root_id': root_node.node_id,
            'child_count': len(root_node.children)
        }


# Global singleton instance
_visualizer_instance = None

def get_tree_visualizer(log_dir: str = None) -> ConversationTreeVisualizer:
    """Get or create global tree visualizer instance."""
    global _visualizer_instance
    if _visualizer_instance is None:
        _visualizer_instance = ConversationTreeVisualizer(log_dir)
    return _visualizer_instance
