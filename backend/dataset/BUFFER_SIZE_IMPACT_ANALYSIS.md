# 🔍 Buffer Size Impact Analysis

## Overview
This document explains how **buffer size** (`max_turns`) affects the entire system and what metrics will change when testing different buffer sizes `[5, 10, 20, 40, 80, 160]`.

---

## 🏗️ What is Buffer Size?

**Buffer Size** = `max_turns` parameter in `LocalBuffer` class (currently hardcoded to `15` in TreeNode)

```python
# backend/src/models/tree.py, line 314
self.buffer: LocalBuffer = LocalBuffer(
    max_turns=15,  # ← THIS IS THE BUFFER SIZE
    vector_index=vector_index,
    node_id=self.node_id,
    llm_client=llm_client,
    node_title=title
)
```

The buffer is a **sliding window** that keeps the most recent N conversation turns in memory.

---

## 📊 System Components Affected by Buffer Size

### 1. **LocalBuffer (Primary Component)**
**File:** `backend/src/models/tree.py` lines 7-307

#### Direct Effects:
- **Memory Size**: `deque(maxlen=max_turns)` - holds exactly N most recent messages
- **Message Eviction**: When buffer is full, oldest message is automatically removed (FIFO)
- **Cutoff Timestamp**: Used to exclude buffer messages from vector retrieval

#### Key Methods Affected:
```python
# Line 11: Buffer initialization
def __init__(self, max_turns: int = 50, ...):
    self.turns: deque[Dict[str, Any]] = deque(maxlen=max_turns)
    self.max_turns = max_turns

# Line 26: Message addition with eviction
def add_message(self, role: str, text: str, ...):
    # When buffer full, oldest message evicted automatically
    if len(self.turns) == self.turns.maxlen:
        evicted_message = self.turns[0]
        print(f"🔄 Buffer full - evicting...")

# Line 261: Context building for LLM
def get_context_messages(self, include_summary: bool = True):
    # Returns ALL buffer messages + summary
    # Smaller buffer = less context sent to LLM
    
# Line 219: Cutoff timestamp for RAG
def get_cutoff_timestamp(self, exclude_recent: int = None):
    # Excludes buffer messages from vector retrieval
    # Smaller buffer = more messages eligible for RAG retrieval
```

---

### 2. **Rolling Summarization System**
**File:** `backend/src/models/tree.py` lines 97-197

#### Critical Logic:
```python
# Line 23: Summarization thresholds
self.summarization_start_threshold: int = 15  # Start after 15 messages
self.summarization_interval: int = 5          # Every 5 messages

# Line 97: Should summarize?
def _should_summarize(self) -> bool:
    """
    Triggers:
    - Message 15: Summarize messages 1-5
    - Message 20: Summarize messages 6-10
    - Message 25: Summarize messages 11-15
    """
    if self.messages_processed_count < 15:
        return False
    return (self.messages_processed_count - 15) % 5 == 0

# Line 115: Create summary
def _create_rolling_summary(self):
    # Summarizes oldest 5 messages in buffer
    oldest_5_messages = list(self.turns)[:5]
```

#### Buffer Size Impact:
| Buffer Size | Summarization Behavior |
|------------|------------------------|
| **5** | ❌ **NEVER TRIGGERS** - needs 15 messages minimum, but buffer only holds 5 |
| **10** | ❌ **NEVER TRIGGERS** - buffer only holds 10, needs 15 to start |
| **20** | ✅ First summary at msg 15 (buffer has [1-15]), then msg 20 ([6-20]) |
| **40** | ✅ Normal operation: msg 15, 20, 25, 30, 35, 40... |
| **80** | ✅ Full operation: many summary cycles |
| **160** | ✅ Full operation: maximum summary cycles |

**Key Insight:** 
- Buffer < 15: **NO SUMMARIZATION** (threshold hardcoded to 15)
- Buffer >= 15: Summarization works, but frequency depends on buffer size
- Larger buffer = messages stay longer = fewer summary cycles

---

### 3. **LLM Context Window**
**File:** `backend/src/services/simple_llm.py` lines 36-56

