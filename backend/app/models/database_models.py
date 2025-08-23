"""
Database Models for Hierarchical Chat Research Backend

This module implements the core database models that preserve and extend
the research innovations from the original notebook implementation.

Notebook Mapping:
- TreeNode class -> ConversationNode model
- Forest class -> ConversationTree model  
- LocalBuffer -> MessageBuffer model
- GlobalVectorIndex -> VectorDocument model
- Session management -> UserSession model

All models are designed for research data persistence, analytics,
and scalable multi-user deployment while maintaining the core
hierarchical chat innovations.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields for all research entities.
    
    Provides audit trail and research data tracking capabilities
    essential for academic publication and analysis.
    """
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Research metadata
    research_metadata = Column(JSON, default=dict, nullable=True, 
                             comment="Research-specific metadata for academic analysis")


class UserSession(BaseModel):
    """
    User Session Model for Multi-User Research Environment
    
    Preserves session isolation while enabling collaborative research.
    Maps to the session management logic from the notebook's ChatGraphManager.
    
    Research Features:
    - Session-based conversation isolation
    - Multi-user support for collaborative research
    - Analytics tracking per session
    """
    __tablename__ = "user_sessions"
    
    session_id = Column(String(255), unique=True, nullable=False, index=True,
                       comment="Unique session identifier")
    user_id = Column(String(255), nullable=True, index=True,
                    comment="Optional user identifier for multi-user research")
    
    # Session Configuration (Research Parameters)
    max_turns = Column(Integer, default=50, nullable=False,
                      comment="LocalBuffer max turns (from notebook research)")
    exclude_recent = Column(Integer, default=10, nullable=False,
                           comment="Recent messages to exclude (from notebook research)")
    
    # Session State
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Research Analytics
    total_conversations = Column(Integer, default=0, nullable=False)
    total_messages = Column(Integer, default=0, nullable=False)
    total_tokens_used = Column(Integer, default=0, nullable=False)
    
    # Relationships (Research Data Hierarchy)
    conversation_trees = relationship("ConversationTree", back_populates="session", cascade="all, delete-orphan")
    message_buffers = relationship("MessageBuffer", back_populates="session", cascade="all, delete-orphan")
    vector_documents = relationship("VectorDocument", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserSession(session_id='{self.session_id}', active={self.is_active})>"


class ConversationTree(BaseModel):
    """
    Conversation Tree Model - Core Research Innovation #3
    
    Maps directly to the Forest class from the notebook.
    Implements the hierarchical conversation structure that enables
    the research innovation of multi-tree conversation management.
    
    Research Features:
    - Multiple conversation trees per session
    - Tree-based conversation branching
    - Hierarchical message organization
    """
    __tablename__ = "conversation_trees"
    
    # Session Reference
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id", ondelete="CASCADE"), 
                       nullable=False, index=True)
    
    # Tree Identification
    tree_name = Column(String(255), nullable=False,
                      comment="Human-readable tree name for research organization")
    tree_index = Column(Integer, nullable=False,
                       comment="Tree order within session (preserves notebook logic)")
    
    # Tree State
    is_active = Column(Boolean, default=True, nullable=False)
    root_node_id = Column(UUID(as_uuid=True), nullable=True,
                         comment="Reference to root conversation node")
    
    # Research Metrics
    total_nodes = Column(Integer, default=0, nullable=False)
    max_depth = Column(Integer, default=0, nullable=False)
    last_interaction = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Tree Configuration (Research Parameters)
    max_nodes = Column(Integer, default=100, nullable=False,
                      comment="Maximum nodes per tree (prevents memory overflow)")
    
    # Relationships
    session = relationship("UserSession", back_populates="conversation_trees")
    nodes = relationship("ConversationNode", back_populates="tree", cascade="all, delete-orphan")
    
    # Indexes for Research Queries
    __table_args__ = (
        Index('ix_conversation_trees_session_active', 'session_id', 'is_active'),
        Index('ix_conversation_trees_last_interaction', 'last_interaction'),
    )
    
    def __repr__(self):
        return f"<ConversationTree(name='{self.tree_name}', nodes={self.total_nodes})>"


