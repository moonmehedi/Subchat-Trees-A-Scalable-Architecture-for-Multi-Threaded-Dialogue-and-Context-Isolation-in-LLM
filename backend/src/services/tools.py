"""
Agentic tools for LLM to call when needed.
Enables intelligent retrieval based on LLM's analysis of user intent.
"""

from typing import List, Dict, Any


class ConversationTools:
    """Tools that LLM can call to search conversation history"""
    
    @staticmethod
    def get_tool_definitions() -> List[Dict[str, Any]]:
        """
        Get tool definitions for function calling.
        These are provided to the LLM which decides when to use them.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_conversation_history",
                    "description": "Search archived conversation messages beyond the recent buffer (last 10 messages). Returns relevant messages from past conversations based on semantic similarity. Use for retrieving user's personal information or specific past discussion topics that are NOT in the recent 10 messages. ** IF UNSURE DONT USE IT **",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Specific search query - be precise about what to find (e.g., 'Python programming discussion' or 'database schema design')"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of relevant messages to retrieve from archives. Recommend 3-5 for good context coverage.",
                                "default": 5,
                                "minimum": 3,
                                "maximum": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    @staticmethod
    def execute_tool(tool_name: str, arguments: Dict[str, Any], vector_index, node) -> str:
        """
        Execute a tool and return formatted results.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments from LLM
            vector_index: GlobalVectorIndex instance
            node: Current TreeNode
            
        Returns:
            Formatted string with tool results
        """
        if tool_name == "search_conversation_history":
            return ConversationTools._execute_search(arguments, vector_index, node)
        else:
            return f"Unknown tool: {tool_name}"
    
    @staticmethod
    def _execute_search(arguments: Dict[str, Any], vector_index, node) -> str:
        """Execute conversation history search - searches across ALL conversations"""
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 5)  # Default to 5 for better context
        
        # Enforce minimum of 3 messages for comprehensive context
        top_k = max(3, top_k)
        
        # Get buffer cutoff timestamp - exclude ALL messages currently in buffer
        # (default behavior excludes all buffer messages to avoid redundancy)
        buffer_cutoff = node.buffer.get_cutoff_timestamp()
        
        print(f"📊 Search context:")
        print(f"   Current conversation buffer has {node.buffer.size()} messages (will be excluded)")
        print(f"   Searching ACROSS ALL CONVERSATIONS for: '{query}'")
        print(f"   Retrieving top {top_k} relevant messages")
        
        # 🔍 Use ENHANCED multi-query retrieval with context windows
        results = vector_index.retrieve_with_multi_query(
            query=query,
            top_k=top_k,
            node_id=None,  # ✅ Search globally across all conversations
            exclude_buffer_cutoff=buffer_cutoff,
            use_context_windows=True  # ✅ Get ±60s context around relevant messages
        )
        
        if not results:
            return f"No archived messages found for query: '{query}'. The conversation may not have enough history yet, or relevant context is already in recent messages."
        
        # Format results for LLM with context markers
        formatted = f"Retrieved {len(results)} archived messages (beyond recent buffer):\n\n"
        for i, result in enumerate(results, 1):
            role = result['metadata'].get('role', 'unknown')
            text = result['text']
            score = result['score']
            is_context = result.get('is_context', False)
            context_marker = " [CONTEXT]" if is_context else ""
            
            formatted += f"{i}. [{role.upper()}]{context_marker} {text}\n   (relevance: {score:.2f})\n\n"
        
        return formatted.strip()


# For testing
if __name__ == "__main__":
    print("🧪 Testing ConversationTools...")
    
    tools = ConversationTools.get_tool_definitions()
    print(f"\n✅ Defined {len(tools)} tool(s)")
    
    for tool in tools:
        print(f"\nTool: {tool['function']['name']}")
        print(f"Description: {tool['function']['description'][:100]}...")
        print(f"Parameters: {list(tool['function']['parameters']['properties'].keys())}")
    
    print("\n✅ ConversationTools test passed!")