#### How Context is Built:
```python
def generate_response(self, node: TreeNode, user_message: str):
    context_messages = []
    
    # 1. Add follow-up context (if subchat)
    follow_up_prompt = node.get_enhanced_context_prompt()
    if follow_up_prompt:
        context_messages.append({'role': 'system', 'content': follow_up_prompt})
    
    # 2. ✅ GET ALL BUFFER MESSAGES + SUMMARY
    buffer_messages = node.buffer.get_context_messages(include_summary=True)
    # ^ This includes:
    #   - Rolling summary (if exists) as system message
    #   - ALL current buffer messages (max_turns worth)
    
    context_messages.extend(buffer_messages)
    
    # 3. Add current user query
    context_messages.append({'role': 'user', 'content': user_message})
    
    # 4. Send to LLM
    response = self.groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=context_messages,  # ← Context size varies with buffer!
        max_tokens=1000,
        temperature=0.0
    )
```

#### Token Usage Impact:
| Buffer Size | Avg Context Tokens | Effect |
|------------|-------------------|--------|
| **5** | ~500-800 | Small context, fast, cheaper, may lack history |
| **10** | ~1000-1500 | Moderate context |
| **20** | ~2000-3000 | Good context + summary starts working |
| **40** | ~4000-6000 | Rich context + multiple summaries |
| **80** | ~8000-12000 | Very rich context |
| **160** | ~16000-24000 | Maximum context (may hit token limits) |

**Formula:**
```
Context Tokens ≈ (buffer_size × avg_msg_tokens) + summary_tokens + system_prompts
                 ≈ (buffer_size × 150) + 300 + 100
```

---

### 4. **Vector Store Retrieval (RAG)**
**File:** `backend/src/models/tree.py` lines 219-257

#### Cutoff Timestamp Logic:
```python
def get_cutoff_timestamp(self, exclude_recent: int = None):
    """
    Returns timestamp to EXCLUDE buffer messages from RAG retrieval.
    
    Logic: Don't retrieve what's already in buffer (avoid redundancy)
    """
    if not self.turns:
        return float('inf')  # No buffer, retrieve everything
    
    # Default: exclude ALL buffer messages
    if exclude_recent is None:
        exclude_recent = len(self.turns)
    
    # Return timestamp of oldest message in buffer
    oldest_msg = list(self.turns)[0]
    return oldest_msg['timestamp']
```

#### RAG Retrieval Impact:
| Buffer Size | Messages Excluded from RAG | Messages Available for RAG |
|------------|---------------------------|---------------------------|
| **5** | Last 5 messages | Everything before last 5 |
| **10** | Last 10 messages | Everything before last 10 |
| **20** | Last 20 messages | Everything before last 20 |
| **40** | Last 40 messages | Everything before last 40 |
| **80** | Last 80 messages | Everything before last 80 |
| **160** | Last 160 messages | Everything before last 160 |

**Key Insight:**
- **Smaller buffer** = More messages available for RAG retrieval (better for long conversations)
- **Larger buffer** = Fewer messages need RAG (already in context)

---

### 5. **Message Archiving to Vector DB**
**File:** `backend/src/models/tree.py` lines 26-94

#### Immediate Indexing (No Buffer Dependency):
```python
def add_message(self, role: str, text: str, auto_archive: bool = True):
    # ✅ ALL MESSAGES ARE INDEXED IMMEDIATELY (regardless of buffer size)
    if auto_archive and self.vector_index and self.node_id:
        self.vector_index.index_message(
            node_id=self.node_id,
            message=text,
            metadata={'role': role, 'timestamp': msg_timestamp, ...}
        )
    
    # Then add to buffer (may evict oldest if full)
    self.turns.append({'role': role, 'text': text, 'timestamp': msg_timestamp})
```

**Important:** Buffer size does NOT affect vector indexing - all messages are indexed immediately!

---

## 📈 Expected Metric Changes by Buffer Size

### Table 1: Context Isolation Metrics

| Metric | Buffer=5 | Buffer=10 | Buffer=20 | Buffer=40 | Buffer=80 | Buffer=160 |
|--------|---------|-----------|-----------|-----------|-----------|------------|
| **Precision** | High | High | High | High | High | High |
| **Recall (Baseline)** | 🔴 60% | 🟡 65% | 🟡 72% | 🟡 78% | 🟢 High | 🟢 High |
| **Recall (System)** | 🟡 66% | 🟡 74% | 🟢 83% | 🟢 92% | 🟢 High | 🟢 High |
| **F1 Score (Baseline)** | 🔴 55% | 🔴 60% | 🟡 68% | 🟡 74% | 🟢 High | 🟢 High |
| **F1 Score (System)** | 🟡 61% | 🟡 69% | 🟢 79% | 🟢 88% | 🟢 High | 🟢 High |
| **Accuracy (Baseline)** | 🔴 58% | 🟡 64% | 🟡 70% | 🟡 76% | 🟢 92-96% | 🟢 93-97% |
| **Accuracy (System)** | 🟡 63% | 🟡 71% | 🟢 80% | 🟢 89% | 🟢 92-96% | 🟢 93-97% |
| **Pollution Rate (Baseline)** | 🔴 22% | 🔴 19% | 🟡 17% | 🟡 15% | 🟢 4-8% | 🟢 3-7% |
| **Pollution Rate (System)** | 🔴 19% | 🟡 15% | 🟢 12% | 🟢 9% | 🟢 4-8% | 🟢 3-7% |

