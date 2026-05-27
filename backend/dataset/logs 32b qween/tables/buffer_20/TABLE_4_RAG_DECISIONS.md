# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 20)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 308 | 309 |
| **RAG Triggered** | 87 | 79 |
| **Buffer Sufficient** | 221 | 230 |
| **Retrieval Rate** | 28.2% | 25.6% |
| **Buffer Rate** | 71.8% | 74.4% |
| **Errors** | 1 | 0 |