class ConversationNode(BaseModel):
    """
    Conversation Node Model - Core Research Innovation #1
    
    Maps directly to the TreeNode class from the notebook.
    Implements the hierarchical node structure with parent-child
    relationships that enable tree-based conversation flow.
    
    Research Features:
    - Parent-child node relationships
    - Message content and metadata storage
    - Node-level analytics and timestamps
    - Preserves exact notebook TreeNode logic
    """
    __tablename__ = "conversation_nodes"
    
    # Tree Reference
    tree_id = Column(UUID(as_uuid=True), ForeignKey("conversation_trees.id", ondelete="CASCADE"),
                    nullable=False, index=True)
    
    # Node Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey("conversation_nodes.id", ondelete="CASCADE"),
                      nullable=True, index=True,
                      comment="Parent node for hierarchical structure")
    
    # Node Content (Core Research Data)
    message_content = Column(Text, nullable=False,
                           comment="Message content (user or assistant)")
    message_type = Column(String(50), nullable=False,
                         comment="Message type: user, assistant, system")
    
    # Node Metadata (Research Analytics)
    node_depth = Column(Integer, default=0, nullable=False,
                       comment="Depth in conversation tree")
    response_time_ms = Column(Integer, nullable=True,
                            comment="Response generation time for research analysis")
    token_count = Column(Integer, nullable=True,
                        comment="Token count for cost and performance analysis")
    
    # Context Assembly Data (Research Innovation #2)
    context_used = Column(JSON, nullable=True,
                         comment="Context sources used for this response")
    retrieved_documents = Column(JSON, nullable=True,
                               comment="Vector store documents retrieved")
    context_tokens = Column(Integer, nullable=True,
                           comment="Tokens used in context assembly")
    
    # Node State
    is_leaf = Column(Boolean, default=True, nullable=False,
                    comment="Whether this is a leaf node")
    is_archived = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    tree = relationship("ConversationTree", back_populates="nodes")
    parent = relationship("ConversationNode", remote_side=[BaseModel.id], backref="children")
    
    # Indexes for Research Queries
    __table_args__ = (
        Index('ix_conversation_nodes_tree_parent', 'tree_id', 'parent_id'),
        Index('ix_conversation_nodes_created_at', 'created_at'),
        Index('ix_conversation_nodes_type', 'message_type'),
    )
    
    def __repr__(self):
        return f"<ConversationNode(type='{self.message_type}', depth={self.node_depth})>"


class MessageBuffer(BaseModel):
    """
    Message Buffer Model - Core Research Innovation #1 (LocalBuffer)
    
    Maps directly to the LocalBuffer class from the notebook.
    Implements the fixed-size buffer with timestamp-based filtering
    that prevents context pollution in the hierarchical chat system.
    
    Research Features:
    - Fixed-size message buffer (preserves notebook max_turns)
    - Timestamp-based recent exclusion (preserves exclude_recent)
    - Session isolation for multi-user research
    """
    __tablename__ = "message_buffers"
    
    # Session Reference
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    
    # Buffer Configuration (Research Parameters)
    max_turns = Column(Integer, default=50, nullable=False,
                      comment="Maximum buffer size (from notebook LocalBuffer)")
    exclude_recent = Column(Integer, default=10, nullable=False,
                           comment="Recent messages to exclude (from notebook LocalBuffer)")
    
    # Buffer Content
    messages = Column(JSON, nullable=False, default=list,
                     comment="Serialized message buffer preserving notebook structure")
    current_size = Column(Integer, default=0, nullable=False,
                         comment="Current buffer size for research analytics")
    
    # Buffer State
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    buffer_version = Column(Integer, default=1, nullable=False,
                           comment="Buffer version for change tracking")
    
    # Research Analytics
    total_messages_processed = Column(Integer, default=0, nullable=False)
    messages_excluded_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    session = relationship("UserSession", back_populates="message_buffers")
    
    def __repr__(self):
        return f"<MessageBuffer(size={self.current_size}, max={self.max_turns})>"


