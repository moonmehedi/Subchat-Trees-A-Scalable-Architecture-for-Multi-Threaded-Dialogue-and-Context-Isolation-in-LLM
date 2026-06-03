# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 10)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 309 | 309 |
| **RAG Triggered** | 26 | 29 |
| **Buffer Sufficient** | 283 | 280 |
| **Retrieval Rate** | 8.4% | 9.4% |
| **Buffer Rate** | 91.6% | 90.6% |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 43 |
| **Probe RAG Triggered** | 19 | 1 |
| **Probe Buffer Sufficient** | 24 | 42 |
| **Probe Retrieval Rate** | 44.2% | 2.3% |
| **Probe Buffer Rate** | 55.8% | 97.7% |
