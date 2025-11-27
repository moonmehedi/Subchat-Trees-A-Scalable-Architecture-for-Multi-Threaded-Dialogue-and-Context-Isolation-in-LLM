# Component Testing Logs

This directory contains detailed debug logs for analyzing system behavior.

## Files

### 1. **VECTOR_STORE.log**
Shows ALL messages currently indexed in the vector database.
- Organized by conversation node
- Shows full message text
- Includes timestamps and roles
- **Overwritt on each new user message**

### 2. **RETRIEVAL.log**
Shows RAG retrieval details when LLM searches for information.
- Original query
- Intent classification
- Sub-queries generated
- Final retrieved results with scores
- **Overwritten on each retrieval**

### 3. **BUFFER.log**
Shows ALL messages currently in the conversation buffer.
- Shows all 10 messages (not just last 3)
- Includes full message text
- Shows which node/conversation
- **Overwritten on each new user message**

### 4. **COT_THINKING.log**
Shows LLM's Chain-of-Thought reasoning process.
- User's query
- LLM's reasoning (scratchpad)
- Final decision (use retrieval or not)
- Search query if retrieval was used
- **Overwritten on each LLM decision**

## Usage

When debugging:
1. Ask a question in the UI
2. Check terminal for quick summary
3. Read these log files for detailed analysis

Example flow:
```
User asks: "what's my favorite game?"

BUFFER.log:
  - Shows last 10 messages in current conversation
  
COT_THINKING.log:
  - Shows LLM decided to use retrieval
  - Search query: "user favorite game"
  
RETRIEVAL.log:
  - Shows sub-queries generated
  - Shows retrieved results (e.g., "cricket is my favourite game")
  
VECTOR_STORE.log:
  - Shows ALL indexed messages across all conversations
```

## Notes

- Files are **OVERWRITTEN** (not appended) on each question
- This makes it easy to see exactly what happened for the most recent query
- Terminal output shows brief summaries; these files show complete details
