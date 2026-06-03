# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 5)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 309 | 309 |
| **RAG Triggered** | 47 | 48 |
| **Buffer Sufficient** | 262 | 261 |
| **Retrieval Rate** | 15.2% | 15.5% |
| **Buffer Rate** | 84.8% | 84.5% |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 43 |
| **Probe RAG Triggered** | 1 | 17 |
| **Probe Buffer Sufficient** | 42 | 26 |
| **Probe Retrieval Rate** | 2.3% | 39.5% |
| **Probe Buffer Rate** | 97.7% | 60.5% |
