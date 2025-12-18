from typing import Optional, List, Dict, Any
import uuid
import time
from collections import deque
from src.utils.debug_logger import get_debug_logger

class LocalBuffer:
    """Fixed-size message buffer per conversation node with auto-archiving and rolling summarization."""

    def __init__(self, max_turns: int = 50, vector_index=None, node_id: str = None, llm_client=None, node_title: str = None):
        self.turns: deque[Dict[str, Any]] = deque(maxlen=max_turns)
        self.vector_index = vector_index  # Reference to global vector index
        self.node_id = node_id  # Node ID for archiving
        self.node_title = node_title  # Node title for display in logs
        self.max_turns = max_turns
        self.llm_client = llm_client  # For generating summaries
        
        # Summarization tracking
        self.summary: str = ""  # Rolling summary of old messages
        self.summary_max_tokens: int = 500  # Max summary length
        self.messages_processed_count: int = 0  # Total messages ever added to this buffer
        
        # 🔧 DYNAMIC SUMMARIZATION: Triggered when buffer fills (at n, 2n, 3n...)
        # No hardcoded thresholds - adapts to any buffer size
        print(f"📊 Buffer size: {max_turns} messages | Summarization will trigger every {max_turns} messages")

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
                        'indexed_immediately': True,  # Flag for debugging
                        'conversation_title': self.node_title or 'Untitled'  # Add title for logging
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
                summary=self.summary,  # Pass summary to logger
                conversation_title=self.node_title  # Pass conversation title
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
        
        🎯 NEW STRATEGY: Summarize when buffer is completely full
        
        Triggers at: n, 2n, 3n, 4n... where n = buffer size (max_turns)
        
        Examples:
        - Buffer=10: Summarize at messages 10, 20, 30, 40...
        - Buffer=20: Summarize at messages 20, 40, 60, 80...
        - Buffer=40: Summarize at messages 40, 80, 120, 160...
        
        This ensures:
        - No race conditions with buffer eviction
        - Scales perfectly with any buffer size
        - Summarizes ALL messages in buffer (maximum information retention)
        """
        if self.messages_processed_count == 0:
            return False
        
        # Trigger every time we've processed a full buffer's worth of messages
        return self.messages_processed_count % self.max_turns == 0
    
    def _create_rolling_summary(self):
        """
        Create/update rolling summary of conversation.
        
        🎯 NEW STRATEGY: Summarize ALL current buffer messages
        
        Timeline example (buffer=10):
        - Msg 10: Buffer full [1-10] → Summarize all 10 messages → Summary_1
        - Msg 20: Buffer full [11-20] → Summarize all 10 messages → Summary_2 = Summary_1 + new_summary(11-20)
        - Msg 30: Buffer full [21-30] → Summarize all 10 messages → Summary_3 = Summary_2 + new_summary(21-30)
        
        Benefits:
        - Perfect alignment with buffer size
        - No information loss (summarizes ALL buffer messages)
        - Works for any buffer size (5, 10, 20, 40, 80, 160...)
        """
        if not self.llm_client:
            print("⚠️  No LLM client available - skipping summarization")
            return
        
        if len(self.turns) == 0:
            print("⚠️  Empty buffer - skipping summarization")
            return
        
        # 🔥 KEY CHANGE: Get ALL messages currently in buffer (not just oldest 5)
        all_buffer_messages = list(self.turns)
        
        # Calculate which message numbers we're summarizing
        start_msg_num = self.messages_processed_count - len(all_buffer_messages) + 1
        end_msg_num = self.messages_processed_count
        
        # Format ALL buffer messages for LLM
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['text']}" 
            for msg in all_buffer_messages
        ])
        
        # Build prompt (updated to reflect ALL buffer messages)
        if self.summary:
            # Rolling update: combine old summary + new buffer messages
            prompt = f"""You are maintaining a rolling summary of a conversation.

PREVIOUS SUMMARY (messages 1-{start_msg_num-1}):
{self.summary}

NEW MESSAGES TO SUMMARIZE (messages {start_msg_num}-{end_msg_num}, total: {len(all_buffer_messages)} messages):
{conversation_text}

