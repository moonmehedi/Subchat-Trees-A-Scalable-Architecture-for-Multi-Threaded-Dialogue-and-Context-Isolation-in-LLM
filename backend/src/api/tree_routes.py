"""
API endpoints for conversation tree visualization.
Provides real-time tree structure data for web visualization.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from typing import List, Dict, Any
from pathlib import Path
from ..services.simple_llm import SimpleChat
from ..utils.tree_visualizer import get_tree_visualizer

router = APIRouter()


@router.get("/tree/structure")
async def get_tree_structure(conversation_id: str = None):
    """
    Get tree structure as JSON for a specific conversation or all conversations.
    
    Args:
        conversation_id: Optional conversation ID. If not provided, returns all trees.
    
    Returns:
        JSON tree structure with metadata
    """
    try:
        from ..api.endpoints import chat_service
        
        visualizer = get_tree_visualizer()
        
        if conversation_id:
            # Get specific conversation tree
            node = chat_service.chat_manager.get_node(conversation_id)
            if not node:
                raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
            
            # Get root of this tree
            root = node
            while root.parent:
                root = root.parent
            
            tree_structure = visualizer.build_tree_structure(root)
            return JSONResponse(content=tree_structure)
        else:
            # Get all conversation trees
            all_roots = chat_service.chat_manager.get_all_roots()
            
            all_trees = {
                'conversations': [visualizer.build_tree_structure(root) for root in all_roots],
                'metadata': {
                    'total_conversations': len(all_roots),
                    'total_nodes': sum(visualizer._count_nodes(root) for root in all_roots)
                }
            }
            
            return JSONResponse(content=all_trees)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tree/ascii")
async def get_ascii_tree(conversation_id: str = None):
    """
    Get ASCII art tree visualization.
    
    Args:
        conversation_id: Optional conversation ID. If not provided, returns all trees.
    
    Returns:
        Plain text ASCII tree
    """
    try:
        from ..api.endpoints import chat_service
        
        visualizer = get_tree_visualizer()
        
        if conversation_id:
            # Get specific conversation tree
            node = chat_service.chat_manager.get_node(conversation_id)
            if not node:
                raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
            
            # Get root of this tree
            root = node
            while root.parent:
                root = root.parent
            
            ascii_tree = visualizer.generate_ascii_tree(root, show_stats=True)
            return PlainTextResponse(content=ascii_tree)
        else:
            # Get all conversation trees
            all_roots = chat_service.chat_manager.get_all_roots()
            
            lines = []
            lines.append("═" * 80)
            lines.append("        🌳 ALL CONVERSATION TREES")
            lines.append("═" * 80)
            lines.append(f"\n📊 Total Conversations: {len(all_roots)}\n")
            
            for i, root in enumerate(all_roots, 1):
                lines.append(f"\n{'─' * 80}")
                lines.append(f"🌳 Conversation {i}:")
                lines.append("─" * 80)
                lines.append(visualizer.generate_ascii_tree(root, show_stats=False))
            
            return PlainTextResponse(content="\n".join(lines))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tree/stats")
async def get_tree_stats(conversation_id: str = None):
    """
    Get statistics about conversation tree(s).
    
    Args:
        conversation_id: Optional conversation ID. If not provided, returns stats for all trees.
    
    Returns:
        JSON with tree statistics
    """
    try:
        from ..api.endpoints import chat_service
        
        visualizer = get_tree_visualizer()
        
        if conversation_id:
            # Get specific conversation stats
            node = chat_service.chat_manager.get_node(conversation_id)
            if not node:
                raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
            
            # Get root of this tree
            root = node
            while root.parent:
                root = root.parent
            
            stats = visualizer.get_tree_stats(root)
            return JSONResponse(content=stats)
        else:
            # Get stats for all trees
            all_roots = chat_service.chat_manager.get_all_roots()
            
            all_stats = {
                'total_conversations': len(all_roots),
                'total_nodes': sum(visualizer._count_nodes(root) for root in all_roots),
                'conversations': [
                    {
                        'id': root.node_id,
                        'title': root.title,
                        **visualizer.get_tree_stats(root)
                    }
                    for root in all_roots
                ]
            }
            
            return JSONResponse(content=all_stats)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tree/save")
async def save_tree_to_file():
    """
    Save current tree structure to log files (ASCII and JSON).
    
    Returns:
        Paths to saved files
    """
    try:
        from ..api.endpoints import chat_service
        
        visualizer = get_tree_visualizer()
        all_roots = chat_service.chat_manager.get_all_roots()
        
        result = visualizer.save_all_trees(all_roots, mode='overwrite')
        
        return JSONResponse(content={
            'status': 'success',
            'files': result,
            'total_conversations': len(all_roots)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tree/visualization")
async def get_visualization_page():
    """
    Serve the HTML visualization page.
    
    Returns:
        HTML file for interactive tree visualization
    """
    try:
        # Path to visualization HTML
        backend_dir = Path(__file__).parent.parent.parent
        html_file = backend_dir / "logs" / "tree_visualization" / "index.html"
        
        if not html_file.exists():
            raise HTTPException(status_code=404, detail="Visualization page not found. Run setup first.")
        
        return FileResponse(html_file, media_type="text/html")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
