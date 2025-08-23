"""
Pydantic Schemas for Hierarchical Chat Research Backend

This module defines the API request/response schemas that preserve
the research innovations from the original notebook implementation.

Schema Mapping:
- Notebook message structures -> MessageSchema, ConversationSchema
- LocalBuffer parameters -> BufferConfigSchema
- API request/response patterns -> Request/Response schemas
- Research analytics -> AnalyticsSchema

All schemas maintain type safety and validation for the research
innovations while providing clear API contracts for frontend integration.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class MessageTypeEnum(str, Enum):
    """Message types for conversation nodes"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SourceTypeEnum(str, Enum):
    """Document source types for vector store"""
    CONVERSATION = "conversation"
    UPLOAD = "upload"
    SYSTEM = "system"


class MetricCategoryEnum(str, Enum):
    """Research metrics categories"""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    USAGE = "usage"
    FILTERING = "filtering"
    INDEXING = "indexing"
    RETRIEVAL = "retrieval"


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
        "validate_by_name": True
    }


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================================
# MESSAGE AND CONVERSATION SCHEMAS (Core Research Innovation #1)
# ============================================================================

class MessageSchema(BaseSchema):
    """
    Message Schema - Preserves Notebook Message Structure
    
    Maps to the message format used throughout the notebook's
    LocalBuffer, TreeNode, and ChatGraphManager implementations.
    
    Preserves:
    - Role-based message typing
    - Timestamp tracking for temporal filtering
    - Content structure for LLM processing
    - Metadata for research analytics
    """
    role: MessageTypeEnum = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Message metadata for research")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class ConversationNodeSchema(BaseSchema, TimestampMixin):
    """
    Conversation Node Schema - TreeNode Preservation
    
    Maps directly to the TreeNode class from the notebook.
    Preserves the hierarchical structure and metadata tracking
    essential for the research innovations.
    """
    id: Optional[str] = None
    parent_id: Optional[str] = Field(None, description="Parent node ID for tree structure")
    message_content: str = Field(..., description="Node message content")
    message_type: MessageTypeEnum = Field(..., description="Message type")
    node_depth: int = Field(default=0, ge=0, description="Node depth in conversation tree")
    response_time_ms: Optional[int] = Field(None, ge=0, description="Response generation time")
    token_count: Optional[int] = Field(None, ge=0, description="Token count for analysis")
    context_used: Optional[Dict[str, Any]] = Field(None, description="Context sources used")
    retrieved_documents: Optional[List[Dict]] = Field(None, description="Retrieved vector documents")
    context_tokens: Optional[int] = Field(None, ge=0, description="Context tokens used")
    is_leaf: bool = Field(default=True, description="Whether node is a leaf")


class ConversationTreeSchema(BaseSchema, TimestampMixin):
    """
    Conversation Tree Schema - Forest Preservation
    
    Maps to the Forest class from the notebook.
    Preserves multi-tree conversation management and
    tree-level analytics for research analysis.
    """
    id: Optional[str] = None
    tree_name: str = Field(..., min_length=1, description="Human-readable tree name")
    tree_index: int = Field(default=0, ge=0, description="Tree order within session")
    is_active: bool = Field(default=True, description="Tree active status")
    root_node_id: Optional[str] = Field(None, description="Root node reference")
    total_nodes: int = Field(default=0, ge=0, description="Total nodes in tree")
    max_depth: int = Field(default=0, ge=0, description="Maximum tree depth")
    last_interaction: datetime = Field(default_factory=datetime.utcnow, description="Last interaction time")
    max_nodes: int = Field(default=100, ge=1, description="Maximum nodes allowed")
    nodes: Optional[List[ConversationNodeSchema]] = Field(None, description="Tree nodes")


# ============================================================================
# BUFFER CONFIGURATION SCHEMAS (Core Research Innovation #1)
# ============================================================================

class BufferConfigSchema(BaseSchema):
    """
    Buffer Configuration Schema - LocalBuffer Parameters
    
    Preserves the exact LocalBuffer configuration parameters
    from the notebook implementation for research reproducibility.
    """
    max_turns: int = Field(default=50, ge=1, le=1000, description="Maximum buffer size (LocalBuffer)")
    exclude_recent: int = Field(default=10, ge=0, description="Recent messages to exclude (LocalBuffer)")
    
    @validator('exclude_recent')
    def validate_exclude_recent(cls, v, values):
        if 'max_turns' in values and v >= values['max_turns']:
            raise ValueError('exclude_recent must be less than max_turns')
        return v


