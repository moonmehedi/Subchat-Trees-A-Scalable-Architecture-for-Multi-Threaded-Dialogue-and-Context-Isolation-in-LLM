"""
Re-ranking module for improving retrieval quality.
Uses cross-encoder for accurate relevance scoring.
"""

from typing import List, Dict, Any
import os


class SimpleReranker:
    """
    Simple re-ranker using cross-encoder scoring.
    Falls back to original scores if re-ranking fails.
    """
    
    def __init__(self):
        """Initialize re-ranker"""
        self.model = None
        self.enabled = True
        
        try:
            # Try to import sentence-transformers for re-ranking
            from sentence_transformers import CrossEncoder
            
            # Use a lightweight cross-encoder model for re-ranking
            # This model is specifically trained for semantic similarity
            model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
            
            print(f"🔄 Loading re-ranker model: {model_name}")
            self.model = CrossEncoder(model_name)
            print(f"✅ Re-ranker loaded successfully")
            
        except ImportError:
            print("⚠️  sentence-transformers not installed - re-ranking disabled")
            print("   Install with: pip install sentence-transformers")
            self.enabled = False
        except Exception as e:
            print(f"⚠️  Failed to load re-ranker: {e}")
            self.enabled = False
    
    def rerank(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Re-rank documents based on query relevance using cross-encoder.
        
        Args:
            query: Search query
            documents: List of retrieved documents with 'text' and 'score' keys
            top_k: Number of top results to return (None = return all)
            
        Returns:
            Re-ranked documents with updated scores
        """
        if not documents:
            return documents
        
        # If re-ranking is disabled, just return original results
        if not self.enabled or not self.model:
            return documents[:top_k] if top_k else documents
        
        try:
            # Prepare query-document pairs for cross-encoder
            pairs = [[query, doc['text']] for doc in documents]
            
            # Get cross-encoder scores (more accurate than embedding similarity)
            print(f"🔄 Re-ranking {len(documents)} documents...")
            scores = self.model.predict(pairs)
            
            # Update documents with new scores
            for i, doc in enumerate(documents):
                doc['original_score'] = doc.get('score', 0.0)
                doc['score'] = float(scores[i])
            
            # Sort by new scores (descending)
            reranked = sorted(documents, key=lambda x: x['score'], reverse=True)
            
            # Show re-ranking changes
            print(f"✅ Re-ranking complete:")
            for i, doc in enumerate(reranked[:3], 1):
                orig = doc.get('original_score', 0.0)
                new = doc['score']
                change = "↑" if new > orig else "↓" if new < orig else "→"
                msg_preview = doc['text'][:50] + ('...' if len(doc['text']) > 50 else '')
                print(f"   {i}. {change} [Score: {orig:.3f} → {new:.3f}] {msg_preview}")
            
            return reranked[:top_k] if top_k else reranked
            
        except Exception as e:
            print(f"⚠️  Re-ranking failed: {e} - using original scores")
            return documents[:top_k] if top_k else documents


class MultiQueryRetriever:
    """
    Breaks down complex queries into multiple sub-queries for comprehensive retrieval.
    Example: "Tell me about myself" → ["name", "college", "interests", "background"]
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize multi-query retriever.
        
        Args:
            llm_client: Optional LLM client for query decomposition
        """
        self.llm_client = llm_client
    
    def decompose_query(self, query: str) -> List[str]:
        """
        Decompose a complex query into multiple sub-queries.
        
        For now, uses simple heuristics. Can be enhanced with LLM in future.
        
        Args:
            query: Original complex query
            
        Returns:
            List of sub-queries
        """
        query_lower = query.lower()
        
        # Pattern 1: "Tell me about myself" / "What do you know about me"
        if any(phrase in query_lower for phrase in [
            "about me", "about myself", "know about me", "tell me what you know"
        ]):
            return [
                "user name introduction",
                "user college university education",
                "user interests hobbies favorite",
                "user background personal information",
                "user age location details"
            ]
        
        # Pattern 2: Multiple questions in one
        # "What is my favorite game, what college I am in"
        if "," in query or " and " in query:
            # Split by comma or "and"
            parts = query.replace(" and ", ",").split(",")
            return [part.strip() for part in parts if part.strip()]
        
        # Default: return original query
        return [query]
    
    def retrieve_with_decomposition(
        self,
        query: str,
        vector_index,
        top_k_per_query: int = 3,
        final_top_k: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve using query decomposition and de-duplication.
        
        Args:
            query: Original query
            vector_index: GlobalVectorIndex instance
            top_k_per_query: Results per sub-query
            final_top_k: Final number of results to return
            **kwargs: Additional arguments for retrieve_relevant
            
        Returns:
            Deduplicated and ranked results
        """
        # Decompose query
        sub_queries = self.decompose_query(query)
        
        if len(sub_queries) > 1:
            print(f"🔍 Multi-query retrieval: Breaking down into {len(sub_queries)} queries")
            for i, sq in enumerate(sub_queries, 1):
                print(f"   {i}. {sq}")
        
        # Retrieve for each sub-query
        all_results = []
        seen_ids = set()
        
        for sub_query in sub_queries:
            results = vector_index.retrieve_relevant(
                query=sub_query,
                top_k=top_k_per_query,
                **kwargs
            )
            
            # De-duplicate by message ID
            for result in results:
                msg_id = result['metadata'].get('message_id', result['text'])
                if msg_id not in seen_ids:
                    seen_ids.add(msg_id)
                    all_results.append(result)
        
        # Sort by score and return top results
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        return all_results[:final_top_k]


# Singleton instances
_reranker_instance = None
_multi_query_instance = None


def get_reranker() -> SimpleReranker:
    """Get singleton re-ranker instance"""
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = SimpleReranker()
    return _reranker_instance


def get_multi_query_retriever() -> MultiQueryRetriever:
    """Get singleton multi-query retriever instance"""
    global _multi_query_instance
    if _multi_query_instance is None:
        _multi_query_instance = MultiQueryRetriever()
    return _multi_query_instance
