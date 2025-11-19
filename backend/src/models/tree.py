from typing import Optional, List, Dict, Any
import uuid
import time
from collections import deque
from src.utils.debug_logger import get_debug_logger

class LocalBuffer:
    """Fixed-size message buffer per conversation node with auto-archiving and rolling summarization."""

    def __init__(self, max_turns: int = 50, vector_index=None, node_id: str = None, llm_client=None):
        self.turns: deque[Dict[str, Any]] = deque(maxlen=max_turns)
        self.vector_index = vector_index  # Reference to global vector index
        self.node_id = node_id  # Node ID for archiving
        self.max_turns = max_turns
        self.llm_client = llm_client  # For generating summaries
        
        # Summarization tracking
        self.summary: str = ""  # Rolling summary of old messages
        self.summary_max_tokens: int = 500  # Max summary length
        self.messages_processed_count: int = 0  # Total messages ever added to this buffer
        self.summarization_interval: int = 5  # Summarize every 5 messages
        self.summarization_start_threshold: int = 15  # Start summarizing after 15 messages

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
        
        # Track total messages for summarization
        self.messages_processed_count += 1
        
        # 3.5 Check if we need to create/update rolling summary
        if self._should_summarize():
            self._create_rolling_summary()
        
        # 4. Log buffer state to BOTH loggers (now includes summary)
        logger_overwrite = get_debug_logger(append_mode=False)  # For user viewing
        logger_append = get_debug_logger(append_mode=True)      # For full debugging
        
        for logger in [logger_overwrite, logger_append]:
            logger.log_buffer(
                node_id=self.node_id,
                buffer_messages=list(self.turns),
                max_turns=self.max_turns,
                summary=self.summary  # Pass summary to logger
            )
        
        # 5. Show brief buffer state in terminal (last 3 messages)
        print(f"📋 Buffer ({self.size()}/{self.max_turns}): Last 3 messages (full log in file)")
        recent_3 = list(self.turns)[-3:]
        for i, msg in enumerate(recent_3, 1):
            msg_preview = msg['text'][:50] + ('...' if len(msg['text']) > 50 else '')
            print(f"   {i}. [{msg['role']}] {msg_preview}")
    
    def _should_summarize(self) -> bool:
        """
        Check if we should create/update summary.
        
        Summarization triggers:
        - At message 15 (first time) - summarize messages 1-5 (oldest 5)
        - At message 20 - summarize messages 6-10 (oldest 5 after 1-5 evicted)
        - At message 25 - summarize messages 11-15 (oldest 5 after 6-10 evicted)
        - Continue every 5 messages...
        """
        if self.messages_processed_count < self.summarization_start_threshold:
            return False  # Not enough messages yet (need 15 first)
        
        # After reaching 15, check if we're at a 5-message interval
        messages_since_first_summary = self.messages_processed_count - self.summarization_start_threshold
        return messages_since_first_summary % self.summarization_interval == 0
    
    def _create_rolling_summary(self):
        """
        Create/update rolling summary of conversation.
        
        Summarizes the 5 OLDEST messages currently in buffer (FIFO order).
        Each summary is appended to previous summary for rolling context.
        
        Timeline example:
        - Msg 15: Summarize m1-m5 (oldest in buffer [m1...m15])
        - Msg 20: Summarize m6-m10 (oldest in buffer [m6...m20]) + previous summary
        - Msg 25: Summarize m11-m15 (oldest in buffer [m11...m25]) + previous summary
        """
        print(f"🔍 DEBUG: llm_client type = {type(self.llm_client)}, value = {self.llm_client}")
        if self.llm_client:
            print(f"🔍 DEBUG: Has groq_client? {hasattr(self.llm_client, 'groq_client')}")
            if hasattr(self.llm_client, 'groq_client'):
                print(f"🔍 DEBUG: groq_client value = {self.llm_client.groq_client}")
        
        if not self.llm_client:
            print("⚠️  No LLM client available - skipping summarization")
            return
        
        if len(self.turns) < 5:
            print("⚠️  Not enough messages in buffer to summarize")
            return
        
        # Get the 5 OLDEST messages from buffer (FIFO = first 5)
        oldest_5_messages = list(self.turns)[:5]
        
        # Calculate which message numbers we're summarizing
        start_msg_num = self.messages_processed_count - len(self.turns) + 1
        end_msg_num = start_msg_num + 4
        
        # Format messages for LLM
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['text']}" 
            for msg in oldest_5_messages
        ])
        
        # Build prompt
        if self.summary:
            # Re-summarize with previous summary (rolling update)
            prompt = f"""You are maintaining a rolling summary of a conversation.

PREVIOUS SUMMARY:
{self.summary}

NEW MESSAGES TO ADD (messages {start_msg_num}-{end_msg_num}):
{conversation_text}

Create an updated summary that:
1. Includes key information from the previous summary
2. Adds important details from the new messages (main topics, user info, preferences, facts)
3. Removes redundant or less important information
4. Stays concise (under {self.summary_max_tokens} tokens)

Updated summary:"""
        else:
            # First summary (messages 1-5)
            prompt = f"""Summarize the following conversation messages concisely.
Focus on: main topics discussed, user information/preferences, key facts, important decisions.
Keep under {self.summary_max_tokens} tokens.

MESSAGES (messages {start_msg_num}-{end_msg_num}):
{conversation_text}

Summary:"""
        
        try:
            # Call LLM to generate summary
            response = self.llm_client.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.summary_max_tokens,
                temperature=0.3  # Lower temperature for consistent summarization
            )
            
            new_summary = response.choices[0].message.content.strip()
            old_summary_len = len(self.summary) if self.summary else 0
            
            self.summary = new_summary
            
            print(f"📝 Summary updated: {old_summary_len} → {len(new_summary)} chars (summarized messages {start_msg_num}-{end_msg_num})")
            print(f"   Summary preview: {new_summary[:100]}{'...' if len(new_summary) > 100 else ''}")
            
        except Exception as e:
            print(f"⚠️  Summarization failed: {e}")
            import traceback
            traceback.print_exc()
    
    def inherit_summary(self, parent_summary: str):
        """
        Called when creating a child node - inherit parent's accumulated knowledge.
        Child starts with parent's summary and builds on top of it.
        """
        if parent_summary:
            self.summary = parent_summary
            summary_len = len(parent_summary)
            print(f"📝 Inherited summary from parent ({summary_len} chars)")
            print(f"   Preview: {parent_summary[:100]}{'...' if len(parent_summary) > 100 else ''}")
    
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

    def __init__(self, node_id: Optional[str] = None, title: str = 'Untitled', parent: Optional['TreeNode'] = None, vector_index=None, llm_client=None):
        self.node_id: str = node_id if node_id else str(uuid.uuid4())
        self.title: str = title
        self.parent: Optional['TreeNode'] = parent
        self.children: List['TreeNode'] = []
        self.buffer: LocalBuffer = LocalBuffer(max_turns=15, vector_index=vector_index, node_id=self.node_id, llm_client=llm_client)
        self.metadata: Dict[str, Any] = {}
        self.llm_client = llm_client  # Store for child node creation
        
        # Inherit summary from parent if this is a child node
        if parent and parent.buffer.summary:
            self.buffer.inherit_summary(parent.buffer.summary)
        
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