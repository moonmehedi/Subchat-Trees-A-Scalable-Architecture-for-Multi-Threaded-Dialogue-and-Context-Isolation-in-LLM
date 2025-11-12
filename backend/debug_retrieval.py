"""
Debug script to check what messages are actually retrieved from vector index.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.vector_index import GlobalVectorIndex

# Initialize vector index
vector_index = GlobalVectorIndex()

# Test retrieval for "what did we discuss about python"
print("="*80)
print("🔍 Testing retrieval for: 'what did we discuss about python'")
print("="*80)

results = vector_index.retrieve_relevant(
    query="what did we discuss about python",
    top_k=5,
    node_id=None,  # Search globally
    exclude_buffer_cutoff=None  # Get everything
)

print(f"\n📊 Retrieved {len(results)} messages:\n")

for i, result in enumerate(results, 1):
    text = result['text']
    role = result['metadata'].get('role', 'unknown')
    score = result['score']
    node_id = result['metadata'].get('node_id', 'unknown')
    
    print(f"{i}. [{role.upper()}] (score: {score:.3f}) (node: {node_id[:8]}...)")
    print(f"   Text: {text}")
    print(f"   Length: {len(text)} characters")
    print()

print("="*80)
print("🔍 Now checking ChromaDB collection directly...")
print("="*80)

# Get collection info
count = vector_index.collection.count()
print(f"📦 Total messages in collection: {count}")

# Get a few sample documents directly
sample = vector_index.collection.peek(5)
if sample and sample['documents']:
    print(f"\n📋 Sample documents from ChromaDB:\n")
    for i, doc in enumerate(sample['documents'], 1):
        metadata = sample['metadatas'][i-1] if sample['metadatas'] else {}
        print(f"{i}. [{metadata.get('role', 'unknown').upper()}]")
        print(f"   Text: {doc[:200]}{'...' if len(doc) > 200 else ''}")
        print(f"   Full length: {len(doc)} characters")
        print()
