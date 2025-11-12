from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class MessageRequest(BaseModel):
    message: str
    # Optional fields to provide context for follow-up questions
    is_follow_up: Optional[bool] = False       # Is this message part of a follow-up conversation?
    original_context: Optional[str] = None     # Context about what this follow-up relates to
    disable_rag: Optional[bool] = False        # Skip RAG retrieval (for population/indexing only)

class MessageResponse(BaseModel):
    response: str
    message_id: str
    timestamp: float
    conversation_title: Optional[str] = None  # Include updated title if changed
    usage: Optional[Dict[str, int]] = None    # Token usage: {prompt_tokens, completion_tokens, total_tokens}

class CreateConversationRequest(BaseModel):
    title: str = "New Chat"

class CreateSubchatRequest(BaseModel):
    title: str
    # Follow-up context fields to enhance AI understanding
    selected_text: Optional[str] = None        # Text user selected from parent chat
    follow_up_context: Optional[str] = None    # Description of what user wants to explore
    context_type: Optional[str] = "follow_up"  # Type of subchat (follow_up, new_topic, etc.)

class ConversationNode(BaseModel):
    node_id: str
    title: str
    parent_id: Optional[str] = None
    children: List[str] = []
    path: List[str] = []
    message_count: int = 0

class ConversationTree(BaseModel):
    root: ConversationNode
    all_nodes: Dict[str, ConversationNode]

class ConversationHistory(BaseModel):
    node_id: str
    title: str
    messages: List[Dict[str, Any]]
    path: List[str]