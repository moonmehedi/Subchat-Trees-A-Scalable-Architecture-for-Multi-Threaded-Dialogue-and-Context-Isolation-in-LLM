"""
Global Vector Index for long-term conversation memory.
Auto-archives messages when they're evicted from LocalBuffer.

ENHANCED WITH:
- Multi-query decomposition for better retrieval
- Turn-based context window retrieval (±2 turns around relevant messages)
- Rank-then-expand pipeline: re-rank anchors first, expand winners with context
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
    Decomposes a query into multiple specific sub-queries for better semantic retrieval.

    PROBLEM: A single vague query often fails to match relevant archived messages.
    SOLUTION: Prompt the LLM to generate 5-7 diverse sub-queries that capture
              different phrasings, synonyms, and aspects of the original query.
              No intent classification — the LLM understands the query directly.

    Example:
        Query: "what did I tell you about myself?"
        Sub-queries: ["my name is", "I am a", "I work as", "I study", "I live in",
                      "my background", "personal introduction"]
    """

    def __init__(self, vllm_client=None):
        """Initialize with vLLM (preferred) or Groq LLM for sub-query generation"""
        self.vllm_client = vllm_client
        self.last_usage = None
        self.client = None  # Groq client (fallback)

        if self.vllm_client:
            self.model = "vllm-local"
            print("✅ QueryDecomposer using vLLM backend")
        else:
            # Fallback to Groq
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable not set")
            self.client = Groq(api_key=api_key)
            self.model = settings.model_base_groq if hasattr(settings, 'model_base_groq') else settings.model_base
            print("✅ QueryDecomposer using Groq backend")

    def get_last_usage(self):
        """Return token usage from the last generate_sub_queries() call."""
        return self.last_usage

    def generate_sub_queries(self, query: str) -> List[str]:
        """
        Generate 5-7 diverse sub-queries directly from the user query.

        The LLM is given the query as-is and asked to produce varied search strings
        that cover synonyms, related concepts, and different phrasings. No intent
        classification step — the LLM handles understanding on its own.
        """
        prompt = (
            f'Given this search query: "{query}"\n\n'
            "Generate 5-7 SHORT, SPECIFIC search strings that capture different aspects, "
            "synonyms, and related concepts of the query. Think about how the relevant "
            "information might actually be phrased in a conversation.\n\n"
            'Return ONLY a JSON array of strings: ["q1", "q2", ...]\n\n'
            "Examples:\n"
            '  Query: "what is my job?"\n'
            '  Output: ["I work as", "my job is", "I am employed", "my profession", "I am a developer", "my career", "I work at"]\n\n'
            '  Query: "where do I live?"\n'
            '  Output: ["I live in", "I am from", "my hometown is", "I am based in", "I reside in", "my city is", "I moved to"]\n\n'
            '  Query: "what are my hobbies?"\n'
            '  Output: ["I enjoy", "I like to", "in my free time", "my hobby is", "I love", "I spend time", "I am passionate about"]\n\n'
            f'Now generate for: "{query}"'
        )

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a Query Expansion Specialist embedded inside a Retrieval-Augmented Generation (RAG) pipeline. "
                        "Your sole purpose is to help the retrieval system find the most relevant archived conversation messages. "
                        "When a user sends a query, you receive it and must generate multiple diverse search strings that cover "
                        "different phrasings, synonyms, and related concepts — because the archived messages may not contain "
                        "the exact words from the user's query, but may express the same idea differently. "
                        "Your output directly determines what context the main LLM receives, so generating high-quality, "
                        "varied search strings is critical. "
                        "Output ONLY a JSON string array. No objects, no explanation, no extra text."
                    )
                },
                {"role": "user", "content": prompt}
            ]

            if self.vllm_client:
                result = self.vllm_client.generate(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=150
                ).strip()
                self.last_usage = self.vllm_client.get_last_usage()
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=150
                )
                result = response.choices[0].message.content.strip()
                if hasattr(response, 'usage') and response.usage:
                    self.last_usage = {
                        "prompt_tokens": response.usage.prompt_tokens or 0,
                        "completion_tokens": response.usage.completion_tokens or 0,
                        "total_tokens": response.usage.total_tokens or 0
                    }

            # Parse JSON array
            sub_queries = json.loads(result)

            if not isinstance(sub_queries, list):
                raise ValueError("Expected JSON array")

            # Normalise: accept plain strings or dicts with a 'query' key
            cleaned_queries = []
            for sq in sub_queries:
                if isinstance(sq, str):
                    cleaned_queries.append(sq)
                elif isinstance(sq, dict):
                    val = sq.get('query') or (list(sq.values())[0] if sq else None)
                    if isinstance(val, str):
                        cleaned_queries.append(val)

            # Always include the original query first
            all_queries = [query] + cleaned_queries

            print(f"🔍 Query Decomposition:")
            print(f"   Original: {query}")
            print(f"   Generated {len(cleaned_queries)} sub-queries:")
            for i, sq in enumerate(cleaned_queries, 1):
                print(f"      {i}. {sq}")

            return all_queries[:8]  # original + up to 7 sub-queries

        except Exception as e:
            print(f"⚠️  Failed to generate sub-queries: {e}")
            return [query]