class MessageBufferSchema(BaseSchema, TimestampMixin):
    """
    Message Buffer Schema - LocalBuffer State
    
    Represents the complete state of a LocalBuffer instance
    including configuration and current messages.
    """
    id: Optional[str] = None
    session_id: str = Field(..., description="Session identifier")
    max_turns: int = Field(..., ge=1, description="Maximum buffer size")
    exclude_recent: int = Field(..., ge=0, description="Recent exclusion count")
    messages: List[MessageSchema] = Field(default=[], description="Current buffer messages")
    current_size: int = Field(default=0, ge=0, description="Current buffer size")
    buffer_version: int = Field(default=1, ge=1, description="Buffer version")
    total_messages_processed: int = Field(default=0, ge=0, description="Total messages processed")


# ============================================================================
# SESSION SCHEMAS (Multi-User Research Environment)
# ============================================================================

class SessionConfigSchema(BaseSchema):
    """Session configuration schema for research parameters"""
    max_turns: int = Field(default=50, ge=1, le=1000, description="LocalBuffer max turns")
    exclude_recent: int = Field(default=10, ge=0, description="LocalBuffer exclude recent")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    
    @validator('exclude_recent')
    def validate_exclude_recent(cls, v, values):
        if 'max_turns' in values and v >= values['max_turns']:
            raise ValueError('exclude_recent must be less than max_turns')
        return v


class UserSessionSchema(BaseSchema, TimestampMixin):
    """
    User Session Schema - Multi-User Research Support
    
    Maps to session management logic from ChatGraphManager.
    Enables multi-user research environment with session isolation.
    """
    id: Optional[str] = None
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    max_turns: int = Field(default=50, description="LocalBuffer max turns")
    exclude_recent: int = Field(default=10, description="LocalBuffer exclude recent")
    is_active: bool = Field(default=True, description="Session active status")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity time")
    total_conversations: int = Field(default=0, ge=0, description="Total conversations")
    total_messages: int = Field(default=0, ge=0, description="Total messages")
    total_tokens_used: int = Field(default=0, ge=0, description="Total tokens used")


# ============================================================================
# VECTOR STORE SCHEMAS (Core Research Innovation #4)
# ============================================================================

class VectorDocumentSchema(BaseSchema, TimestampMixin):
    """
    Vector Document Schema - GlobalVectorIndex Preservation
    
    Maps to the GlobalVectorIndex class from the notebook.
    Preserves vector storage and temporal filtering capabilities.
    """
    id: Optional[str] = None
    document_id: str = Field(..., description="Unique document identifier")
    collection_name: str = Field(..., description="ChromaDB collection name")
    content: str = Field(..., min_length=1, description="Document content")
    content_hash: str = Field(..., description="Content hash for deduplication")
    embedding_model: str = Field(..., description="Embedding model name")
    embedding_dimension: int = Field(..., ge=1, description="Embedding vector dimension")
    timestamp: datetime = Field(..., description="Document timestamp")
    source_type: SourceTypeEnum = Field(..., description="Document source type")
    source_reference: Optional[str] = Field(None, description="Source reference")
    conversation_context: Optional[Dict[str, Any]] = Field(None, description="Conversation context")
    retrieval_count: int = Field(default=0, ge=0, description="Retrieval count")
    last_retrieved: Optional[datetime] = Field(None, description="Last retrieval time")
    relevance_scores: Optional[List[Dict]] = Field(None, description="Historical relevance scores")
    is_active: bool = Field(default=True, description="Document active status")
    is_indexed: bool = Field(default=False, description="ChromaDB indexing status")


class VectorSearchRequest(BaseSchema):
    """
    Vector Search Request Schema
    
    Parameters for vector similarity search with temporal filtering.
    Preserves GlobalVectorIndex search capabilities.
    """
    query: str = Field(..., min_length=1, description="Search query text")
    limit: Optional[int] = Field(None, ge=1, le=50, description="Maximum results")
    time_filter_hours: Optional[int] = Field(None, ge=1, description="Temporal filter in hours")
    session_id: str = Field(..., description="Session identifier for isolation")


