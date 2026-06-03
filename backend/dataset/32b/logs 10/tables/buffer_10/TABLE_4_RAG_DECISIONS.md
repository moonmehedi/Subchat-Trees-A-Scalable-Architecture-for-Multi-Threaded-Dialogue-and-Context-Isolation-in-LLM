# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 10)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 309 | 309 |
| **RAG Triggered** | 84 | 66 |
| **Buffer Sufficient** | 225 | 243 |
| **Retrieval Rate** | 27.2% | 21.4% |
| **Buffer Rate** | 72.8% | 78.6% |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 43 |
| **Probe RAG Triggered** | 40 | 23 |
| **Probe Buffer Sufficient** | 3 | 20 |
| **Probe Retrieval Rate** | 93.0% | 53.5% |
| **Probe Buffer Rate** | 7.0% | 46.5% |
