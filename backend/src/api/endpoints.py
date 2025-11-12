from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from .schemas import (
    MessageRequest, MessageResponse, CreateConversationRequest,
    CreateSubchatRequest, ConversationHistory, ConversationNode
)
from ..services.simple_llm import SimpleChat
import time
import json

# 🧠 Single global chat instance with RAG ENABLED by default
chat_service = SimpleChat(enable_rag=True)

router = APIRouter()

@router.post("/conversations", response_model=ConversationNode)
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation tree with default title."""

    # Create with default title "New Chat"
    tree = chat_service.start_new_conversation(request.title)
    return ConversationNode(
        node_id=tree.node_id,
        title=tree.title,
        parent_id=None,
        children=[],
        path=tree.get_path(),
        message_count=tree.buffer.size()
    )

@router.post("/conversations/{node_id}/messages", response_model=MessageResponse)
async def send_message(node_id: str, request: MessageRequest):
    """Send a message to a conversation node with unified title generation."""
    try:
        chat_service.chat_manager.switch_node(node_id)
        
        # Send the message and get response (title generation handled internally)
        response = chat_service.send_message(request.message, disable_rag=request.disable_rag)
        
        # Get the current title (may have been updated during processing)
        current_node = chat_service.chat_manager.get_active_node()
        
        # Get actual usage data from LLM service
        usage = chat_service.llm.get_last_usage()
        
        return MessageResponse(
            response=response,
            message_id=f"{node_id}_{int(time.time())}",
            timestamp=time.time(),
            conversation_title=current_node.title,
            usage=usage
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Node not found") 

@router.post("/conversations/{node_id}/messages/stream")
async def send_message_stream(node_id: str, request: MessageRequest):
    """Send a message to a conversation node and stream the response token by token."""
    try:
        chat_service.chat_manager.switch_node(node_id)
        
        # 🎯 UNIFIED: Check if title needs to be generated BEFORE processing
        current_node = chat_service.chat_manager.get_active_node()
        needs_title_generation = current_node.title == "New Chat"
        
        def generate_stream():
            try:
                # Stream the response token by token
                for chunk in chat_service.send_message_stream(request.message):
                    # Send as Server-Sent Events format
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                
                # 🎯 UNIFIED: Send title update if it was generated
                if needs_title_generation:
                    # Get the updated title after processing
                    updated_node = chat_service.chat_manager.get_active_node()
                    if updated_node.title != "New Chat":
                        yield f"data: {json.dumps({'type': 'title', 'content': updated_node.title})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
            }
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Node not found")

@router.post("/conversations/{parent_id}/subchats", response_model=ConversationNode)
async def create_subchat(parent_id: str, request: CreateSubchatRequest):
    """Create a subchat under a parent node with optional follow-up context."""
    try:
        chat_service.chat_manager.switch_node(parent_id)
        
        # Create subchat with follow-up context information
        subchat = chat_service.chat_manager.create_node(
            title=request.title,
            parent_id=parent_id,
            selected_text=request.selected_text,
            follow_up_context=request.follow_up_context,
            context_type=request.context_type or "follow_up"
        )
        
        return ConversationNode(
            node_id=subchat.node_id,
            title=subchat.title,
            parent_id=parent_id,
            children=[],
            path=subchat.get_path(),
            message_count=subchat.buffer.size()
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Parent node not found")

@router.get("/conversations/{node_id}/history", response_model=ConversationHistory)
async def get_conversation_history(node_id: str):
    """Get conversation history for a node."""
    try:
        node = chat_service.chat_manager.get_node(node_id)
        messages = node.buffer.get_recent()
        
        return ConversationHistory(
            node_id=node.node_id,
            title=node.title,
            messages=messages,
            path=node.get_path()
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Node not found")

@router.get("/conversations/{node_id}", response_model=ConversationNode)
async def get_conversation_node(node_id: str):
    """Get information about a conversation node."""
    try:
        node = chat_service.chat_manager.get_node(node_id)
        
        return ConversationNode(
            node_id=node.node_id,
            title=node.title,
            parent_id=node.parent.node_id if node.parent else None,
            children=[child.node_id for child in node.children],
            path=node.get_path(),
            message_count=node.buffer.size()
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Node not found")


@router.post("/generate-title")
async def generate_ai_title(request: dict):
    """Generate AI-powered title from user question"""
    try:
        question = request.get("question", "")
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # Use the chat service to generate AI title
        generated_title = chat_service.generate_title_from_question(question)
        
        return {"title": generated_title}
    except Exception as e:
        print(f"❌ Error generating AI title: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate title")