class VectorSearchResult(BaseSchema):
    """Vector search result schema"""
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    document_id: str = Field(..., description="Document identifier")


# ============================================================================
# LLM SCHEMAS (Core Research Innovation #5)
# ============================================================================

class LLMRequest(BaseSchema):
    """
    LLM Request Schema - LLMClient Parameters
    
    Preserves the exact LLMClient request structure from the notebook
    including OpenAI 4o-mini configuration and context integration.
    """
    messages: List[MessageSchema] = Field(..., min_items=1, description="Conversation messages")
    context_documents: Optional[List[VectorSearchResult]] = Field(None, description="Context documents")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="LLM temperature override")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens override")
    session_id: str = Field(..., description="Session identifier")


class LLMResponse(BaseSchema):
    """
    LLM Response Schema - LLMClient Response
    
    Preserves the response format from the notebook LLMClient
    including metadata for research analysis.
    """
    content: str = Field(..., description="Generated response content")
    response_time_ms: int = Field(..., ge=0, description="Response generation time")
    tokens_used: int = Field(..., ge=0, description="Total tokens used")
    model: str = Field(..., description="Model used for generation")
    context_documents_used: int = Field(default=0, ge=0, description="Context documents count")
    timestamp: datetime = Field(..., description="Response timestamp")


# ============================================================================
# CONVERSATION API SCHEMAS (Complete Workflow)
# ============================================================================

class ConversationRequest(BaseSchema):
    """
    Conversation Request Schema - Complete Workflow
    
    Maps to the complete ChatGraphManager.process_message workflow
    including all research innovations integration.
    """
    message: str = Field(..., min_length=1, description="User message")
    session_id: str = Field(..., description="Session identifier")
    tree_name: str = Field(default="default", description="Conversation tree name")
    include_context: bool = Field(default=True, description="Include vector context")
    max_context_documents: Optional[int] = Field(None, ge=0, le=20, description="Max context docs")


