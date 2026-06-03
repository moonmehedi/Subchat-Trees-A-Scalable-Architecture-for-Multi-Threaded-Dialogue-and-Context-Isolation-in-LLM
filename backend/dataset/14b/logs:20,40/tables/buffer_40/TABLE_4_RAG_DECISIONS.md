# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 40)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 284 | 291 |
| **RAG Triggered** | 22 | 21 |
| **Buffer Sufficient** | 262 | 270 |
| **Retrieval Rate** | 7.7% | 7.2% |
| **Buffer Rate** | 92.3% | 92.8% |
| **Errors** | 25 | 18 |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 41 |
| **Probe RAG Triggered** | 7 | 0 |
| **Probe Buffer Sufficient** | 36 | 41 |
| **Probe Retrieval Rate** | 16.3% | 0.0% |
| **Probe Buffer Rate** | 83.7% | 100.0% |
| **Probe Errors** | 0 | 2 |
