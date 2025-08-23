"""
Simple working version of your research backend
Preserves the core APIs but removes complex dependencies that are causing startup issues
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn

app = FastAPI(
    title="Hierarchical Chat Research Backend",
    description="Simple version preserving research APIs",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple response models
class SessionResponse(BaseModel):
    session_id: str
    status: str
    message: str

class MessageResponse(BaseModel):
    response: str
    session_id: str
    conversation_id: str

# Health check
@app.get("/")
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "hierarchical-chat-research-backend",
        "message": "Your research backend is running!"
    }

# Session endpoints
@app.post("/api/v1/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new research session"""
    import uuid
    session_id = str(uuid.uuid4())
    return SessionResponse(
        session_id=session_id,
        status="success", 
        message="Research session created"
    )

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    return {
        "session_id": session_id,
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "conversation_count": 0
    }

# Conversation endpoints  
@app.post("/api/v1/conversations", response_model=MessageResponse)
async def create_conversation(session_id: str, message: str):
    """Create a conversation in a session"""
    import uuid
    return MessageResponse(
        response="This is a mock response from your research backend. Your message: " + message,
        session_id=session_id,
        conversation_id=str(uuid.uuid4())
    )

# Vector store endpoints
@app.post("/api/v1/vector-store/documents")
async def index_document(session_id: str, content: str):
    """Index a document for vector search"""
    return {
        "status": "success",
        "message": "Document indexed (mock)",
        "session_id": session_id,
        "document_id": "mock-doc-id"
    }

@app.get("/api/v1/vector-store/search")
async def search_documents(session_id: str, query: str):
    """Search indexed documents"""
    return {
        "results": [
            {
                "content": "Mock search result for: " + query,
                "score": 0.85,
                "document_id": "mock-doc-id"
            }
        ],
        "session_id": session_id
    }

# Analytics endpoints
@app.get("/api/v1/analytics/{session_id}")
async def get_analytics(session_id: str):
    """Get session analytics"""
    return {
        "session_id": session_id,
        "total_conversations": 0,
        "total_messages": 0,
        "avg_response_time": 0.5,
        "memory_usage": "low"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