class ConversationResponse(BaseSchema):
    """
    Conversation Response Schema - Complete Response
    
    Represents the complete response from the ChatGraphManager workflow
    including all research innovations and metadata.
    """
    response: str = Field(..., description="Assistant response")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")
    context_sources: List[Dict[str, Any]] = Field(default=[], description="Context sources used")
    session_id: str = Field(..., description="Session identifier")
    tree_name: str = Field(..., description="Conversation tree name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


# ============================================================================
# RESEARCH ANALYTICS SCHEMAS
# ============================================================================

class ResearchMetricSchema(BaseSchema, TimestampMixin):
    """Research analytics metric schema"""
    id: Optional[str] = None
    session_id: str = Field(..., description="Session identifier")
    metric_name: str = Field(..., description="Metric name")
    metric_category: MetricCategoryEnum = Field(..., description="Metric category")
    metric_value: float = Field(..., description="Metric value")
    metric_unit: Optional[str] = Field(None, description="Metric unit")
    metric_metadata: Optional[Dict[str, Any]] = Field(None, description="Metric metadata")
    conversation_tree_id: Optional[str] = Field(None, description="Associated tree")
    conversation_node_id: Optional[str] = Field(None, description="Associated node")
    measurement_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Measurement time")


class AnalyticsRequest(BaseSchema):
    """Analytics request schema"""
    session_id: str = Field(..., description="Session identifier")
    metric_categories: Optional[List[MetricCategoryEnum]] = Field(None, description="Metric categories")
    start_time: Optional[datetime] = Field(None, description="Start time filter")
    end_time: Optional[datetime] = Field(None, description="End time filter")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Result limit")


class AnalyticsSummary(BaseSchema):
    """Analytics summary schema"""
    session_id: str = Field(..., description="Session identifier")
    total_conversations: int = Field(..., ge=0, description="Total conversations")
    total_messages: int = Field(..., ge=0, description="Total messages")
    total_tokens_used: int = Field(..., ge=0, description="Total tokens")
    average_response_time_ms: float = Field(..., ge=0, description="Average response time")
    context_usage_rate: float = Field(..., ge=0.0, le=1.0, description="Context usage rate")
    buffer_efficiency: float = Field(..., ge=0.0, le=1.0, description="Buffer efficiency")
    vector_retrieval_accuracy: float = Field(..., ge=0.0, le=1.0, description="Retrieval accuracy")


# ============================================================================
# DATA EXPORT SCHEMAS (Research Collaboration)
# ============================================================================

class ExportRequest(BaseSchema):
    """Data export request schema"""
    session_id: str = Field(..., description="Session identifier")
    export_name: str = Field(..., min_length=1, description="Export name")
    export_format: str = Field(default="json", pattern="^(json|csv|parquet)$", description="Export format")
    include_trees: Optional[List[str]] = Field(None, description="Tree IDs to include")
    include_metadata: bool = Field(default=True, description="Include metadata")
    include_analytics: bool = Field(default=False, description="Include analytics")
    anonymize_content: bool = Field(default=False, description="Anonymize content")
    remove_timestamps: bool = Field(default=False, description="Remove timestamps")


class ExportStatus(BaseSchema):
    """Export status schema"""
    export_id: str = Field(..., description="Export identifier")
    export_name: str = Field(..., description="Export name")
    export_status: str = Field(..., description="Export status")
    export_format: str = Field(..., description="Export format")
    file_size_bytes: Optional[int] = Field(None, description="File size")
    exported_at: Optional[datetime] = Field(None, description="Export completion time")
    export_duration_ms: Optional[int] = Field(None, description="Export duration")
    download_url: Optional[str] = Field(None, description="Download URL")


# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class ErrorDetail(BaseSchema):
    """Error detail schema"""
    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field causing error")


class ErrorResponse(BaseSchema):
    """Error response schema"""
    error: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[List[ErrorDetail]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


# ============================================================================
# HEALTH AND STATUS SCHEMAS
# ============================================================================

class HealthCheck(BaseSchema):
    """Health check schema"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    services: Dict[str, str] = Field(..., description="Service statuses")


class SystemStatus(BaseSchema):
    """System status schema"""
    database_connected: bool = Field(..., description="Database connection status")
    vector_store_connected: bool = Field(..., description="Vector store connection status")
    llm_service_available: bool = Field(..., description="LLM service availability")
    active_sessions: int = Field(..., ge=0, description="Active sessions count")
    total_conversations: int = Field(..., ge=0, description="Total conversations")
    total_documents_indexed: int = Field(..., ge=0, description="Total indexed documents")


# ============================================================================
# SCHEMA MAPPING SUMMARY
# ============================================================================

def get_schema_mapping_summary() -> Dict[str, Any]:
    """
    Get comprehensive mapping between notebook structures and API schemas.
    
    Returns:
        dict: Complete mapping between notebook and schema implementations
    """
    return {
        "notebook_to_schema_mapping": {
            "LocalBuffer_messages": {
                "schemas": ["MessageSchema", "MessageBufferSchema"],
                "description": "Message format and buffer state preservation",
                "research_preservation": "Exact role/content/timestamp structure"
            },
            "TreeNode_structure": {
                "schemas": ["ConversationNodeSchema", "ConversationTreeSchema"],
                "description": "Hierarchical conversation structure",
                "research_preservation": "Parent-child relationships and metadata"
            },
            "GlobalVectorIndex_documents": {
                "schemas": ["VectorDocumentSchema", "VectorSearchRequest", "VectorSearchResult"],
                "description": "Vector storage and search capabilities",
                "research_preservation": "Temporal filtering and relevance tracking"
            },
            "LLMClient_interface": {
                "schemas": ["LLMRequest", "LLMResponse"],
                "description": "OpenAI 4o-mini integration interface",
                "research_preservation": "Exact parameter and response structure"
            },
            "ChatGraphManager_workflow": {
                "schemas": ["ConversationRequest", "ConversationResponse"],
                "description": "Complete conversation processing workflow",
                "research_preservation": "Full research innovation integration"
            }
        },
        "api_contract_features": {
            "type_safety": "Pydantic validation for all research parameters",
            "documentation": "Auto-generated OpenAPI docs with research context",
            "validation": "Input validation preserving notebook constraints",
            "serialization": "JSON serialization for frontend integration"
        },
        "research_extensions": {
            "analytics_schemas": "Research metrics and performance tracking",
            "export_schemas": "Academic collaboration and data sharing",
            "session_schemas": "Multi-user research environment support"
        }
    }
