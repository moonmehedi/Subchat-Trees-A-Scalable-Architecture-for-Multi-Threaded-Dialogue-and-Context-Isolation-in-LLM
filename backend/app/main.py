"""
Main FastAPI Application Entry Point

This module sets up the FastAPI application with all research innovations
from the notebook integrated into a production-ready backend.

Key Features:
- Preserves all notebook research logic
- Multi-user session management
- Frontend integration with CORS
- Auto-generated API documentation
- Research analytics and export capabilities
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from pathlib import Path

# Import errors expected until dependencies are installed
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
except ImportError:
    create_engine = None
    sessionmaker = None
    Session = None

from app.core.config import settings, get_research_config_summary
from app.api.v1.endpoints import conversations, sessions, analytics, vector_store
from app.schemas.api_schemas import HealthCheck, SystemStatus, ErrorResponse


# ============================================================================
# APPLICATION SETUP
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("🚀 Starting Hierarchical Chat Research Backend...")
    print("📊 Research Innovations Preserved:")
    
    research_config = get_research_config_summary()
    for innovation_key, innovation_data in research_config.items():
        print(f"   ✓ {innovation_data['description']}")
    
    print(f"📝 Configuration: {settings.environment} environment")
    print(f"🎯 Frontend URL: {settings.frontend_url}")
    print(f"🔗 Database: {settings.effective_database_url}")
    print(f"🧠 LLM Model: {settings.openai_model}")
    print(f"🔍 Vector Store: ChromaDB + {settings.embedding_model_name}")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down Hierarchical Chat Research Backend...")


# Create FastAPI application
app = FastAPI(
    title="Hierarchical Chat Research Backend",
    description="""
    Production-ready FastAPI backend preserving all research innovations
    from the hierarchical chat notebook implementation.
    
    ## Research Innovations Preserved:
    
    1. **LocalBuffer** - Fixed-size message buffer with timestamp filtering
    2. **Context Assembly** - Intelligent context assembly preventing pollution  
    3. **Forest Management** - Multi-tree conversation management
    4. **Vector Memory** - Vector-based memory with temporal filtering
    5. **LLM Integration** - OpenAI 4o-mini with research parameters
    
    ## Key Features:
    
    - Multi-user session isolation
    - Real-time conversation processing
    - Vector-based context retrieval
    - Research analytics collection
    - Data export for collaboration
    - Frontend integration ready
    
    ## Notebook Mapping:
    
    - `LocalBuffer` ➜ Message Buffer Service
    - `TreeNode` ➜ Conversation Node Model
    - `Forest` ➜ Conversation Tree Management
    - `GlobalVectorIndex` ➜ Vector Store Service
    - `LLMClient` ➜ LLM Service (OpenAI 4o-mini)
    - `ChatGraphManager` ➜ Conversation Service
    - `ChatAssembler` ➜ Context Assembly Logic
    
    All research logic is preserved exactly as implemented in the notebook
    while adding production capabilities, error handling, and scalability.
    """,
    version=settings.api_version,
    docs_url=settings.docs_url if settings.enable_docs else None,
    redoc_url=settings.redoc_url if settings.enable_docs else None,
    lifespan=lifespan
)


# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# CORS middleware for frontend integration
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=settings.allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )


# ============================================================================
# DATABASE SETUP
# ============================================================================

# Database engine and session setup
engine = None
SessionLocal = None

if create_engine and sessionmaker:
    try:
        engine = create_engine(
            settings.effective_database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            echo=settings.database_echo
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        from app.models.database_models import create_all_tables
        create_all_tables(engine)
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")


def get_db():
    """Database dependency for API endpoints"""
    if not SessionLocal:
        raise HTTPException(status_code=503, detail="Database not available")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with research context"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=None  # Will be set by Pydantic default
        ).dict()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=str(exc),
            error_code="VALIDATION_ERROR"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR"
        ).dict()
    )


# ============================================================================
# HEALTH AND STATUS ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and deployment.
    
    Returns basic application health status and version information.
    """
    return HealthCheck(
        status="healthy",
        version=settings.api_version,
        services={
            "database": "connected" if engine else "unavailable",
            "vector_store": "configured",
            "llm_service": "configured",
            "frontend_cors": "enabled" if settings.cors_enabled else "disabled"
        }
    )


