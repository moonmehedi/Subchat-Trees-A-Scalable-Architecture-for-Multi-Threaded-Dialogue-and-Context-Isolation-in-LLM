# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 20)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 306 | 309 |
| **RAG Triggered** | 27 | 30 |
| **Buffer Sufficient** | 279 | 279 |
| **Retrieval Rate** | 8.8% | 9.7% |
| **Buffer Rate** | 91.2% | 90.3% |
| **Errors** | 3 | 0 |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 43 |
| **Probe RAG Triggered** | 16 | 2 |
| **Probe Buffer Sufficient** | 27 | 41 |
| **Probe Retrieval Rate** | 37.2% | 4.7% |
| **Probe Buffer Rate** | 62.8% | 95.3% |