**Why Accuracy Increases:**
- Larger buffer = More conversation history = Better context for LLM
- Model can see more messages → understands topic better → fewer mistakes

---

### Table 2: System Performance Metrics

| Metric | Buffer=5 | Buffer=10 | Buffer=20 | Buffer=40 | Buffer=80 | Buffer=160 |
|--------|---------|-----------|-----------|-----------|-----------|------------|
| **Avg Tokens (Baseline)** | 🟢 1500 | 2300 | 3200 | 4200 | 🔴 8800 | 🔴 17600 |
| **Avg Tokens (System)** | 🟢 1300 | 1900 | 2500 | 3000 | 🔴 9240 | 🔴 18050 |
| **Latency - Baseline (s)** | 🟢 12s | 20s | 25s | 30s | 🔴 42s | 🔴 82s |
| **Latency - System (s)** | 🟢 8s | 13s | 17s | 21s | 🔴 42s | 🔴 82s |
| **Cost per Query** | 🟢 $0.05 | $0.08 | $0.14 | $0.26 | 🔴 $0.50 | 🔴 $0.98 |
| **Token Compression** | N/A | N/A | ✅ Starts | ✅ Active | ✅ Heavy | ✅ Maximum |
| **Summarization Active** | ❌ No | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

**Key Tradeoffs:**
- **Small buffer (5-10)**: Fast, cheap, but poor accuracy (lacks context)
- **Medium buffer (20-40)**: Balanced - good accuracy, reasonable cost
- **Large buffer (80-160)**: Best accuracy, but expensive and slow

---

## 🔧 Implementation Strategy

### Step 1: Modify `TreeNode` to Accept Buffer Size
**File:** `backend/src/models/tree.py` line 314

```python
import os

class TreeNode:
    def __init__(self, node_id: Optional[str] = None, title: str = 'Untitled', 
                 parent: Optional['TreeNode'] = None, vector_index=None, 
                 llm_client=None, buffer_size: Optional[int] = None):
        
        # Get buffer size from parameter, env var, or default to 15
        if buffer_size is None:
            buffer_size = int(os.getenv('BUFFER_SIZE', '15'))
        
        self.node_id: str = node_id if node_id else str(uuid.uuid4())
        self.title: str = title
        self.parent: Optional['TreeNode'] = parent
        self.children: List['TreeNode'] = []
        
        # ✅ Use dynamic buffer size
        self.buffer: LocalBuffer = LocalBuffer(
            max_turns=buffer_size,  # ← DYNAMIC NOW!
            vector_index=vector_index,
            node_id=self.node_id,
            llm_client=llm_client,
            node_title=title
        )
        # ... rest of init
```

### Step 2: Update `ChatGraphManager` 
**File:** `backend/src/services/chat_manager.py` line 18

```python
def create_node(self, title: str, parent_id: Optional[str] = None, 
                selected_text: str = None, follow_up_context: str = None, 
                context_type: str = "general", buffer_size: Optional[int] = None) -> TreeNode:
    
    parent = self.node_map.get(parent_id) if parent_id else None
    
    # ✅ Pass buffer_size through
    node = TreeNode(
        title=title, 
        parent=parent, 
        vector_index=self.vector_index, 
        llm_client=self.llm_client,
        buffer_size=buffer_size  # ← NEW PARAMETER
    )
    # ... rest of method
```

### Step 3: Update `Forest` Class
**File:** `backend/src/services/forest.py` line 19

```python
def create_tree(self, title: str = "Untitled", buffer_size: Optional[int] = None) -> TreeNode:
    root = TreeNode(
        title=title, 
        vector_index=vector_index, 
        llm_client=llm_client,
        buffer_size=buffer_size  # ← NEW PARAMETER
    )
    # ... rest of method
```

### Step 4: Test Runner with Auto-Restart
**File:** `backend/dataset/buffer_test_runner.py`