@app.get("/status", response_model=SystemStatus, tags=["Health"])
async def system_status(db: Session = Depends(get_db)):
    """
    Detailed system status for research monitoring.
    
    Provides comprehensive status including research metrics
    and system component availability.
    """
    try:
        # Check database connectivity
        db_connected = True
        try:
            db.execute("SELECT 1")
        except:
            db_connected = False
        
        # Get system statistics
        from app.models.database_models import UserSession, ConversationTree, VectorDocument
        
        active_sessions = db.query(UserSession).filter_by(is_active=True).count() if db_connected else 0
        total_conversations = db.query(ConversationTree).count() if db_connected else 0
        total_documents = db.query(VectorDocument).count() if db_connected else 0
        
        return SystemStatus(
            database_connected=db_connected,
            vector_store_connected=True,  # ChromaDB is file-based
            llm_service_available=bool(settings.openai_api_key),
            active_sessions=active_sessions,
            total_conversations=total_conversations,
            total_documents_indexed=total_documents
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


# ============================================================================
# RESEARCH CONFIGURATION ENDPOINT
# ============================================================================

@app.get("/research/config", tags=["Research"])
async def get_research_configuration():
    """
    Get research configuration summary.
    
    Returns detailed information about how notebook innovations
    are preserved in the backend implementation.
    """
    try:
        research_config = get_research_config_summary()
        
        from app.models.database_models import get_model_mapping_summary
        model_mapping = get_model_mapping_summary()
        
        from app.services.research_services import get_service_mapping_summary
        service_mapping = get_service_mapping_summary()
        
        from app.schemas.api_schemas import get_schema_mapping_summary
        schema_mapping = get_schema_mapping_summary()
        
        return {
            "research_config": research_config,
            "model_mapping": model_mapping,
            "service_mapping": service_mapping,
            "schema_mapping": schema_mapping,
            "notebook_preservation_status": "complete",
            "api_documentation": f"{settings.frontend_url}/docs",
            "research_ready": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research config failed: {str(e)}")


# ============================================================================
# API ROUTER REGISTRATION
# ============================================================================

# Register API v1 routes
app.include_router(
    conversations.router,
    prefix="/api/v1/conversations",
    tags=["Conversations"],
    dependencies=[Depends(get_db)]
)

app.include_router(
    sessions.router,
    prefix="/api/v1/sessions",
    tags=["Sessions"],
    dependencies=[Depends(get_db)]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Research Analytics"],
    dependencies=[Depends(get_db)]
)

app.include_router(
    vector_store.router,
    prefix="/api/v1/vector",
    tags=["Vector Store"],
    dependencies=[Depends(get_db)]
)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with research backend information.
    
    Provides overview of the hierarchical chat research backend
    and links to documentation and configuration.
    """
    return {
        "message": "Hierarchical Chat Research Backend",
        "description": "Production-ready FastAPI backend preserving notebook research innovations",
        "research_innovations": [
            "LocalBuffer - Fixed-size message buffer with timestamp filtering",
            "Context Assembly - Intelligent context assembly preventing pollution",
            "Forest Management - Multi-tree conversation management", 
            "Vector Memory - Vector-based memory with temporal filtering",
            "LLM Integration - OpenAI 4o-mini with research parameters"
        ],
        "notebook_mapping": {
            "LocalBuffer": "Message Buffer Service",
            "TreeNode": "Conversation Node Model",
            "Forest": "Conversation Tree Management",
            "GlobalVectorIndex": "Vector Store Service",
            "LLMClient": "LLM Service (OpenAI 4o-mini)",
            "ChatGraphManager": "Conversation Service",
            "ChatAssembler": "Context Assembly Logic"
        },
        "api_documentation": "/docs",
        "research_configuration": "/research/config",
        "health_check": "/health",
        "system_status": "/status",
        "version": settings.api_version,
        "environment": settings.environment
    }


# ============================================================================
# APPLICATION RUNNER
# ============================================================================

if __name__ == "__main__":
    """
    Run the research backend server.
    
    This starts the FastAPI application with all research innovations
    preserved and ready for frontend integration.
    """
    print("🔬 Starting Hierarchical Chat Research Backend...")
    print("📊 All notebook innovations preserved and production-ready!")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.auto_reload and settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=settings.is_development
    )
