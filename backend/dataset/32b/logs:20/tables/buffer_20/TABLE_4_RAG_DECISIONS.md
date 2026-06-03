# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 20)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 309 | 309 |
| **RAG Triggered** | 71 | 67 |
| **Buffer Sufficient** | 238 | 242 |
| **Retrieval Rate** | 23.0% | 21.7% |
| **Buffer Rate** | 77.0% | 78.3% |

## Recall/Summarization Probe RAG Decisions

These are the end-of-topic summarization probes used for recall scoring. They are reported separately from normal conversation turns.

| Metric | Baseline | System |
|--------|----------|--------|
| **Probe Turns** | 43 | 43 |
| **RAG-Eligible Probe Turns** | 43 | 43 |
| **Probe RAG Triggered** | 26 | 8 |
| **Probe Buffer Sufficient** | 17 | 35 |
| **Probe Retrieval Rate** | 60.5% | 18.6% |
| **Probe Buffer Rate** | 39.5% | 81.4% |
