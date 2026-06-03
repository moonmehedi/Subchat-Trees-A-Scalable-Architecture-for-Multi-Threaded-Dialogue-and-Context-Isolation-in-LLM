# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 10)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 309 | 309 |
| **RAG Triggered** | 42 | 49 |
| **Buffer Sufficient** | 267 | 260 |
| **Retrieval Rate** | 13.6% | 15.9% |
| **Buffer Rate** | 86.4% | 84.1% |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 43 |
| **Probe RAG Triggered** | 2 | 9 |
| **Probe Buffer Sufficient** | 41 | 34 |
| **Probe Retrieval Rate** | 4.7% | 20.9% |
| **Probe Buffer Rate** | 95.3% | 79.1% |