class VectorDocument(BaseModel):
    """
    Vector Document Model - Core Research Innovation #4
    
    Maps to the GlobalVectorIndex class from the notebook.
    Stores document embeddings and metadata for vector-based
    memory retrieval with temporal filtering.
    
    Research Features:
    - Vector embeddings storage
    - Temporal filtering metadata
    - Session-based document isolation
    - ChromaDB integration preservation
    """
    __tablename__ = "vector_documents"
    
    # Session Reference
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    
    # Document Identity
    document_id = Column(String(255), nullable=False, unique=True,
                        comment="Unique document identifier for ChromaDB")
    collection_name = Column(String(255), nullable=False,
                           comment="ChromaDB collection name")
    
    # Document Content
    content = Column(Text, nullable=False,
                    comment="Original document content")
    content_hash = Column(String(64), nullable=False,
                         comment="Content hash for deduplication")
    
    # Vector Data (Research Innovation)
    embedding_model = Column(String(255), nullable=False,
                           comment="Embedding model used (sentence-transformers)")
    embedding_dimension = Column(Integer, nullable=False,
                               comment="Embedding vector dimension")
    
    # Temporal Metadata (Core Research Feature)
    timestamp = Column(DateTime(timezone=True), nullable=False,
                      comment="Document timestamp for temporal filtering")
    conversation_context = Column(JSON, nullable=True,
                                comment="Conversation context when document was created")
    
    # Document Metadata
    source_type = Column(String(100), nullable=False,
                        comment="Document source: conversation, upload, system")
    source_reference = Column(String(255), nullable=True,
                            comment="Reference to source (node_id, file_name, etc.)")
    
    # Research Analytics
    retrieval_count = Column(Integer, default=0, nullable=False,
                           comment="Number of times document was retrieved")
    last_retrieved = Column(DateTime(timezone=True), nullable=True,
                          comment="Last retrieval timestamp")
    relevance_scores = Column(JSON, nullable=True,
                            comment="Historical relevance scores for research analysis")
    
    # Document State
    is_active = Column(Boolean, default=True, nullable=False)
    is_indexed = Column(Boolean, default=False, nullable=False,
                       comment="Whether document is indexed in ChromaDB")
    
    # Relationships
    session = relationship("UserSession", back_populates="vector_documents")
    
    # Indexes for Research Queries
    __table_args__ = (
        Index('ix_vector_documents_session_active', 'session_id', 'is_active'),
        Index('ix_vector_documents_timestamp', 'timestamp'),
        Index('ix_vector_documents_content_hash', 'content_hash'),
        Index('ix_vector_documents_source', 'source_type', 'source_reference'),
    )
    
    def __repr__(self):
        return f"<VectorDocument(id='{self.document_id}', source='{self.source_type}')>"


class ResearchAnalytics(BaseModel):
    """
    Research Analytics Model for Academic Publication
    
    Tracks detailed metrics and performance data for research analysis.
    Enables quantitative evaluation of the hierarchical chat innovations.
    
    Research Features:
    - Conversation flow analytics
    - Response quality metrics
    - System performance tracking
    - User interaction patterns
    """
    __tablename__ = "research_analytics"
    
    # Session Reference
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    
    # Analytics Type
    metric_name = Column(String(255), nullable=False,
                        comment="Metric name for research analysis")
    metric_category = Column(String(100), nullable=False,
                           comment="Metric category: performance, quality, usage")
    
    # Metric Data
    metric_value = Column(Float, nullable=False,
                         comment="Numeric metric value")
    metric_unit = Column(String(50), nullable=True,
                        comment="Metric unit (seconds, tokens, count, etc.)")
    metric_metadata = Column(JSON, nullable=True,
                           comment="Additional metric metadata")
    
    # Context
    conversation_tree_id = Column(UUID(as_uuid=True), nullable=True,
                                comment="Associated conversation tree")
    conversation_node_id = Column(UUID(as_uuid=True), nullable=True,
                                comment="Associated conversation node")
    
    # Timestamp
    measurement_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Indexes for Research Queries
    __table_args__ = (
        Index('ix_research_analytics_session_metric', 'session_id', 'metric_name'),
        Index('ix_research_analytics_timestamp', 'measurement_timestamp'),
        Index('ix_research_analytics_category', 'metric_category'),
    )
    
    def __repr__(self):
        return f"<ResearchAnalytics(metric='{self.metric_name}', value={self.metric_value})>"