Create an updated summary that:
1. Preserves key information from the previous summary
2. Adds important details from the new messages (topics, facts, decisions, preferences)
3. Removes redundant information
4. Stays concise (under {self.summary_max_tokens} tokens)

Updated summary:"""
        else:
            # First summary - summarizing first full buffer
            prompt = f"""Summarize the following conversation messages concisely.
Focus on: main topics, user information, key facts, important decisions.
Keep under {self.summary_max_tokens} tokens.

MESSAGES (messages {start_msg_num}-{end_msg_num}, total: {len(all_buffer_messages)} messages):
{conversation_text}

Summary:"""
        
        try:
            # 🎯 Use vLLM ONLY - no fallback to save Groq quota
            if hasattr(self.llm_client, 'vllm_client') and self.llm_client.vllm_client:
                # Use vLLM (Kaggle GPU)
                new_summary = self.llm_client.vllm_client.generate(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,  # Lower temperature for consistent summarization
                    max_tokens=500
                )
                new_summary = new_summary.strip()
            else:
                # Hard fail - no fallback to preserve Groq quota
                raise RuntimeError(
                    "❌ vLLM not available for summarization!\n"
                    "   Summarization requires vLLM to avoid Groq API quota limits.\n"
                    "   Please ensure VLLMClient.set_model(llm) was called in your notebook."
                )
            
            old_summary_len = len(self.summary) if self.summary else 0
            self.summary = new_summary
            
            print(f"📝 Summary updated: {old_summary_len} → {len(new_summary)} chars")
            print(f"   Summarized messages {start_msg_num}-{end_msg_num} ({len(all_buffer_messages)} messages in buffer)")
            print(f"   Summary preview: {new_summary[:100]}{'...' if len(new_summary) > 100 else ''}")
            
        except Exception as e:
            print(f"❌ CRITICAL: Summarization failed: {e}")
            print("   Server cannot continue without working summarization.")
            import traceback
            traceback.print_exc()
            # Re-raise to stop execution
            raise
    
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
    
    def get_context_messages(self, include_summary: bool = True) -> List[Dict[str, Any]]:
        """
        Get context messages for LLM (buffer + optional summary).
        
        This builds the conversation context that gets sent to the LLM,
        optionally including the rolling summary of archived messages.
        
        Args:
            include_summary: Whether to include rolling summary as first message
            
        Returns:
            List of message dicts with 'role' and 'content' keys, in chronological order.
            If summary exists and include_summary=True, it appears first as a system message.
        """
        messages = []
        
        # 1. Add rolling summary as system message (if available and requested)
        if include_summary and self.summary:
            messages.append({
                "role": "system",
                "content": f"📋 CONVERSATION SUMMARY (older archived context):\n{self.summary}\n\n---\nRecent messages in buffer follow below:"
            })
        
        # 2. Add all current buffer messages in chronological order
        for msg in self.turns:
            messages.append({
                "role": msg["role"],
                "content": msg["text"]
            })
        
        return messages
    
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

    def __init__(self, node_id: Optional[str] = None, title: str = 'Untitled', parent: Optional['TreeNode'] = None, vector_index=None, llm_client=None, buffer_size: int = 15):
        self.node_id: str = node_id if node_id else str(uuid.uuid4())
        self.title: str = title
        self.parent: Optional['TreeNode'] = parent
        self.children: List['TreeNode'] = []
        
        # 🔧 DYNAMIC BUFFER SIZE: Accept as parameter (default 15 for backward compatibility)
        self.buffer: LocalBuffer = LocalBuffer(
            max_turns=buffer_size,  # ← Use parameter instead of hardcoded 15
            vector_index=vector_index, 
            node_id=self.node_id, 
            llm_client=llm_client, 
            node_title=title
        )
        
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

    def auto_generate_title_if_needed(self, llm_client, user_message: str):
        """🎯 SIMPLE: Generate title if node still has default 'New Chat' title."""
        if self.title == "New Chat":
            self.title = llm_client.generate_title_from_question(user_message)
            self.buffer.node_title = self.title  # Update buffer's title reference
            
            # Update vector store metadata for all previously-indexed messages
            if self.buffer.vector_index:
                self.buffer.vector_index.update_conversation_title(
                    self.node_id, 
                    self.title
                )
            
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