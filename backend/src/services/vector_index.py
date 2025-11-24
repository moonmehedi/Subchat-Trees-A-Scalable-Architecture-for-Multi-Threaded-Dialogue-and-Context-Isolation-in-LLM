"""
Global Vector Index for long-term conversation memory.
Auto-archives messages when they're evicted from LocalBuffer.

ENHANCED WITH:
- Multi-query decomposition for better retrieval
- Context window retrieval (±60s around relevant messages)
- Intent-aware query generation
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional, Any, Set
import os
from pathlib import Path
import time
import json
from groq import Groq
from src.utils.debug_logger import get_debug_logger
from src.cores.config import settings


class QueryDecomposer:
    """
    Decomposes vague queries into multiple specific sub-queries.
    
    PROBLEM: Semantic search fails with vague queries like "user identity information"
    SOLUTION: Generate 5-7 targeted sub-queries that capture specific patterns
    
    Example:
        Query: "who am i?" or "user identity information"
        Sub-queries: ["my name is", "I am a", "I study", "I work as", "my favorite"]
    """
    
    def __init__(self):
        """Initialize with Groq LLM for query generation"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=api_key)
        self.model = settings.model_base
    
    def classify_intent(self, query: str) -> str:
        """
        Classify query intent to guide sub-query generation.
        
        Intents:
        - identity: Questions about user (name, occupation, preferences)
        - preference: Questions about user likes/dislikes
        - discussion: Questions about past conversations
        - factual: Questions about facts/information shared
        - general: General questions
        """
        query_lower = query.lower()
        
        # Identity keywords
        if any(kw in query_lower for kw in ["who am i", "my name", "about me", "user identity"]):
            return "identity"
        
        # Preference keywords
        if any(kw in query_lower for kw in ["favorite", "prefer", "like", "love", "hate", "dislike"]):
            return "preference"
        
        # Discussion keywords
        if any(kw in query_lower for kw in ["discussed", "talked about", "mentioned", "said earlier"]):
            return "discussion"
        
        # Factual keywords
        if any(kw in query_lower for kw in ["what is", "define", "explain", "how does"]):
            return "factual"
        
        return "general"
    
    def generate_sub_queries(self, query: str, intent: str) -> List[str]:
        """
        Generate 5-7 targeted sub-queries based on intent.
        
        Uses LLM to generate diverse, specific queries that capture
        different aspects of the user's vague query.
        """
        # Base template - all prompts share this structure
        base_template = """Given query: "{query}"
Intent: {intent_description}

Generate 5-7 SHORT, SPECIFIC search queries. {focus_hint}

Return ONLY a JSON array of strings: ["query1", "query2", ...]

Example: {example}"""

        # Intent-specific configurations
        intent_configs = {
            "identity": {
                "description": "user identity/introduction",
                "focus": "Focus on: 'my name is', 'I am a', 'I work as', 'I study'",
                "example": '["my name is", "I am a student", "I work as", "I study", "about myself"]'
            },
            "preference": {
                "description": "user preferences/likes",
                "focus": "Focus on: 'my favorite', 'I like', 'I love', 'I prefer', 'I hate'",
                "example": '["my favorite", "I like", "I love", "I prefer", "I enjoy"]'
            },
            "discussion": {
                "description": "past conversation topics",
                "focus": "Focus on: key topics, entities, concepts",
                "example": '["python programming", "snake facts", "decorators", "async"]'
            },
            "factual": {
                "description": "factual information",
                "focus": "Break down into: concepts, entities, related topics",
                "example": '["capital france", "paris location", "french capital", "france geography"]'
            },
            "general": {
                "description": "general information",
                "focus": "Extract: key entities, topics, concepts",
                "example": '["user data", "personal info", "account details"]'
            }
        }
        
        # Get config or use general as fallback
        config = intent_configs.get(intent, intent_configs["general"])
        
        # Build prompt from template
        prompt = base_template.format(
            query=query,
            intent_description=config["description"],
            focus_hint=config["focus"],
            example=config["example"]
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Generate focused search query arrays. Output ONLY JSON string arrays: [\"q1\", \"q2\"]. No objects, no extra text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON array
            sub_queries = json.loads(result)
            
            # Validate it's a list
            if not isinstance(sub_queries, list):
                raise ValueError("Expected JSON array")
            
            # Extract strings from various formats
            # Handle both ["query1", "query2"] and [{"query": "query1"}, {"query": "query2"}]
            cleaned_queries = []
            for sq in sub_queries:
                if isinstance(sq, str):
                    cleaned_queries.append(sq)
                elif isinstance(sq, dict):
                    # Extract 'query' field from dict
                    if 'query' in sq:
                        cleaned_queries.append(sq['query'])
                    else:
                        # Try to get first value from dict
                        values = list(sq.values())
                        if values and isinstance(values[0], str):
                            cleaned_queries.append(values[0])
            
            # Include original query as well
            all_queries = [query] + cleaned_queries
            
            print(f"🔍 Query Decomposition (Intent: {intent}):")
            print(f"   Original: {query}")
            print(f"   Generated {len(cleaned_queries)} sub-queries:")
            for i, sq in enumerate(cleaned_queries, 1):
                print(f"      {i}. {sq}")
            
            return all_queries[:8]  # Max 8 queries (original + 7 sub-queries)
            
        except Exception as e:
            print(f"⚠️  Failed to generate sub-queries: {e}")
            # Fallback: return just the original query
            return [query]


class ContextWindowRetriever:
    """
    Retrieves context windows (±60 seconds) around relevant messages.
    
    PROBLEM: Single messages lack context
    SOLUTION: Retrieve surrounding messages within ±60s window
    
    Example:
        Relevant message at 12:00:00
        Window: All messages from 11:59:00 to 12:01:00
    """
    
    def __init__(self, collection):
        """
        Args:
            collection: ChromaDB collection to query
        """
        self.collection = collection
        self.window_seconds = 60  # ±60 second window
    
    def get_context_window(
        self,
        anchor_timestamp: float,
        node_id: str,
        exclude_buffer_cutoff: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all messages within ±60s of anchor timestamp.
        
        Args:
            anchor_timestamp: Timestamp of relevant message
            node_id: Conversation node to search within
            exclude_buffer_cutoff: Don't retrieve messages newer than this
        
        Returns:
            List of messages in time window, sorted by timestamp
        """
        try:
            # Calculate window bounds
            window_start = anchor_timestamp - self.window_seconds
            window_end = anchor_timestamp + self.window_seconds
            
            # Apply buffer cutoff if provided
            if exclude_buffer_cutoff:
                window_end = min(window_end, exclude_buffer_cutoff)
            
            # Build where clause
            where_clause = {
                "$and": [
                    {"archived": {"$eq": True}},
                    {"node_id": {"$eq": node_id}},
                    {"timestamp": {"$gte": window_start}},
                    {"timestamp": {"$lte": window_end}}
                ]
            }
            
            # Get all messages in window
            results = self.collection.get(
                where=where_clause,
                include=["documents", "metadatas"]
            )
            
            # Parse and sort by timestamp
            messages = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    messages.append({
                        "text": doc,
                        "metadata": metadata,
                        "timestamp": metadata.get("timestamp", 0)
                    })
            
            # Sort chronologically
            messages.sort(key=lambda x: x["timestamp"])
            
            return messages
            
        except Exception as e:
            print(f"⚠️  Failed to get context window: {e}")
            return []


class GlobalVectorIndex:
    """
    Vector storage for archived conversation messages.
    
    ENHANCED WITH:
    - Multi-query decomposition for better retrieval
    - Context window retrieval (±60s around relevant messages)
    - Backward compatible retrieve_relevant() method
    
    Messages are automatically added when evicted from LocalBuffer (10+ messages old).
    Enables semantic search across long conversation history.
    """
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        """
        Initialize vector index with ChromaDB.
        
        🧹 RESEARCH MODE: Clears all old data on startup for clean testing.
        Every server restart starts with fresh, empty vector storage.
        
        Args:
            persist_dir: Directory to persist vector database
        """
        # 🧹 CLEAR OLD DATA - Fresh start for each test run
        import shutil
        if Path(persist_dir).exists():
            try:
                # Try to cleanly delete using ChromaDB's reset first
                temp_client = chromadb.PersistentClient(
                    path=persist_dir,
                    settings=Settings(anonymized_telemetry=False, allow_reset=True)
                )
                temp_client.reset()
                del temp_client
                print(f"🧹 Cleared old vector data (research mode - fresh start)")
            except Exception as e:
                # If that fails, force delete the directory
                try:
                    shutil.rmtree(persist_dir)
                    print(f"🧹 Force-cleared old vector data: {e}")
                except Exception as e2:
                    print(f"⚠️  Warning: Could not fully clear old data: {e2}")
        
        # Create fresh directory
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 🔥 Use better embedding model for improved semantic search
        # Options: 'all-mpnet-base-v2' (best), 'multi-qa-mpnet-base-dot-v1' (QA-optimized), 'all-MiniLM-L12-v2' (faster)
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-mpnet-base-v2"  # 🔥 UPGRADE: Much better than default all-MiniLM-L6-v2
        )
        
        # Create new collection (always fresh) with better embeddings
        self.collection = self.client.create_collection(
            name="conversation_archive",
            metadata={"description": "Archived conversation messages beyond buffer"},
            embedding_function=embedding_function
        )
        print(f"✅ Created fresh vector collection with all-mpnet-base-v2 embeddings (0 messages)")
        
        self.persist_dir = persist_dir
        
        # Initialize enhanced retrieval components
        try:
            self.query_decomposer = QueryDecomposer()
            self.context_retriever = ContextWindowRetriever(self.collection)
            # Note: Cross-encoder re-ranking disabled - embedding similarity (all-mpnet-base-v2) works better for conversational context
            print(f"✅ Initialized multi-query decomposition + context windows")
        except Exception as e:
            print(f"⚠️  Failed to initialize enhanced retrieval: {e}")
            self.query_decomposer = None
            self.context_retriever = None
    
    def _print_all_indexed_messages(self):
        """
        Print all messages currently in the vector database.
        Also logs to file for detailed analysis.
        """
        try:
            total_count = self.collection.count()
            
            # Get ALL messages from collection
            results = self.collection.get(
                limit=total_count if total_count > 0 else 1,
                include=["documents", "metadatas"]
            )
            
            # Group by conversation node for better readability
            messages_by_node = {}
            if results and results['documents']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    node_id = metadata.get('node_id', 'unknown')
                    
                    if node_id not in messages_by_node:
                        messages_by_node[node_id] = []
                    
                    messages_by_node[node_id].append({
                        'text': doc,
                        'metadata': metadata,
                        'index': i
                    })
                
                # Sort by timestamp within each conversation
                for node_id in messages_by_node:
                    messages_by_node[node_id].sort(key=lambda x: x['metadata'].get('timestamp', 0))
            
            # Log to BOTH loggers
            logger_overwrite = get_debug_logger(append_mode=False)  # For user viewing
            logger_append = get_debug_logger(append_mode=True)      # For full debugging
            
            for logger in [logger_overwrite, logger_append]:
                logger.log_vector_store(messages_by_node, total_count)
            
            # Print brief summary to terminal
            print(f"📚 Vector store: {total_count} messages across {len(messages_by_node)} conversations (logged to file)")
            
        except Exception as e:
            print(f"⚠️  Failed to log indexed messages: {e}")
            import traceback
            traceback.print_exc()
            
            print(f"\n{'='*80}")
            print(f"✅ Total: {total_count} messages indexed across {len(messages_by_node)} conversations")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"⚠️  Failed to print indexed messages: {e}")
            import traceback
            traceback.print_exc()
    
    def index_message(self, node_id: str, message: str, metadata: Dict[str, Any]):
        """
        Archive a message to vector storage.
        Called automatically when message is evicted from LocalBuffer.
        
        Args:
            node_id: ID of conversation node
            message: Message text to archive
            metadata: Additional metadata (role, timestamp, conversation_title, etc.)
        """
        try:
            # Create unique ID for this message
            message_id = f"{node_id}_{metadata.get('timestamp', time.time())}"
            
            # Prepare metadata for ChromaDB
            chroma_metadata = {
                "node_id": node_id,
                "role": metadata.get("role", "unknown"),
                "timestamp": float(metadata.get("timestamp", time.time())),
                "conversation_title": metadata.get("conversation_title", "Untitled"),  # Store title
                "archived": True  # Mark as archived (not in buffer)
            }
            
            # Add to collection
            self.collection.add(
                documents=[message],
                metadatas=[chroma_metadata],
                ids=[message_id]
            )
            
            print(f"📦 Archived message: {message[:60]}... (ID: {message_id})")
            
            # 🔍 DEBUG: Print ALL indexed messages after each addition
            self._print_all_indexed_messages()
            
        except Exception as e:
            print(f"⚠️  Failed to archive message: {e}")
    
    def update_conversation_title(self, node_id: str, new_title: str) -> int:
        """
        Update conversation_title metadata for all messages of a given node_id.
        
        This is called when auto_generate_title_if_needed() changes a title from "New Chat"
        to an AI-generated title. It ensures all previously-indexed messages get the new title.
        
        Args:
            node_id: The conversation node ID to update
            new_title: The new title to set
            
        Returns:
            Number of messages updated
        """
        try:
            # Get all messages for this node_id
            results = self.collection.get(
                where={"node_id": node_id},
                include=["metadatas", "documents", "embeddings"]
            )
            
            if not results or not results['ids']:
                print(f"⚠️  No messages found for node_id: {node_id}")
                return 0
            
            # Update metadata for each message
            # ChromaDB doesn't support in-place metadata updates, so we delete and re-add
            updated_count = 0
            for i, msg_id in enumerate(results['ids']):
                metadata = results['metadatas'][i]
                metadata['conversation_title'] = new_title
                
                # Delete old message
                self.collection.delete(ids=[msg_id])
                
                # Re-add with updated metadata
                self.collection.add(
                    ids=[msg_id],
                    documents=[results['documents'][i]],
                    metadatas=[metadata],
                    embeddings=[results['embeddings'][i]]
                )
                updated_count += 1
            
            print(f"✅ Updated {updated_count} messages with new title: '{new_title}'")
            
            # Refresh logs to show updated titles
            self._print_all_indexed_messages()
            
            return updated_count
            
        except Exception as e:
            print(f"⚠️  Failed to update conversation title: {e}")
            return 0
    
    def retrieve_with_multi_query(
        self,
        query: str,
        top_k: int = 5,
        node_id: Optional[str] = None,
        exclude_buffer_cutoff: Optional[float] = None,
        use_context_windows: bool = True
    ) -> List[Dict[str, Any]]:
        """
        ENHANCED RETRIEVAL with multi-query decomposition + context windows.
        
        This is the NEW method that should be used for all retrieval.
        It dramatically improves recall by:
        1. Decomposing vague queries into 5-7 specific sub-queries
        2. Retrieving context windows (±60s) around relevant messages
        3. Merging and deduplicating results
        
        Args:
            query: Search query (user's message or question)
            top_k: Number of final results to return
            node_id: Limit search to specific conversation node
            exclude_buffer_cutoff: Don't retrieve messages newer than this timestamp
            use_context_windows: Whether to retrieve ±60s context around hits
        
        Returns:
            List of retrieved messages with metadata and relevance scores
        """
        try:
            # Check if collection is empty
            if self.collection.count() == 0:
                print("ℹ️  Vector index is empty - no archived messages yet")
                return []
            
            print(f"\n{'='*60}")
            print(f"🔍 ENHANCED RETRIEVAL: {query}")
            print(f"{'='*60}")
            
            # PHASE 1: Multi-Query Decomposition
            if self.query_decomposer:
                intent = self.query_decomposer.classify_intent(query)
                sub_queries = self.query_decomposer.generate_sub_queries(query, intent)
                # GUARANTEE: Original query is always first (even if decomposer fails)
                if not sub_queries or sub_queries[0] != query:
                    sub_queries = [query] + (sub_queries or [])
            else:
                print("⚠️  Query decomposer not available, using single query")
                sub_queries = [query]
            
            # PHASE 2: Retrieve with each sub-query
            all_results = []
            seen_message_ids: Set[str] = set()
            seen_texts: Set[str] = set()  # 🆕 Track seen message texts for deduplication
            sub_query_results = {}  # Track results per sub-query for logging
            
            for i, sub_query in enumerate(sub_queries, 1):
                print(f"\n📋 Sub-query {i}/{len(sub_queries)}: {sub_query}")
                
                sub_query_results[sub_query] = []  # Initialize results list for this sub-query
                
                # Build where clause
                where_clause = None
                if node_id:
                    where_clause = {
                        "$and": [
                            {"archived": {"$eq": True}},
                            {"node_id": {"$eq": node_id}}
                        ]
                    }
                else:
                    where_clause = {"archived": {"$eq": True}}
                
                # Query collection - fetch more results to ensure we get enough unique ones
                results = self.collection.query(
                    query_texts=[sub_query],
                    n_results=min(20, self.collection.count()),  # Fetch 20 to find 5 unique
                    where=where_clause if where_clause else None
                )
                
                # Parse results and deduplicate by text
                unique_count = 0  # Track unique results for this sub-query
                if results and results['documents'] and results['documents'][0]:
                    for j, doc in enumerate(results['documents'][0]):
                        # Stop if we already have 5 unique results for this sub-query
                        if unique_count >= 5:
                            break
                        
                        metadata = results['metadatas'][0][j] if results['metadatas'] else {}
                        distance = results['distances'][0][j] if results['distances'] else 1.0
                        score = max(0.0, 1.0 - distance)  # Fix: Clamp negative scores to 0
                        
                        # Filter by timestamp if cutoff provided
                        if exclude_buffer_cutoff:
                            msg_timestamp = metadata.get('timestamp', 0)
                            if msg_timestamp >= exclude_buffer_cutoff:
                                print(f"   ⏭️  Skipped (in buffer): {doc[:80]}...")
                                continue  # Skip messages still in buffer
                        
                        # 🆕 Check for duplicate text (normalize for comparison)
                        normalized_text = doc.strip().lower()
                        if normalized_text in seen_texts:
                            print(f"   ⏭️  Skipped duplicate: {doc[:80]}...")
                            continue  # Skip duplicate, search for next unique
                        
                        # Create unique ID for deduplication by message ID
                        msg_id = f"{metadata.get('node_id', '')}_{metadata.get('timestamp', 0)}"
                        
                        if msg_id not in seen_message_ids:
                            # First time seeing this text and message ID - keep it
                            seen_message_ids.add(msg_id)
                            seen_texts.add(normalized_text)  # 🆕 Track text
                            unique_count += 1  # Increment unique counter
                            
                            all_results.append({
                                "text": doc,
                                "score": score,
                                "metadata": metadata,
                                "sub_query": sub_query,  # Track which sub-query found this
                                "message_id": msg_id
                            })
                            
                            # ✅ Store result for this sub-query AFTER deduplication (for logging)
                            sub_query_results[sub_query].append({
                                "text": doc,
                                "score": score,
                                "metadata": metadata
                            })
                            
                            print(f"   ✓ Found: {doc[:80]}... (score: {score:.3f})")
                else:
                    print(f"   ✗ No results found")
            
            print(f"\n📊 Total unique messages from {len(sub_queries)} sub-queries: {len(all_results)}")
            
            # PHASE 3: Context Window Expansion
            if use_context_windows and self.context_retriever and node_id:
                print(f"\n🔍 PHASE 3: Context Window Expansion (±60s)")
                
                expanded_results = []
                context_message_ids: Set[str] = set()
                
                # For each result, get context window
                for result in all_results:
                    anchor_timestamp = result['metadata'].get('timestamp', 0)
                    
                    # Get context window
                    context_messages = self.context_retriever.get_context_window(
                        anchor_timestamp=anchor_timestamp,
                        node_id=node_id,
                        exclude_buffer_cutoff=exclude_buffer_cutoff
                    )
                    
                    # Add context messages
                    for ctx_msg in context_messages:
                        ctx_id = f"{ctx_msg['metadata'].get('node_id', '')}_{ctx_msg['metadata'].get('timestamp', 0)}"
                        
                        if ctx_id not in context_message_ids:
                            context_message_ids.add(ctx_id)
                            
                            # Check if this is the anchor message (already in results)
                            if ctx_id == result['message_id']:
                                expanded_results.append(result)  # Keep original score
                            else:
                                # Add as context with lower score
                                expanded_results.append({
                                    "text": ctx_msg['text'],
                                    "score": result['score'] * 0.8,  # Slightly lower score for context
                                    "metadata": ctx_msg['metadata'],
                                    "is_context": True,  # Mark as context
                                    "message_id": ctx_id
                                })
                
                print(f"   ✓ Expanded to {len(expanded_results)} messages (including context)")
                all_results = expanded_results
            
            # PHASE 4: Re-Ranking
            print(f"\n{'='*80}")
            print(f"🎯 RE-RANKING ({len(all_results)} candidates)")
            print(f"{'='*80}")
            
            # Sort by embedding similarity score (all-mpnet-base-v2 is quite good!)
            # Higher scores are better (similarity scores), recent timestamps as tiebreaker
            all_results.sort(key=lambda x: (x['score'], x['metadata'].get('timestamp', 0)), reverse=True)
            final_results = all_results[:top_k]
            
            print(f"✅ Selected top {len(final_results)} results by embedding similarity")
            
            # Log retrieval to BOTH loggers
            logger_overwrite = get_debug_logger(append_mode=False)  # For user viewing
            logger_append = get_debug_logger(append_mode=True)      # For full debugging
            
            for logger in [logger_overwrite, logger_append]:
                logger.log_retrieval(
                    query=query,
                    intent=intent if self.query_decomposer else "unknown",
                    sub_queries=sub_queries,
                    sub_query_results=sub_query_results,  # Pass detailed sub-query results
                    retrieved_results=final_results,
                    node_id=node_id
                )
            
            # Print brief summary to terminal
            print(f"✅ Retrieved {len(final_results)} results (logged to file)")
            
            return final_results
            
        except Exception as e:
            print(f"⚠️  Failed to retrieve with multi-query: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def retrieve_relevant(
        self,
        query: str,
        top_k: int = 3,
        node_id: Optional[str] = None,
        exclude_buffer_cutoff: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant archived messages (not in current buffer).
        
        Args:
            query: Search query (user's message or question)
            top_k: Number of results to retrieve
            node_id: Limit search to specific conversation node
            exclude_buffer_cutoff: Don't retrieve messages newer than this timestamp
                                   (i.e., messages still in buffer)
        
        Returns:
            List of retrieved messages with metadata and relevance scores
        """
        try:
            # Check if collection is empty
            if self.collection.count() == 0:
                print("ℹ️  Vector index is empty - no archived messages yet")
                return []
            
            # Build where clause for filtering (ChromaDB requires $and operator for multiple conditions)
            where_clause = None
            if node_id:
                # Use $and operator for multiple conditions
                where_clause = {
                    "$and": [
                        {"archived": {"$eq": True}},
                        {"node_id": {"$eq": node_id}}
                    ]
                }
            else:
                # Single condition
                where_clause = {"archived": {"$eq": True}}
            
            # 🔍 DEBUG: Show collection stats
            total_in_db = self.collection.count()
            print(f"📊 Database has {total_in_db} total messages")
            if exclude_buffer_cutoff:
                print(f"   Excluding messages newer than timestamp: {exclude_buffer_cutoff}")
            
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k * 2, self.collection.count()),  # Get more to filter
                where=where_clause if where_clause else None
            )
            
            # Parse results
            retrieved = []
            excluded_by_cutoff = 0
            if results and results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    
                    # Filter by timestamp if cutoff provided
                    if exclude_buffer_cutoff:
                        msg_timestamp = metadata.get('timestamp', 0)
                        if msg_timestamp >= exclude_buffer_cutoff:
                            excluded_by_cutoff += 1
                            continue  # Skip messages still in buffer
                    
                    retrieved.append({
                        "text": doc,
                        "score": 1.0 - distance,  # Convert distance to similarity score
                        "metadata": metadata
                    })
            
            # � DEBUG: Show filtering stats
            if exclude_buffer_cutoff and excluded_by_cutoff > 0:
                print(f"   Excluded {excluded_by_cutoff} messages (still in buffer)")
            
            # �📊 DEBUG: Show BEFORE re-ranking
            if retrieved:
                print(f"\n📋 BEFORE re-ranking ({len(retrieved)} messages):")
                for i, item in enumerate(retrieved[:5], 1):  # Show first 5
                    msg_preview = item['text'][:200] + ('...' if len(item['text']) > 200 else '')
                    score = item['score']
                    role = item['metadata'].get('role', 'unknown')
                    print(f"   {i}. [Score: {score:.3f}] [{role.upper()}]")
                    print(f"       {msg_preview}")
            
            # Return top_k results
            retrieved = retrieved[:top_k]
            
            # 📊 DEBUG: Show AFTER filtering to top_k WITH FULL TEXT
            if retrieved:
                print(f"\n✅ AFTER filtering to top_{top_k} ({len(retrieved)} messages):")
                print(f"{'='*60}")
                for i, item in enumerate(retrieved, 1):
                    full_text = item['text']  # FULL message text, no truncation
                    score = item['score']
                    role = item['metadata'].get('role', 'unknown')
                    print(f"\n{i}. [Score: {score:.3f}] [{role.upper()}]")
                    print(f"   FULL MESSAGE:")
                    print(f"   {full_text}")
                    print(f"   {'-'*60}")
                print(f"{'='*60}")
            
            return retrieved
            
        except Exception as e:
            print(f"⚠️  Failed to retrieve from vector index: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about archived messages"""
        try:
            total_count = self.collection.count()
            
            # Get all metadata to analyze
            if total_count > 0:
                results = self.collection.get(
                    limit=total_count,
                    include=["metadatas"]
                )
                
                # Count by node
                nodes = {}
                for metadata in results['metadatas']:
                    node_id = metadata.get('node_id', 'unknown')
                    nodes[node_id] = nodes.get(node_id, 0) + 1
                
                return {
                    "total_archived_messages": total_count,
                    "unique_conversations": len(nodes),
                    "messages_per_conversation": nodes,
                    "persist_dir": self.persist_dir
                }
            
            return {
                "total_archived_messages": 0,
                "unique_conversations": 0,
                "messages_per_conversation": {},
                "persist_dir": self.persist_dir
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def clear(self):
        """Clear all archived messages (for testing)"""
        try:
            self.client.delete_collection("conversation_archive")
            self.collection = self.client.create_collection(
                name="conversation_archive",
                metadata={"description": "Archived conversation messages beyond buffer"}
            )
            print("🗑️  Cleared vector index")
        except Exception as e:
            print(f"⚠️  Failed to clear vector index: {e}")


# Testing









if __name__ == "__main__":
    print("🧪 Testing Enhanced GlobalVectorIndex with Multi-Query Decomposition...")
    
    # Create index
    index = GlobalVectorIndex(persist_dir="./test_chroma_db")
    
    # Test 1: Index realistic conversation messages
    print("\n--- Test 1: Indexing realistic conversation messages ---")
    
    base_time = time.time() - 200
    
    # User introduction messages
    index.index_message(
        node_id="test_node_1",
        message="Hi! My name is Moon and I'm a student at MIT.",
        metadata={"role": "user", "timestamp": base_time}
    )
    
    index.index_message(
        node_id="test_node_1",
        message="That's a great introduction, Moon! What are you studying at MIT?",
        metadata={"role": "assistant", "timestamp": base_time + 5}
    )
    
    index.index_message(
        node_id="test_node_1",
        message="I'm studying computer science and my favorite programming language is Python.",
        metadata={"role": "user", "timestamp": base_time + 10}
    )
    
    # Discussion about Python (programming)
    index.index_message(
        node_id="test_node_1",
        message="Python is a high-level programming language known for its simplicity.",
        metadata={"role": "assistant", "timestamp": base_time + 60}
    )
    
    index.index_message(
        node_id="test_node_1",
        message="Decorators in Python allow modifying function behavior without changing the function itself.",
        metadata={"role": "assistant", "timestamp": base_time + 70}
    )
    
    # Unrelated: Python snakes
    index.index_message(
        node_id="test_node_1",
        message="What is the capital of France?",
        metadata={"role": "user", "timestamp": base_time + 120}
    )
    
    index.index_message(
        node_id="test_node_1",
        message="The capital of France is Paris, a beautiful city known for the Eiffel Tower.",
        metadata={"role": "assistant", "timestamp": base_time + 125}
    )
    
    # More user preferences
    index.index_message(
        node_id="test_node_1",
        message="I love machine learning and I'm working on a project using PyTorch.",
        metadata={"role": "user", "timestamp": base_time + 150}
    )
    
    print(f"✅ Indexed {index.collection.count()} messages")
    
    # Test 2: OLD METHOD - Single query retrieval (should fail for vague queries)
    print("\n\n" + "="*80)
    print("--- Test 2: OLD METHOD - retrieve_relevant() with vague query ---")
    print("="*80)
    
    results_old = index.retrieve_relevant(
        query="user identity information",  # Vague query
        top_k=3,
        node_id="test_node_1"
    )
    
    print(f"\n🔍 Query: 'user identity information' (VAGUE)")
    print(f"📊 Results from OLD method: {len(results_old)}")
    for i, result in enumerate(results_old, 1):
        print(f"\n{i}. [Score: {result['score']:.3f}] {result['text'][:100]}...")
    
    # Test 3: NEW METHOD - Multi-query retrieval (should succeed)
    print("\n\n" + "="*80)
    print("--- Test 3: NEW METHOD - retrieve_with_multi_query() with vague query ---")
    print("="*80)
    
    results_new = index.retrieve_with_multi_query(
        query="user identity information",  # Same vague query
        top_k=5,
        node_id="test_node_1",
        use_context_windows=True
    )
    
    print(f"\n📊 Comparison:")
    print(f"   OLD method: {len(results_old)} results")
    print(f"   NEW method: {len(results_new)} results")
    
    # Test 4: NEW METHOD with "who am i" query
    print("\n\n" + "="*80)
    print("--- Test 4: NEW METHOD - 'who am i?' query ---")
    print("="*80)
    
    results_who = index.retrieve_with_multi_query(
        query="who am i?",
        top_k=5,
        node_id="test_node_1",
        use_context_windows=True
    )
    
    # Verify we get user introduction
    has_introduction = any("My name is Moon" in r['text'] for r in results_who)
    has_preferences = any("favorite programming language" in r['text'] or "machine learning" in r['text'] for r in results_who)
    
    print(f"\n✅ Verification:")
    print(f"   Found introduction: {has_introduction}")
    print(f"   Found preferences: {has_preferences}")
    
    # Test 5: Get statistics
    print("\n\n--- Test 5: Statistics ---")
    stats = index.get_stats()
    print(f"Total archived: {stats['total_archived_messages']}")
    print(f"Unique conversations: {stats['unique_conversations']}")
    
    # Success check
    print("\n\n" + "="*80)
    if has_introduction and has_preferences:
        print("✅ ALL TESTS PASSED! Multi-query decomposition working correctly.")
        print("   The system can now find user identity information with vague queries.")
    else:
        print("⚠️  TESTS FAILED! Multi-query decomposition needs debugging.")
    print("="*80)
    
    # Clean up
    index.clear()
    print("\n🗑️  Cleaned up test data")

