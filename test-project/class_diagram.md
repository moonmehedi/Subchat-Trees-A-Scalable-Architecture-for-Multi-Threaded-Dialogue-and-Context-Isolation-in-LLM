# Hierarchical Chat System - Class Diagram

This diagram shows the relationships between all classes in the hierarchical chat system.

```mermaid
classDiagram
    class LocalBuffer {
        -deque~Dict~ turns
        -int max_turns
        +__init__(max_turns: int)
        +add_message(role: str, text: str)
        +get_recent(n: Optional~int~) List~Dict~
        +clear(n: int)
    }

    class TreeNode {
        -str node_id
        -str title
        -TreeNode parent
        -List~TreeNode~ children
        -LocalBuffer buffer
        -Optional~str~ summary
        -Dict~str, Any~ metadata
        +__init__(node_id: Optional~str~, title: str, parent: Optional~TreeNode~)
        +add_child(child_node: TreeNode)
        +get_path() List~str~
    }

    class ChatGraphManager {
        -Dict~str, TreeNode~ node_map
        -Optional~str~ active_node_id
        +__init__()
        +create_node(title: str, parent_id: Optional~str~) TreeNode
        +switch_node(node_id: str) TreeNode
        +get_active_node() TreeNode
        +get_node(node_id: str) TreeNode
    }

    class Forest {
        -Dict~str, TreeNode~ trees_map
        -Optional~str~ active_tree_id
        +__init__()
        +create_tree(title: str) TreeNode
        +switch_tree(tree_id: str) TreeNode
        +get_active_tree() TreeNode
    }

    class GlobalVectorIndex {
        -OpenAIEmbeddings embeddings
        -Chroma store
        +__init__(persist_dir: Optional~str~)
        +index_docs(docs: List~Dict~)
        +query(query_text: str, top_k: int, filter_meta: Optional~Dict~)
        +as_retriever(k: int, fetch_k: int, filter_meta: Optional~Dict~)
        +delete_collection()
    }

    class LLMClient {
        -ChatOpenAI model
        +__init__(model_name: str, temperature: float)
        +generate_response(messages: List~Dict~, system_prompt: Optional~str~) str
    }

    class ChatAssembler {
        -ChatGraphManager chat_manager
        -GlobalVectorIndex vector_index
        -LLMClient llm_client
        +__init__(persist_dir: Optional~str~)
        +process_user_message(user_text: str) str
        +create_subchat(title: str, parent_id: Optional~str~) TreeNode
        +switch_to_node(node_id: str) TreeNode
    }

    %% Relationships
    TreeNode ||--o{ TreeNode : "parent-child"
    TreeNode ||--|| LocalBuffer : "has"
    
    ChatGraphManager ||--o{ TreeNode : "manages"
    Forest ||--o{ TreeNode : "manages root trees"
    
    ChatAssembler ||--|| ChatGraphManager : "uses"
    ChatAssembler ||--|| GlobalVectorIndex : "uses"
    ChatAssembler ||--|| LLMClient : "uses"
    
    %% External dependencies (shown for completeness)
    GlobalVectorIndex ..> OpenAIEmbeddings : "uses"
    GlobalVectorIndex ..> Chroma : "uses"
    LLMClient ..> ChatOpenAI : "uses"

    %% Notes
    note for TreeNode "Each node has its own\nmessage buffer and can\nhave multiple children"
    note for ChatAssembler "Main orchestrator that\ncoordinates all components\nfor chat processing"
    note for GlobalVectorIndex "Provides semantic search\nacross all chat history\nusing vector embeddings"
```

## Key Relationships Explained:

### 1. **TreeNode Structure**
- Each `TreeNode` contains a `LocalBuffer` for storing recent messages
- TreeNodes form a hierarchical tree structure with parent-child relationships
- Each node has a unique ID, title, and can store metadata

### 2. **Management Layer**
- `ChatGraphManager`: Manages individual nodes within a single conversation tree
- `Forest`: Manages multiple independent conversation trees (multiple root nodes)

### 3. **Core Services**
- `GlobalVectorIndex`: Provides semantic search across all chat history using embeddings
- `LLMClient`: Handles communication with the language model (GPT)

### 4. **Orchestration**
- `ChatAssembler`: The main coordinator that brings everything together
- It uses ChatGraphManager for node management
- It uses GlobalVectorIndex for retrieving relevant context
- It uses LLMClient for generating responses

## Data Flow:
1. User sends a message to `ChatAssembler`
2. `ChatAssembler` gets the active node from `ChatGraphManager`
3. Message is added to the node's `LocalBuffer`
4. `GlobalVectorIndex` retrieves relevant context from other conversations
5. `LLMClient` generates a response using local + retrieved context
6. Response is added to the buffer and indexed in the vector store

This architecture allows for:
- **Hierarchical conversations** (branching discussions)
- **Context preservation** (local buffers per node)
- **Cross-conversation memory** (global vector index)
- **Flexible navigation** (switching between nodes/trees)
