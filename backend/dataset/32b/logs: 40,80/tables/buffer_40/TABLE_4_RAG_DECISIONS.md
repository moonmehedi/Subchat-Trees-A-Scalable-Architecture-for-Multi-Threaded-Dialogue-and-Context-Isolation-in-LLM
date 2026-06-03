# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 40)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 300 | 306 |
| **RAG Triggered** | 64 | 48 |
| **Buffer Sufficient** | 236 | 258 |
| **Retrieval Rate** | 21.3% | 15.7% |
| **Buffer Rate** | 78.7% | 84.3% |
| **Errors** | 9 | 3 |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 42 |
| **Probe RAG Triggered** | 31 | 1 |
| **Probe Buffer Sufficient** | 12 | 41 |
| **Probe Retrieval Rate** | 72.1% | 2.4% |
| **Probe Buffer Rate** | 27.9% | 97.6% |
| **Probe Errors** | 0 | 1 |
