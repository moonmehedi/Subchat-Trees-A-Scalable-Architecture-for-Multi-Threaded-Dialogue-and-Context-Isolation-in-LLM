# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 5)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 309 | 309 |
| **RAG Triggered** | 36 | 29 |
| **Buffer Sufficient** | 273 | 280 |
| **Retrieval Rate** | 11.7% | 9.4% |
| **Buffer Rate** | 88.3% | 90.6% |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 43 |
| **Probe RAG Triggered** | 25 | 10 |
| **Probe Buffer Sufficient** | 18 | 33 |
| **Probe Retrieval Rate** | 58.1% | 23.3% |
| **Probe Buffer Rate** | 41.9% | 76.7% |
