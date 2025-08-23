"""
Core Configuration Module for Hierarchical Chat Research Backend

This module manages all application settings using Pydantic Settings,
ensuring type safety and validation for the research environment.

The configuration preserves all research parameters from the original notebook
while adding production-grade settings for deployment and scalability.
"""

from typing import List, Optional, Any
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Application Settings for Hierarchical Chat Research Backend
    
    This class manages all configuration parameters, preserving the research
    notebook settings while adding production capabilities.
    """
    
    # =========================================================================
    # CORE APPLICATION SETTINGS
    # =========================================================================
    app_name: str = Field(default="Hierarchical Chat Research Backend", description="Application name")
    environment: str = Field(default="development", description="Environment: development/staging/production")
    debug: bool = Field(default=True, description="Enable debug mode")
    api_version: str = Field(default="1.0.0", description="API version")
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT tokens and encryption")
    access_token_expire_minutes: int = Field(default=1440, description="Token expiration time in minutes")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # =========================================================================
    # DATABASE CONFIGURATION (Research Data Persistence)
    # =========================================================================
    database_url: str = Field(..., description="PostgreSQL database URL for research data")
    dev_database_url: str = Field(default="sqlite:///./research_data.db", description="Development SQLite URL")
    use_sqlite_for_dev: bool = Field(default=True, description="Use SQLite for development")
    
    # Database Pool Settings (for research workloads)
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Maximum overflow connections")
    database_pool_timeout: int = Field(default=30, description="Pool timeout in seconds")
    
    @property
    def effective_database_url(self) -> str:
        """Get the effective database URL based on environment"""
        if self.environment == "development" and self.use_sqlite_for_dev:
            return self.dev_database_url
        return self.database_url
    
    # =========================================================================
    # LLM CONFIGURATION (Multiple LLM Providers for Research)
    # =========================================================================
    # OpenAI Configuration (Primary LLM)
    openai_api_key: str = Field(..., description="OpenAI API key for LLM responses")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model name for research")
    openai_temperature: float = Field(default=0.7, description="LLM temperature for response generation")
    openai_max_tokens: int = Field(default=2000, description="Maximum tokens per LLM response")
    openai_request_timeout: int = Field(default=60, description="OpenAI API request timeout")
    
    # Groq Configuration (Fast Inference Alternative)
    groq_api_key: str = Field(..., description="Groq API key for fast inference")
    groq_model: str = Field(default="llama3-70b-8192", description="Groq model for research")
    groq_temperature: float = Field(default=0.7, description="Groq temperature setting")
    groq_max_tokens: int = Field(default=2048, description="Maximum tokens for Groq responses")
    
    # LangChain Configuration (Research Tools)
    langchain_api_key: str = Field(..., description="LangChain API key for research tools")
    langchain_tracing: bool = Field(default=True, description="Enable LangChain tracing")
    
    # LLM Provider Selection
    primary_llm_provider: str = Field(default="openai", description="Primary LLM provider (openai/groq)")
    fallback_llm_provider: str = Field(default="groq", description="Fallback LLM provider")
    
    @field_validator('openai_temperature', 'groq_temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v
    
    @field_validator('primary_llm_provider', 'fallback_llm_provider')
    def validate_llm_provider(cls, v):
        valid_providers = ['openai', 'groq']
        if v not in valid_providers:
            raise ValueError(f'LLM provider must be one of {valid_providers}')
        return v
    
    # =========================================================================
    # VECTOR STORE CONFIGURATION (ChromaDB + Sentence Transformers)
    # =========================================================================
    chroma_persist_directory: str = Field(default="./data/chromadb", description="ChromaDB persistence directory")
    chroma_collection_name: str = Field(default="hierarchical_chat_research", description="ChromaDB collection name")
    
    # Sentence Transformers Configuration (No API costs)
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformers model name")
    embedding_device: str = Field(default="cpu", description="Device for embeddings: cpu or cuda")
    embedding_batch_size: int = Field(default=32, description="Batch size for embedding generation")
    
    @field_validator('chroma_persist_directory')
    def create_chroma_directory(cls, v):
        """Ensure ChromaDB directory exists"""
        Path(v).mkdir(parents=True, exist_ok=True)
        return v
    
    # =========================================================================
    # RESEARCH-SPECIFIC SETTINGS (From Notebook Implementation)
    # =========================================================================
    
    # LocalBuffer Settings (Core Research Innovation)
    default_max_turns: int = Field(default=50, description="Default LocalBuffer max turns (from notebook)")
    default_exclude_recent: int = Field(default=10, description="Default recent messages to exclude (from notebook)")
    
    # Context Assembly Settings (Research Parameters)
    max_context_tokens: int = Field(default=4000, description="Maximum context tokens for LLM")
    max_retrieved_docs: int = Field(default=5, description="Maximum documents to retrieve from vector store")
    context_overlap_threshold: float = Field(default=0.8, description="Context overlap threshold for deduplication")
    
    # Forest Management (Multi-tree Research Innovation)
    max_trees_per_session: int = Field(default=10, description="Maximum conversation trees per session")
    max_nodes_per_tree: int = Field(default=100, description="Maximum nodes per conversation tree")
    
    # Research Metrics Collection
    enable_research_metrics: bool = Field(default=True, description="Enable research metrics collection")
    metrics_collection_interval: int = Field(default=60, description="Metrics collection interval in seconds")
    
    @field_validator('default_max_turns')
    def validate_max_turns(cls, v):
        if v <= 0:
            raise ValueError('Max turns must be positive')
        return v
    
    @field_validator('default_exclude_recent')
    def validate_exclude_recent(cls, v):
        if v < 0:
            raise ValueError('Exclude recent must be non-negative')
        return v
    
    # =========================================================================
    # FRONTEND INTEGRATION SETTINGS
    # =========================================================================
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
        description="Allowed CORS origins for frontend integration"
    )
    allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    frontend_url: str = Field(default="http://localhost:3000", description="Frontend URL")
    
    # =========================================================================
    # REDIS CONFIGURATION (Session Management)
    # =========================================================================
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL for session storage")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_session_ttl: int = Field(default=86400, description="Redis session TTL in seconds")
    
    # =========================================================================
    # LOGGING & MONITORING
    # =========================================================================
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        description="Log format string"
    )
    log_file: str = Field(default="./logs/hierarchical_chat.log", description="Log file path")
    log_rotation: str = Field(default="10 MB", description="Log rotation size")
    log_retention: str = Field(default="30 days", description="Log retention period")
    
    @field_validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()
    
    # =========================================================================
    # RESEARCH DATA EXPORT & ANALYTICS
    # =========================================================================
    enable_conversation_analytics: bool = Field(default=True, description="Enable conversation analytics")
    analytics_export_path: str = Field(default="./data/analytics", description="Analytics export path")
    export_format: str = Field(default="json", description="Export format: json, csv, parquet")
    export_directory: str = Field(default="./data/exports", description="Export directory")
    auto_export_interval: int = Field(default=3600, description="Auto export interval in seconds")
    
    # Research Backup Settings
    backup_enabled: bool = Field(default=True, description="Enable automatic backups")
    backup_directory: str = Field(default="./data/backups", description="Backup directory")
    backup_retention_days: int = Field(default=30, description="Backup retention in days")
    
    @field_validator('export_format')
    def validate_export_format(cls, v):
        valid_formats = ["json", "csv", "parquet"]
        if v.lower() not in valid_formats:
            raise ValueError(f'Export format must be one of {valid_formats}')
        return v.lower()
    
    # =========================================================================
    # PERFORMANCE TUNING
    # =========================================================================
    http_timeout: int = Field(default=30, description="HTTP client timeout")
    http_max_connections: int = Field(default=100, description="Maximum HTTP connections")
    http_max_keepalive_connections: int = Field(default=20, description="Maximum keepalive connections")
    
    # Vector Search Performance
    vector_search_timeout: int = Field(default=10, description="Vector search timeout in seconds")
    vector_index_batch_size: int = Field(default=100, description="Vector indexing batch size")
    
    # =========================================================================
    # SECURITY SETTINGS
    # =========================================================================
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    max_request_size: int = Field(default=10485760, description="Maximum request size in bytes (10MB)")
    max_upload_size: int = Field(default=52428800, description="Maximum upload size in bytes (50MB)")
    
    # HTTPS Settings
    force_https: bool = Field(default=False, description="Force HTTPS redirects")
    https_redirect: bool = Field(default=False, description="Enable HTTPS redirects")
    
    # =========================================================================
    # DEVELOPMENT SETTINGS
    # =========================================================================
    enable_debug_routes: bool = Field(default=True, description="Enable debug API routes")
    enable_admin_panel: bool = Field(default=True, description="Enable admin panel")
    auto_reload: bool = Field(default=True, description="Enable auto-reload in development")
    
    # API Documentation
    enable_docs: bool = Field(default=True, description="Enable API documentation")
    docs_url: str = Field(default="/docs", description="API docs URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    
    # =========================================================================
    # RESEARCH COLLABORATION SETTINGS
    # =========================================================================
    enable_user_sessions: bool = Field(default=True, description="Enable multi-user sessions")
    session_isolation: bool = Field(default=True, description="Isolate user sessions")
    shared_vector_store: bool = Field(default=False, description="Share vector store across users")
    
    # Data Export API
    enable_data_export_api: bool = Field(default=True, description="Enable data export API")
    enable_analytics_api: bool = Field(default=True, description="Enable analytics API")
    require_auth_for_export: bool = Field(default=True, description="Require authentication for data export")
    
    # =========================================================================
    # COMPUTED PROPERTIES
    # =========================================================================
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    @property
    def database_echo(self) -> bool:
        """Enable database query logging in development"""
        return self.is_development and self.debug
    
    @property
    def cors_enabled(self) -> bool:
        """Enable CORS in non-production environments"""
        return not self.is_production or len(self.allowed_origins) > 0
    
    # =========================================================================
    # DIRECTORY CREATION
    # =========================================================================
    
    def create_directories(self) -> None:
        """Create necessary directories for the application"""
        directories = [
            self.chroma_persist_directory,
            self.analytics_export_path,
            self.export_directory,
            self.backup_directory,
            Path(self.log_file).parent,
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    This function returns a cached instance of the Settings class,
    ensuring that environment variables are read only once during
    application startup for better performance.
    
    Returns:
        Settings: Cached application settings instance
    """
    settings = Settings()
    
    # Create necessary directories on startup
    settings.create_directories()
    
    return settings


