# Component Testing Logs - FULL (Append Mode)

This directory contains **APPEND-ONLY** debug logs for complete debugging history.

## Difference from `component-testing/`

| Feature | `component-testing/` | `component-testing-full/` |
|---------|---------------------|---------------------------|
| **Mode** | Overwrite | Append |
| **Purpose** | User viewing (latest query only) | Developer debugging (full history) |
| **File Size** | Small (1 query) | Large (all queries) |
| **Best For** | Quick analysis | Pattern detection, bug tracking |

## Files

### 1. **VECTOR_STORE.log**
Complete history of vector store states.
- Each entry shows snapshot at that time
- **Appended** with timestamps
- Track how messages accumulate over time

### 2. **RETRIEVAL.log**
Complete history of all RAG retrievals.
- Every retrieval logged with full details
- Sub-query results for each query
- **Appended** with timestamps
- Track retrieval patterns and failures

### 3. **BUFFER.log**
Complete history of buffer states.
- Every buffer update logged
- **Appended** with timestamps
- Track buffer evolution and evictions

### 4. **COT_THINKING.log**
Complete history of LLM decisions.
- Every CoT decision logged
- **Appended** with timestamps
- Track when LLM chooses retrieval vs buffer

## Usage

### For Pattern Detection:
```bash
# Find all times "cricket" was searched
grep -A 20 "cricket" RETRIEVAL.log

# See when buffer was full
grep "Buffer (10/10)" BUFFER.log

# Track LLM decision patterns
grep "FINAL DECISION" COT_THINKING.log
```

### For Bug Tracking:
1. Reproduce the bug multiple times
2. Check this directory for patterns
3. Compare with `component-testing/` for latest state

### For Performance Analysis:
1. Count how many retrievals happened
2. Analyze sub-query effectiveness
3. Track buffer hit rates

## Notes

- **Files grow over time** - may need to clear occasionally
- **Timestamps** help correlate events across files
- **Complete history** helps identify intermittent issues
- Use `component-testing/` for quick checks, this for deep dives