```python
def restart_server_with_buffer_size(self, buffer_size: int):
    """Kill server, restart with new buffer size, wait for ready"""
    
    # 1. Stop existing server
    self.log(f"🛑 Stopping server...", "INFO")
    os.system("pkill -f 'python -m src.main'")
    os.system("pkill -f 'uvicorn'")
    time.sleep(3)
    
    # 2. Delete ChromaDB to clear vector store
    chroma_path = Path(__file__).parent.parent / "chroma_db"
    if chroma_path.exists():
        import shutil
        shutil.rmtree(chroma_path)
        self.log(f"🗑️  Cleared ChromaDB", "INFO")
    
    # 3. Start server with new buffer size
    self.log(f"🚀 Starting server with BUFFER_SIZE={buffer_size}...", "INFO")
    
    env = os.environ.copy()
    env['BUFFER_SIZE'] = str(buffer_size)
    
    server_dir = Path(__file__).parent.parent
    self.server_process = subprocess.Popen(
        ["python", "-m", "src.main"],
        cwd=str(server_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 4. Wait for server ready
    time.sleep(10)
    if not self.wait_for_server_ready():
        raise Exception(f"Server failed to start with buffer_size={buffer_size}")
    
    self.log(f"✅ Server ready with BUFFER_SIZE={buffer_size}", "INFO")


def run_full_buffer_evaluation(self, scenario_files: List[str]):
    """Test with all buffer sizes [5, 10, 20, 40, 80, 160]"""
    
    buffer_sizes = [5, 10, 20, 40, 80, 160]
    all_results = {}
    
    for buffer_size in buffer_sizes:
        self.log(f"\n{'='*80}", "INFO")
        self.log(f"📊 TESTING BUFFER SIZE = {buffer_size}", "INFO")
        self.log(f"{'='*80}\n", "INFO")
        
        # Run tests for this buffer size
        baseline_results = []
        system_results = []
        
        for scenario_file in scenario_files:
            scenario = self.load_scenario(scenario_file)
            
            # BASELINE TEST
            self.restart_server_with_buffer_size(buffer_size)
            baseline = self.run_baseline_test(scenario)
            baseline_results.extend(baseline)
            
            # SYSTEM TEST
            self.restart_server_with_buffer_size(buffer_size)
            system = self.run_system_test(scenario)
            system_results.extend(system)
        
        # Calculate metrics
        metrics = self.calculate_metrics(baseline_results, system_results)
        
        # Generate tables for this buffer size
        output_dir = self.logs_dir / "tables" / f"buffer_{buffer_size}"
        output_dir.mkdir(parents=True, exist_ok=True)
        self.generate_table(metrics, output_dir)
        
        # Store for aggregation
        all_results[buffer_size] = metrics
    
    # Generate comparison visualization
    self.generate_buffer_comparison_viz(all_results)
```

---

## 🎯 Summary: What Changes and Why

### Buffer Size 5 → 160 Effects:

1. **Context Size** ⬆️
   - More messages in buffer → More context sent to LLM
   - Better understanding but higher token cost

2. **Summarization** 🔄
   - Buffer < 15: No summarization
   - Buffer ≥ 15: Rolling summaries of old messages
   - More cycles with larger buffers

3. **Token Usage** ⬆️
   - Input tokens: ~150 per message × buffer_size
   - Grows linearly with buffer size

4. **Latency** ⬆️
   - More tokens → Slower LLM processing
   - Roughly linear growth

5. **Cost** ⬆️
   - Proportional to token usage
   - Can be 20x higher (5 → 160)

6. **Accuracy** ⬆️
   - More context → Better answers
   - Diminishing returns after buffer=40

7. **RAG Utilization** ⬇️
   - Larger buffer → Fewer messages need retrieval
   - Buffer already has recent history

---

## ✅ Testing Checklist

- [ ] Modify `TreeNode.__init__()` to accept `buffer_size` parameter
- [ ] Add environment variable support `BUFFER_SIZE`
- [ ] Update `ChatGraphManager.create_node()` to pass buffer_size
- [ ] Update `Forest.create_tree()` to pass buffer_size
- [ ] Implement `restart_server_with_buffer_size()` in test runner
- [ ] Test with buffer_sizes = [5, 10, 20, 40, 80, 160]
- [ ] Generate tables for each buffer size
- [ ] Create visualization comparing all buffer sizes
- [ ] Verify summarization works for buffer ≥ 15
- [ ] Verify no summarization for buffer < 15
