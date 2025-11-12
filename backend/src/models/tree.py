from typing import Optional, List, Dict, Any
import uuid
import time
from collections import deque
from src.utils.debug_logger import get_debug_logger

class LocalBuffer:
    """Fixed-size message buffer per conversation node with auto-archiving."""

    def __init__(self, max_turns: int = 50, vector_index=None, node_id: str = None):
        self.turns: deque[Dict[str, Any]] = deque(maxlen=max_turns)
        self.vector_index = vector_index  # Reference to global vector index
        self.node_id = node_id  # Node ID for archiving
        self.max_turns = max_turns

    def add_message(self, role: str, text: str, auto_archive: bool = True):
        """
        Add message with timestamp and immediate indexing to vector DB.
        
        Strategy:
        1. Create timestamp ONCE (use same timestamp for both buffer and index!)
        2. Index message to vector DB immediately (for cross-conversation search)
        3. Add to buffer (evicts oldest if full)
        4. Show debug info about buffer state
        
        This ensures messages are searchable even if user switches conversations
        before buffer fills up.
        """
        # Create timestamp ONCE to ensure consistency between buffer and index
        msg_timestamp = time.time()
        
        # 1. INDEX IMMEDIATELY to vector DB (so it's searchable across conversations)
        if auto_archive and self.vector_index and self.node_id:
            try:
                self.vector_index.index_message(
                    node_id=self.node_id,
                    message=text,
                    metadata={
                        'role': role,
                        'timestamp': msg_timestamp,  # ← Use SAME timestamp!
                        'indexed_immediately': True  # Flag for debugging
                    }
                )
                print(f"💾 Indexed: [{role}] {text[:40]}{'...' if len(text) > 40 else ''}")
            except Exception as e:
                print(f"⚠️  Failed to index message: {e}")
        
        # 2. Check if buffer is full - show what will be evicted
        if len(self.turns) == self.turns.maxlen:
            evicted_message = self.turns[0]
            print(f"🔄 Buffer full - evicting: {evicted_message['text'][:40]}{'...' if len(evicted_message['text']) > 40 else ''}")
        
        # 3. Add new message to buffer with SAME timestamp as index
        self.turns.append({
            'role': role,
            'text': text,
            'timestamp': msg_timestamp  # ← Use SAME timestamp!
        })
        
        # 4. Log buffer state to BOTH loggers
        logger_overwrite = get_debug_logger(append_mode=False)  # For user viewing
        logger_append = get_debug_logger(append_mode=True)      # For full debugging
        
        for logger in [logger_overwrite, logger_append]:
            logger.log_buffer(
                node_id=self.node_id,
                buffer_messages=list(self.turns),
                max_turns=self.max_turns
            )
        
        # 5. Show brief buffer state in terminal (last 3 messages)
        print(f"📋 Buffer ({self.size()}/{self.max_turns}): Last 3 messages (full log in file)")
        recent_3 = list(self.turns)[-3:]
        for i, msg in enumerate(recent_3, 1):
            msg_preview = msg['text'][:50] + ('...' if len(msg['text']) > 50 else '')
            print(f"   {i}. [{msg['role']}] {msg_preview}")
    
    def _archive_message(self, message: Dict[str, Any]):
        """
        DEPRECATED: Messages are now indexed immediately in add_message().
        This method kept for backward compatibility.
        """
        pass  # No longer needed - indexing happens immediately

    def get_recent(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent n messages."""
        return list(self.turns)[-n:] if n is not None else list(self.turns)
    
    def get_cutoff_timestamp(self, exclude_recent: int = None) -> float:
        """
        Get timestamp to exclude messages currently in buffer from retrieval.
        
        This ensures we don't retrieve messages that are already available
        in the buffer (avoiding redundancy).
        
        Logic: Returns timestamp of OLDEST message in buffer.
        Retrieval will exclude messages with timestamp >= this value,
        effectively excluding ALL messages in the buffer.
        
        Args:
            exclude_recent: Number of recent messages to exclude (default: all buffer messages)
        
        Returns:
            Timestamp cutoff - messages with timestamp >= this are in buffer and should be excluded
        """
        if not self.turns:
            return float('inf')  # No messages in buffer, don't exclude anything
        
        # By default, exclude ALL messages in buffer
        if exclude_recent is None:
            exclude_recent = len(self.turns)
        
        # If buffer has fewer messages than requested, exclude all
        if len(self.turns) <= exclude_recent:
            # Return timestamp of OLDEST message in buffer
            # Retrieval logic: msg_timestamp >= cutoff means "in buffer, skip it"
            # So this excludes all messages from oldest to newest in buffer
            oldest_msg = list(self.turns)[0]
            oldest_timestamp = oldest_msg['timestamp']
            return oldest_timestamp
        
        # Return timestamp to exclude last N messages
        # (timestamp of the Nth message from the end)
        return list(self.turns)[-exclude_recent]['timestamp']
    
    def get_buffer_messages(self) -> List[str]:
        """Get list of message texts currently in buffer (for debugging/comparison)"""
        return [msg['text'] for msg in self.turns]
    
    def clear(self, n: int = None):
        """Clear last n messages from buffer, or all if n is None."""
        if n is None:
            self.turns.clear()
        else:
            for _ in range(min(n, len(self.turns))):
                self.turns.pop()
    
    def size(self) -> int:
        """Get current buffer size."""
        return len(self.turns)


class TreeNode:
    """Hierarchical conversation node."""

    def __init__(self, node_id: Optional[str] = None, title: str = 'Untitled', parent: Optional['TreeNode'] = None, vector_index=None):
        self.node_id: str = node_id if node_id else str(uuid.uuid4())
        self.title: str = title
        self.parent: Optional['TreeNode'] = parent
        self.children: List['TreeNode'] = []
        self.buffer: LocalBuffer = LocalBuffer(max_turns=10, vector_index=vector_index, node_id=self.node_id)
        self.metadata: Dict[str, Any] = {}
        
        # Follow-up context fields - store information about what this subchat focuses on
        self.follow_up_context: Optional[Dict[str, Any]] = {
            'selected_text': None,      # Text that was selected from parent to create this subchat
            'follow_up_intent': None,   # What the user wants to explore about the selected text
            'context_type': 'general'   # Type of conversation (follow_up, new_topic, etc.)
        }

    def get_path(self) -> List[str]:
        """Get path from root to this node."""
        path = []
        current = self
        while current:
            path.append(current.title)
            current = current.parent
        return list(reversed(path))
    
    def add_child(self, child_node: 'TreeNode'):
        """Add child and set parent relationship."""
        self.children.append(child_node)
        child_node.parent = self
    
    def set_follow_up_context(self, selected_text: str = None, follow_up_intent: str = None, context_type: str = "follow_up"):
        """Set follow-up context information for this node."""
        self.follow_up_context = {
            'selected_text': selected_text,
            'follow_up_intent': follow_up_intent,
            'context_type': context_type
        }
    
    def get_enhanced_context_prompt(self) -> str:
        """Generate enhanced context prompt for follow-up conversations."""
        if not self.follow_up_context or self.follow_up_context.get('context_type') != 'follow_up':
            return ""
        
        context_parts = []
        
        # Add information about what text was selected
        if self.follow_up_context.get('selected_text'):
            context_parts.append(f"User wants to ask a follow-up questions, selected this text from the previous conversation: \"{self.follow_up_context['selected_text']}\"")
        
        # # Add information about user's intent
        # if self.follow_up_context.get('follow_up_intent'):
        #     context_parts.append(f"User wants to: {self.follow_up_context['follow_up_intent']}") #user query or what user wants to know check if this also being added while in query with user content addition
        # else:
        #     context_parts.append("User wants to know more details about the selected topic") #does this prints by deafult all the time?
            
        
        # Add instruction for AI
        context_parts.append("Please focus your response on this specific topic and provide detailed, relevant information. The context is given below ")
        
        return " ".join(context_parts)

    def auto_generate_title_if_needed(self, llm_client, user_message: str) -> bool:
        """🎯 SIMPLE: Generate title if node still has default 'New Chat' title."""
        if self.title == "New Chat":
            self.title = llm_client.generate_title_from_question(user_message)
            print(f"✅ Auto-generated title: '{self.title}'")
            return True
        return False








#-------------------------------------TESTS-----------------------------




# Test functions
def test_local_buffer():
    """Test LocalBuffer functionality."""
    print("🧪 Testing LocalBuffer...")
    
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
    
    # Test clear functionality
    print(f"✅ Before clear: {buffer.size()} messages")
    buffer.clear(1)  # Clear last message
    print(f"✅ After clearing 1: {buffer.size()} messages")
    buffer.clear()  # Clear all
    print(f"✅ After clearing all: {buffer.size()} messages")
    
    # Test overflow
    for i in range(10):
        buffer.add_message("user", f"Message {i}")
    final_count = buffer.size()
    print(f"✅ After adding 10 more, buffer size: {final_count} (should be 5)")
    
    print("🎉 LocalBuffer test passed!")
    return True


def test_tree_node():
    """Test TreeNode functionality."""
    print("\n🧪 Testing TreeNode...")
    
    # Create nodes
    root = TreeNode(title="Main Chat")
    child = TreeNode(title="Subchat", parent=root)
    root.add_child(child)
    
    print(f"✅ Root: {root.title}")
    print(f"✅ Child: {child.title}")
    print(f"✅ Child path: {' > '.join(child.get_path())}")
    print(f"✅ Root has {len(root.children)} children")
    
    # Test buffers in nodes
    root.buffer.add_message("user", "Hello from root")
    child.buffer.add_message("user", "Hello from child")
    
    print(f"✅ Root buffer: {root.buffer.size()} messages")
    print(f"✅ Child buffer: {child.buffer.size()} messages")
    
    print("🎉 TreeNode test passed!")
    return True


def test_tree():
    """Run all tree component tests."""
    print("🧪 Testing Tree Components...")
    
    try:
        test_local_buffer()
        test_tree_node()
        print("\n🎉 All tree tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    test_tree()