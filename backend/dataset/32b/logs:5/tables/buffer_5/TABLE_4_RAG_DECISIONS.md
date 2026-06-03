# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 5)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 309 | 309 |
| **RAG Triggered** | 61 | 80 |
| **Buffer Sufficient** | 248 | 229 |
| **Retrieval Rate** | 19.7% | 25.9% |
| **Buffer Rate** | 80.3% | 74.1% |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 43 |
| **Probe RAG Triggered** | 23 | 38 |
| **Probe Buffer Sufficient** | 20 | 5 |
| **Probe Retrieval Rate** | 53.5% | 88.4% |
| **Probe Buffer Rate** | 46.5% | 11.6% |
