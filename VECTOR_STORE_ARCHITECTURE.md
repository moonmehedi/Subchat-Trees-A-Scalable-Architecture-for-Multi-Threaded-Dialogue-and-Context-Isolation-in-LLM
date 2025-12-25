# Vector Store Architecture - RAG (Retrieval-Augmented Generation)

## 🔍 Overview

The system uses **ChromaDB** as a vector database for long-term memory and cross-conversation search. Messages are automatically embedded and stored when they're evicted from the local buffer.

---

## 📂 Key Files

### 1. **`src/services/vector_index.py`** (Main Vector Store Logic)
   - **Line 410-450**: `index_message()` - Embeds and stores messages in ChromaDB
   - **Line 300-350**: ChromaDB collection initialization with sentence-transformers embeddings
   - **Line 150-200**: `QueryDecomposer` - Breaks vague queries into specific sub-queries
   - **Line 200-250**: `ContextWindowRetriever` - Gets ±60 second context windows

### 2. **`src/models/tree.py`** (Buffer with Auto-Archive)
   - **Line 29-50**: `add_message()` - Adds message to buffer AND indexes to vector store
   - **Line 44-46**: Immediate indexing when message is added (if `auto_archive=True`)

### 3. **`src/services/simple_llm.py`** (LLM Client with RAG)
   - **Line 14**: `__init__(enable_vector_index=False)` - RAG is **DISABLED by default**
   - **Line 66-74**: Vector index initialization (only if enabled)
   - **Line 285**: Warning when vector index not enabled

---

## 🔄 How Messages Are Embedded & Stored

### **Flow:**

```
User sends message
     ↓
TreeNode.buffer.add_message(role, content)  [Line 43 in tree.py]
     ↓
     ├─> Add to local buffer (recent N messages)
     └─> Auto-index to ChromaDB vector store [Line 44-46]
              ↓
         vector_index.index_message(node_id, message, metadata)  [Line 410 in vector_index.py]
              ↓
         ChromaDB embeds using sentence-transformers
              ↓
         Stored with metadata:
         - node_id (which conversation)
         - role (user/assistant)
         - timestamp
         - conversation_title
         - archived: True
```

### **Code Location: `src/models/tree.py` Line 43-50**

```python
def add_message(self, role: str, content: str, auto_archive: bool = True):
    """Add message with timestamp and immediate indexing to vector DB."""
    
    # 1. INDEX IMMEDIATELY to vector DB (so it's searchable across conversations)
    if auto_archive and self.vector_index and self.node_id:
        try:
            self.vector_index.index_message(
                node_id=self.node_id,
                message=f"{role}: {content}",
                metadata={
                    "role": role,
                    "timestamp": time.time(),
                    "conversation_title": self.node_title
                }
            )
        except Exception as e:
            print(f"⚠️  Failed to index message: {e}")
    
    # 2. Add to local buffer
    self.messages.append({...})
```

---

## 🧠 Embedding Model

**Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Location**: `src/services/vector_index.py` Line ~300
- **Dimensions**: 384
- **Speed**: Fast (~50ms per message)
- **Quality**: Good for semantic similarity

```python
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

self.collection = self.client.create_collection(
    name="subchat_trees_archive",
    embedding_function=embedding_function,
    metadata={"hnsw:space": "cosine"}
)
```

---

## 🔍 Query Enhancement (Multi-Query Decomposition)

### **Problem**: Vague queries like "who am i?" fail with semantic search

### **Solution**: Decompose into 5-7 specific sub-queries using LLM

**Code Location: `src/services/vector_index.py` Line 150-200**

**Example:**
```
User Query: "who am i?"
Intent: identity

Sub-queries generated:
1. "my name is"
2. "I am a student"
3. "I work as"
4. "I study"
5. "about myself"
6. "my background"

→ Search with ALL queries, merge results
```

---

## ⏰ Context Window Retrieval (±60 seconds)

### **Problem**: Single messages lack context

### **Solution**: Retrieve all messages within ±60s window

**Code Location: `src/services/vector_index.py` Line 200-250**

**Example:**
```
Found relevant message at 12:00:00
↓
Retrieve ALL messages from 11:59:00 to 12:01:00
↓
Provides full conversation context
```

---

## 🗃️ ChromaDB Storage Location

**Default Path**: `backend/chroma_db/`

**Structure:**
```
chroma_db/
├── chroma.sqlite3              # Metadata database
└── <collection_id>/            # Embeddings & vectors
    ├── data_level0.bin
    └── header.bin
```

**To clear ChromaDB:**
```bash
rm -rf backend/chroma_db/
```

---

## ⚙️ RAG Status in Different Modes

### **1. Serverless Test Runner (Kaggle)**
- ❌ **RAG DISABLED** by default
- Why? Faster testing, focus on context isolation
- `SimpleLLMClient(enable_vector_index=False)`  [Line 45 in kaggle_serverless_runner.py]

### **2. HTTP Server Mode**
- ✅ **RAG CAN BE ENABLED** via API parameter
- `POST /api/conversations/{node_id}/messages`
- Body: `{"message": "...", "disable_rag": false}`

### **3. Simple Test Scripts**
- ❌ **RAG DISABLED** by default
- Can be enabled: `SimpleLLMClient(enable_vector_index=True)`

---

## 📊 Logs & Debugging

### **Vector Store Logs:**
`backend/dataset/logs/serverless_tests/VECTOR_STORE.log`

**Shows:**
- All indexed messages
- Grouped by conversation
- Timestamps & metadata

### **Enable RAG Logging:**
```python
from src.utils.debug_logger import get_debug_logger
logger = get_debug_logger()
logger.log_vector_store(messages_by_node, total_count)
```

---

## 🚀 How to Enable RAG

### **In Serverless Runner:**
```python
# In kaggle_serverless_runner.py, Line 45
self.llm_client = SimpleLLMClient(enable_vector_index=True)  # ← Change to True
```

### **In HTTP Server:**
```python
# Already enabled via API parameter
curl -X POST http://localhost:8000/api/conversations/{node_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Who am I?", "disable_rag": false}'
```

---

## 📈 Performance Characteristics

| Metric | Value |
|--------|-------|
| Embedding Speed | ~50ms per message |
| Query Latency | ~100-300ms (with multi-query) |
| Storage | ~1KB per message |
| Max Messages | Unlimited (ChromaDB scales) |
| Context Window | ±60 seconds |
| Sub-queries | 5-7 per vague query |

---

## 🔧 Configuration

### **Environment Variables:**
```bash
# Groq API for query decomposition
GROQ_API_KEY=your_key_here

# Model for sub-query generation
MODEL_BASE=llama-3.3-70b-versatile
```

### **Settings in `src/cores/config.py`:**
```python
model_base = "llama-3.3-70b-versatile"  # For query decomposition
chroma_db_path = "./chroma_db"           # Vector store location
```

---

## 🎯 Summary

✅ **Automatic Embedding**: Messages are embedded when added to buffer
✅ **Smart Retrieval**: Multi-query decomposition for vague queries
✅ **Context-Aware**: ±60s window retrieval for conversation context
✅ **Persistent**: ChromaDB stores all archived messages
✅ **Scalable**: Handles unlimited conversations and messages
✅ **Flexible**: Can be enabled/disabled per mode

**Current Status in Kaggle Tests**: ❌ DISABLED (focus on context isolation without RAG complexity)
