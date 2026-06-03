# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 40)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 302 | 309 |
| **RAG Triggered** | 6 | 9 |
| **Buffer Sufficient** | 296 | 300 |
| **Retrieval Rate** | 2.0% | 2.9% |
| **Buffer Rate** | 98.0% | 97.1% |
| **Errors** | 7 | 0 |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 43 |
| **Probe RAG Triggered** | 0 | 1 |
| **Probe Buffer Sufficient** | 43 | 42 |
| **Probe Retrieval Rate** | 0.0% | 2.3% |
| **Probe Buffer Rate** | 100.0% | 97.7% |
