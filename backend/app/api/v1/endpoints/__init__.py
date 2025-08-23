"""
API Router Initialization Files

This package contains all API endpoint routers for the hierarchical chat
research backend, organized by functionality and preserving notebook innovations.
"""

# API v1 endpoint routers
from .conversations import router as conversations_router  
from .sessions import router as sessions_router
from .analytics import router as analytics_router
from .vector_store import router as vector_store_router

__all__ = [
    "conversations_router",
    "sessions_router", 
    "analytics_router",
    "vector_store_router"
]