# Global settings instance for import
settings = get_settings()


# ============================================================================
# RESEARCH CONFIGURATION SUMMARY
# ============================================================================
def get_research_config_summary() -> dict:
    """
    Get a summary of research-specific configuration parameters.
    
    This function provides a clear overview of all research parameters
    that preserve the notebook's innovative features.
    
    Returns:
        dict: Research configuration summary
    """
    return {
        "local_buffer": {
            "max_turns": settings.default_max_turns,
            "exclude_recent": settings.default_exclude_recent,
            "description": "Fixed-size message buffer with timestamp filtering (Research Innovation #1)"
        },
        "context_assembly": {
            "max_tokens": settings.max_context_tokens,
            "max_retrieved_docs": settings.max_retrieved_docs,
            "overlap_threshold": settings.context_overlap_threshold,
            "description": "Intelligent context assembly preventing pollution (Research Innovation #2)"
        },
        "forest_management": {
            "max_trees_per_session": settings.max_trees_per_session,
            "max_nodes_per_tree": settings.max_nodes_per_tree,
            "description": "Multi-tree conversation management (Research Innovation #3)"
        },
        "vector_store": {
            "collection_name": settings.chroma_collection_name,
            "embedding_model": settings.embedding_model_name,
            "persist_directory": settings.chroma_persist_directory,
            "description": "Vector-based memory with temporal filtering (Research Innovation #4)"
        },
        "llm_configuration": {
            "primary_provider": settings.primary_llm_provider,
            "primary_model": settings.openai_model if settings.primary_llm_provider == "openai" else settings.groq_model,
            "fallback_provider": settings.fallback_llm_provider,
            "temperature": settings.openai_temperature,
            "max_tokens": settings.openai_max_tokens,
            "langchain_tracing": settings.langchain_tracing,
            "description": "Multi-provider LLM integration with fallback (Research Innovation #5)"
        }
    }
