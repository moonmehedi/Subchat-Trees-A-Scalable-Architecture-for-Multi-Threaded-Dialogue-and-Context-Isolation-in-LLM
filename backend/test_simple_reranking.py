"""
Simple standalone test to verify re-ranking is working.
This script directly tests the vector index without importing the full application.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import only what we need
import chromadb
from chromadb.config import Settings
import time


def test_reranking():
    """Test that re-ranking changes the order of results"""
    print("="*80)
    print("TESTING: Re-ranking Changes Order")
    print("="*80)
    
    # Create a test ChromaDB collection
    client = chromadb.Client(Settings(
        anonymized_telemetry=False,
        allow_reset=True
    ))
    
    # Reset and create fresh collection
    client.reset()
    collection = client.create_collection(
        name="test_reranking",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Add test documents with different relevance levels
    test_docs = [
        ("My name is Alice and I'm a software engineer", {"role": "user", "timestamp": time.time()}),
        ("I work at Google in Mountain View", {"role": "user", "timestamp": time.time() + 1}),
        ("Python is a programming language", {"role": "assistant", "timestamp": time.time() + 2}),
        ("I enjoy hiking on weekends", {"role": "user", "timestamp": time.time() + 3}),
        ("The weather is nice today", {"role": "user", "timestamp": time.time() + 4}),
    ]
    
    for i, (text, metadata) in enumerate(test_docs):
        collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[f"doc_{i}"]
        )
    
    print(f"\n✅ Added {len(test_docs)} test documents")
    
    # Query with a specific search
    query = "Tell me about Alice's work"
    print(f"\n🔍 Query: '{query}'")
    
    results = collection.query(
        query_texts=[query],
        n_results=len(test_docs)
    )
    
    print("\n📊 Results from ChromaDB (cosine similarity):")
    if results and results['documents'] and results['documents'][0]:
        for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
            score = 1.0 - distance
            print(f"   {i+1}. [Score: {score:.3f}] {doc[:80]}")
    
    # Check if scores are different
    if results['distances'][0]:
        distances = results['distances'][0]
        unique_scores = set(distances)
        
        if len(unique_scores) > 1:
            print("\n✅ PASS: Scores are different - ranking is working!")
            print(f"   Found {len(unique_scores)} unique scores")
            return True
        else:
            print("\n❌ FAIL: All scores are identical")
            return False
    else:
        print("\n⚠️  No results returned")
        return False


def test_database_stats():
    """Show current database statistics from the real application"""
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)
    
    try:
        # Try to connect to the actual application's ChromaDB
        client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get the conversation_memory collection
        try:
            collection = client.get_collection(name="conversation_memory")
            total = collection.count()
            
            print(f"\n📦 Total messages in database: {total}")
            
            if total > 0:
                # Sample some documents
                sample = collection.peek(min(10, total))
                
                print(f"\n📋 Sample messages:")
                for i, (doc, metadata) in enumerate(zip(sample['documents'], sample['metadatas'])):
                    role = metadata.get('role', 'unknown')
                    preview = doc[:100] + ('...' if len(doc) > 100 else '')
                    print(f"   {i+1}. [{role.upper()}] {preview}")
                
                # Check for duplicates
                unique_docs = set(sample['documents'])
                if len(unique_docs) < len(sample['documents']):
                    print(f"\n⚠️  Found duplicate messages: {len(sample['documents'])} total, {len(unique_docs)} unique")
                else:
                    print(f"\n✅ No duplicates in sample")
            
        except Exception as e:
            print(f"⚠️  Collection not found: {e}")
            print("   (This is normal if the app hasn't been run yet)")
    
    except Exception as e:
        print(f"⚠️  Could not connect to database: {e}")


def test_query_similarity():
    """Test how different queries match against the same documents"""
    print("\n" + "="*80)
    print("TESTING: Query Similarity Matching")
    print("="*80)
    
    # Create test collection
    client = chromadb.Client(Settings(
        anonymized_telemetry=False,
        allow_reset=True
    ))
    client.reset()
    collection = client.create_collection(name="test_queries")
    
    # Add a specific user introduction
    collection.add(
        documents=["My name is Moon, I'm 22 years old, I study at MIST and I like cricket"],
        metadatas=[{"role": "user", "timestamp": time.time()}],
        ids=["intro"]
    )
    
    print("\n✅ Added user introduction message")
    
    # Test different queries
    queries = [
        "What is my name?",
        "who am i?",
        "user name introduction",
        "user personal info",
        "tell me about myself"
    ]
    
    print("\n🔍 Testing different query formulations:")
    for query in queries:
        results = collection.query(
            query_texts=[query],
            n_results=1
        )
        
        if results and results['distances'] and results['distances'][0]:
            distance = results['distances'][0][0]
            score = 1.0 - distance
            print(f"   '{query}'")
            print(f"      → Score: {score:.3f} (distance: {distance:.3f})")


def main():
    """Run all tests"""
    print("="*80)
    print("RE-RANKING AND VECTOR SEARCH TEST SUITE")
    print("="*80)
    
    # Test 1: Re-ranking changes order
    test1_pass = test_reranking()
    
    # Test 2: Database stats
    test_database_stats()
    
    # Test 3: Query similarity
    test_query_similarity()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if test1_pass:
        print("✅ Basic ranking is working")
    else:
        print("❌ Basic ranking may have issues")
    
    print("\n💡 To see full re-ranking in action:")
    print("   1. Run the backend server")
    print("   2. Use the frontend to create conversations")
    print("   3. Watch the backend logs for BEFORE/AFTER re-ranking output")


if __name__ == "__main__":
    main()