class ContextWindowRetriever:
    """
    Retrieves context windows (±k turns) around relevant messages.
    
    PROBLEM: Single messages lack conversational context
    SOLUTION: Retrieve surrounding messages by turn number (±2 turns)
    
    Turn-based windows are more reliable than temporal windows because
    user response times vary unpredictably (seconds to minutes), while
    turn ordering is deterministic and preserves conversational structure.
    
    Example:
        Anchor message at turn 15
        Window: All messages from turn 13 to turn 17
    """
    
    def __init__(self, collection):
        """
        Args:
            collection: ChromaDB collection to query
        """
        self.collection = collection
        self.window_turns = 2  # ±2 turns around anchor
    
    def get_context_window(
        self,
        anchor_turn_number: int,
        node_id: str,
        exclude_buffer_cutoff: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all messages within ±2 turns of anchor turn number.
        
        Args:
            anchor_turn_number: Turn number of the anchor message
            node_id: Conversation node to search within
            exclude_buffer_cutoff: Don't retrieve messages newer than this timestamp
        
        Returns:
            List of messages in turn window, sorted by turn_number
        """
        try:
            if anchor_turn_number <= 0:
                print(f"⚠️  Invalid turn number: {anchor_turn_number}")
                return []
            
            # Calculate turn window bounds
            turn_start = max(1, anchor_turn_number - self.window_turns)
            turn_end = anchor_turn_number + self.window_turns
            
            # Build where clause using turn_number range
            where_conditions = [
                {"archived": {"$eq": True}},
                {"node_id": {"$eq": node_id}},
                {"turn_number": {"$gte": turn_start}},
                {"turn_number": {"$lte": turn_end}}
            ]
            
            # Optionally exclude messages still in buffer (by timestamp cutoff)
            if exclude_buffer_cutoff:
                where_conditions.append({"timestamp": {"$lt": exclude_buffer_cutoff}})
            
            where_clause = {"$and": where_conditions}
            
            # Get all messages in turn window
            results = self.collection.get(
                where=where_clause,
                include=["documents", "metadatas"]
            )
            
            # Parse and sort by turn_number (deterministic ordering)
            messages = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    messages.append({
                        "text": doc,
                        "metadata": metadata,
                        "turn_number": metadata.get("turn_number", 0),
                        "timestamp": metadata.get("timestamp", 0)
                    })
            
            # Sort by turn number (chronological within the conversation)
            messages.sort(key=lambda x: x["turn_number"])
            
            return messages
            
        except Exception as e:
            print(f"⚠️  Failed to get context window: {e}")
            return []


class GlobalVectorIndex:
    """
    Vector storage for archived conversation messages.
    
    ENHANCED WITH:
    - Multi-query decomposition for better retrieval
    - Turn-based context window retrieval (±2 turns around relevant messages)
    - Re-rank-then-expand pipeline: select top-k anchors first, then expand
    - Backward compatible retrieve_relevant() method
    
    Messages are automatically added when evicted from LocalBuffer (10+ messages old).
    Enables semantic search across long conversation history.
    """
    
    def __init__(self, persist_dir: str = None):
        """
        Initialize vector index with ChromaDB.
        
        🧹 RESEARCH MODE: Clears all old data on startup for clean testing.
        Every server restart starts with fresh, empty vector storage.
        
        Args:
            persist_dir: Directory to persist vector database. 
                         Auto-detects Kaggle environment and uses /kaggle/working/chroma_db
        """
        # Auto-detect Kaggle environment for writable path
        if persist_dir is None:
            if os.path.exists("/kaggle"):
                persist_dir = "/kaggle/working/chroma_db"
                print(f"🔧 Kaggle detected: Using writable path {persist_dir}")
            else:
                persist_dir = "./chroma_db"
        
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
        self.last_retrieval_debug = None  # Populated by retrieve_with_multi_query; read by simple_llm for unified RAG_PIPELINE log
        
        # Initialize enhanced retrieval components
        # Pass vLLM client to QueryDecomposer so it can run locally without Groq
        _vllm_client = None
        if settings.llm_backend == "vllm":
            try:
                from .vllm_client import vllm_client as _vc
                if _vc.is_available():
                    _vllm_client = _vc
            except ImportError:
                pass
        
        try:
            self.query_decomposer = QueryDecomposer(vllm_client=_vllm_client)
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
                "turn_number": int(metadata.get("turn_number", 0)),  # Turn-based ordering within node
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
        ENHANCED RETRIEVAL with multi-query decomposition + turn-based context windows.
        
        Pipeline:
        1. Decompose query into sub-queries (multi-query decomposition)
        2. Retrieve candidates per sub-query, deduplicate across all
        3. Re-rank the deduplicated anchors by cosine similarity → select top-k
        4. For each top-k winner, expand ±2 turns to form coherent context blocks
        
        Args:
            query: Search query (user's message or question)
            top_k: Number of anchor messages to return
            node_id: Limit search to specific conversation node
            exclude_buffer_cutoff: Don't retrieve messages newer than this timestamp
            use_context_windows: Whether to retrieve ±2 turn context around hits
        
        Returns:
            List of retrieved messages with metadata, relevance scores, and
            coherent context blocks (neighbours grouped with their anchors)
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
                sub_queries = self.query_decomposer.generate_sub_queries(query)
                # GUARANTEE: Original query is always first (even if decomposer fails)
                if not sub_queries or sub_queries[0] != query:
                    sub_queries = [query] + (sub_queries or [])
            else:
                print("⚠️  Query decomposer not available, using single query")
                sub_queries = [query]
            
            # PHASE 2: Retrieve with each sub-query (deduplicated across all)
            all_results = []
            seen_message_ids: Set[str] = set()
            seen_texts: Set[str] = set()
            sub_query_results = {}
            
            for i, sub_query in enumerate(sub_queries, 1):
                print(f"\n📋 Sub-query {i}/{len(sub_queries)}: {sub_query}")
                
                sub_query_results[sub_query] = []
                
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
                unique_count = 0
                if results and results['documents'] and results['documents'][0]:
                    for j, doc in enumerate(results['documents'][0]):
                        # Stop if we already have 5 unique results for this sub-query
                        if unique_count >= 5:
                            break
                        
                        metadata = results['metadatas'][0][j] if results['metadatas'] else {}
                        distance = results['distances'][0][j] if results['distances'] else 1.0
                        score = max(0.0, 1.0 - distance)  # Clamp negative scores to 0
                        
                        # Filter by timestamp if cutoff provided
                        if exclude_buffer_cutoff:
                            msg_timestamp = metadata.get('timestamp', 0)
                            if msg_timestamp >= exclude_buffer_cutoff:
                                print(f"   ⏭️  Skipped (in buffer): {doc[:80]}...")
                                continue
                        
                        # Check for duplicate text (normalize for comparison)
                        normalized_text = doc.strip().lower()
                        if normalized_text in seen_texts:
                            print(f"   ⏭️  Skipped duplicate: {doc[:80]}...")
                            continue
                        
                        # Create unique ID for deduplication by message ID
                        msg_id = f"{metadata.get('node_id', '')}_{metadata.get('timestamp', 0)}"
                        
                        if msg_id not in seen_message_ids:
                            seen_message_ids.add(msg_id)
                            seen_texts.add(normalized_text)
                            unique_count += 1
                            
                            all_results.append({
                                "text": doc,
                                "score": score,
                                "metadata": metadata,
                                "sub_query": sub_query,
                                "message_id": msg_id
                            })
                            
                            sub_query_results[sub_query].append({
                                "text": doc,
                                "score": score,
                                "metadata": metadata
                            })
                            
                            print(f"   ✓ Found: {doc[:80]}... (score: {score:.3f}, turn: {metadata.get('turn_number', '?')})")
                else:
                    print(f"   ✗ No results found")
            
            print(f"\n📊 Total unique anchor messages from {len(sub_queries)} sub-queries: {len(all_results)}")
            
            # PHASE 3: Re-Rank ANCHORS ONLY → select top-k
            print(f"\n{'='*80}")
            print(f"🎯 PHASE 3: RE-RANKING ANCHORS ({len(all_results)} candidates → top {top_k})")
            print(f"{'='*80}")
            
            # Sort anchors by cosine similarity score, timestamp as tiebreaker
            all_results.sort(key=lambda x: (x['score'], x['metadata'].get('timestamp', 0)), reverse=True)
            top_anchors = all_results[:top_k]
            
            for i, anchor in enumerate(top_anchors, 1):
                turn = anchor['metadata'].get('turn_number', '?')
                print(f"   #{i} [turn {turn}] score={anchor['score']:.3f}: {anchor['text'][:80]}...")
            
            print(f"✅ Selected top {len(top_anchors)} anchors by embedding similarity")
            
            # PHASE 4: Turn-Based Context Window Expansion (±2 turns per anchor)
            final_results = []
            
            if use_context_windows and self.context_retriever and node_id:
                print(f"\n🔍 PHASE 4: Turn-Based Context Expansion (±{self.context_retriever.window_turns} turns per anchor)")
                
                seen_context_ids: Set[str] = set()
                
                for anchor in top_anchors:
                    anchor_turn = anchor['metadata'].get('turn_number', 0)
                    anchor_node = anchor['metadata'].get('node_id', node_id)
                    
                    if anchor_turn <= 0:
                        # Fallback: no turn_number available, return anchor only
                        print(f"   ⚠️  No turn_number for anchor, returning without context")
                        final_results.append(anchor)
                        continue
                    
                    # Get ±2 turn context window around this anchor
                    context_messages = self.context_retriever.get_context_window(
                        anchor_turn_number=anchor_turn,
                        node_id=anchor_node,
                        exclude_buffer_cutoff=exclude_buffer_cutoff
                    )
                    
                    # Build coherent block: anchor + its neighbours
                    block_messages = []
                    for ctx_msg in context_messages:
                        ctx_id = f"{ctx_msg['metadata'].get('node_id', '')}_{ctx_msg['metadata'].get('timestamp', 0)}"
                        ctx_turn = ctx_msg.get('turn_number', ctx_msg['metadata'].get('turn_number', 0))
                        
                        if ctx_id not in seen_context_ids:
                            seen_context_ids.add(ctx_id)
                            
                            is_anchor = (ctx_turn == anchor_turn)
                            block_messages.append({
                                "text": ctx_msg['text'],
                                "score": anchor['score'] if is_anchor else anchor['score'] * 0.8,
                                "metadata": ctx_msg['metadata'],
                                "is_context": not is_anchor,
                                "is_anchor": is_anchor,
                                "anchor_turn": anchor_turn,
                                "message_id": ctx_id
                            })
                    
                    # If context window returned nothing (edge case), at least keep the anchor
                    if not block_messages:
                        block_messages.append({
                            **anchor,
                            "is_context": False,
                            "is_anchor": True,
                            "anchor_turn": anchor_turn
                        })
                    
                    print(f"   ✓ Anchor turn {anchor_turn}: expanded to {len(block_messages)} messages (turns {block_messages[0]['metadata'].get('turn_number', '?')}–{block_messages[-1]['metadata'].get('turn_number', '?')})")
                    final_results.extend(block_messages)
                
                print(f"   ✅ Total: {len(final_results)} messages in {len(top_anchors)} coherent blocks")
            else:
                # No context expansion — just return the top anchors
                final_results = top_anchors
            
            # Store retrieval details — will be read by simple_llm.py to write unified RAG_PIPELINE.log
            self.last_retrieval_debug = {
                'sub_queries': sub_queries,
                'sub_query_results': sub_query_results,
                'final_results': final_results,
            }
            
            print(f"✅ Retrieved {len(final_results)} results in coherent blocks")
            
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

