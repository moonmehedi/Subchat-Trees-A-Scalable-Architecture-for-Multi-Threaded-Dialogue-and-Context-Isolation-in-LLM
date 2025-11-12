#!/usr/bin/env python3
"""
Pre-download ChromaDB embedding model to cache.
Run this once to avoid slow download during actual usage.
"""

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

print("🔽 Downloading embedding model to cache...")
print("This is a ONE-TIME setup. Future runs will be instant.\n")

# Method 1: Download via sentence-transformers (faster server)
print("📥 Downloading via sentence-transformers...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Sentence-transformers model downloaded\n")

# Method 2: Trigger ChromaDB's ONNX download
print("📥 Downloading ChromaDB ONNX model...")
client = chromadb.Client()
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

# Trigger embedding to force download
test_embedding = embedding_fn(["test"])
print("✅ ChromaDB ONNX model downloaded\n")

print("🎉 All models cached! Future runs will be instant.")
print(f"Cache location: ~/.cache/chroma/")