class ConversationExport(BaseModel):
    """
    Conversation Export Model for Research Data Sharing
    
    Enables export of conversation data for academic collaboration
    and research publication while maintaining privacy controls.
    
    Research Features:
    - Structured conversation export
    - Privacy-aware data sharing
    - Multiple export formats
    - Research collaboration support
    """
    __tablename__ = "conversation_exports"
    
    # Session Reference
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    
    # Export Configuration
    export_name = Column(String(255), nullable=False,
                        comment="Human-readable export name")
    export_format = Column(String(50), nullable=False,
                          comment="Export format: json, csv, parquet")
    
    # Export Scope
    include_trees = Column(JSON, nullable=True,
                          comment="Tree IDs to include in export")
    include_metadata = Column(Boolean, default=True, nullable=False,
                            comment="Include research metadata")
    include_analytics = Column(Boolean, default=False, nullable=False,
                             comment="Include analytics data")
    
    # Privacy Controls
    anonymize_content = Column(Boolean, default=False, nullable=False,
                             comment="Anonymize message content")
    remove_timestamps = Column(Boolean, default=False, nullable=False,
                             comment="Remove timestamp data")
    
    # Export State
    export_status = Column(String(50), default="pending", nullable=False,
                          comment="Export status: pending, processing, completed, failed")
    export_path = Column(String(500), nullable=True,
                        comment="Path to exported file")
    file_size_bytes = Column(Integer, nullable=True,
                           comment="Export file size in bytes")
    
    # Export Metadata
    exported_at = Column(DateTime(timezone=True), nullable=True,
                        comment="Export completion timestamp")
    export_duration_ms = Column(Integer, nullable=True,
                               comment="Export processing duration")
    
    def __repr__(self):
        return f"<ConversationExport(name='{self.export_name}', status='{self.export_status}')>"


# ============================================================================
# DATABASE INITIALIZATION AND RESEARCH SUMMARY
# ============================================================================

def get_model_mapping_summary() -> Dict[str, Any]:
    """
    Get a comprehensive mapping between notebook classes and database models.
    
    This function provides clear documentation of how the research innovations
    from the notebook are preserved in the database schema.
    
    Returns:
        dict: Complete mapping between notebook and database implementations
    """
    return {
        "notebook_to_database_mapping": {
            "TreeNode": {
                "database_model": "ConversationNode",
                "description": "Hierarchical node structure with parent-child relationships",
                "research_innovation": "Preserves tree-based conversation flow",
                "key_fields": ["parent_id", "message_content", "node_depth", "context_used"]
            },
            "Forest": {
                "database_model": "ConversationTree", 
                "description": "Multiple conversation trees per session",
                "research_innovation": "Multi-tree conversation management",
                "key_fields": ["tree_index", "total_nodes", "max_depth", "root_node_id"]
            },
            "LocalBuffer": {
                "database_model": "MessageBuffer",
                "description": "Fixed-size buffer with timestamp filtering",
                "research_innovation": "Prevents context pollution",
                "key_fields": ["max_turns", "exclude_recent", "messages", "current_size"]
            },
            "GlobalVectorIndex": {
                "database_model": "VectorDocument",
                "description": "Vector embeddings with temporal metadata",
                "research_innovation": "Vector-based memory with time filtering",
                "key_fields": ["embedding_model", "timestamp", "retrieval_count", "content_hash"]
            },
            "ChatGraphManager": {
                "database_model": "UserSession",
                "description": "Session management and configuration",
                "research_innovation": "Multi-user research environment",
                "key_fields": ["session_id", "max_turns", "exclude_recent", "total_conversations"]
            }
        },
        "research_extensions": {
            "ResearchAnalytics": {
                "description": "Quantitative metrics for academic publication",
                "purpose": "Enables research evaluation and performance analysis"
            },
            "ConversationExport": {
                "description": "Research data sharing and collaboration",
                "purpose": "Academic collaboration and publication support"
            }
        },
        "preserved_innovations": [
            "Fixed-size message buffer with timestamp filtering (LocalBuffer)",
            "Hierarchical conversation nodes with parent-child relationships (TreeNode)",
            "Multi-tree conversation management per session (Forest)", 
            "Vector-based memory with temporal filtering (GlobalVectorIndex)",
            "Context assembly with overlap prevention (ChatAssembler)",
            "Session-based isolation for multi-user research"
        ]
    }


def create_all_tables(engine):
    """
    Create all database tables for the research backend.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables(engine):
    """
    Drop all database tables (use with caution in development).
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(bind=engine)
