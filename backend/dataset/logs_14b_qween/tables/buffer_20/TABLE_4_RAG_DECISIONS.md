# TABLE 4: RAG DECISION BREAKDOWN (Buffer Size: 20)

Shows how the LLM's Phase 1 JSON decision split across all turns.
**RAG Triggered** = LLM decided archived context was needed.
**Buffer Sufficient** = LLM decided recent buffer had enough info.

| Metric | Baseline | System |
|--------|----------|--------|
| **Total Turns** | 309 | 309 |
| **RAG-Eligible Turns** | 309 | 309 |
| **RAG Triggered** | 39 | 28 |
| **Buffer Sufficient** | 270 | 281 |
| **Retrieval Rate** | 12.6% | 9.1% |
| **Buffer Rate** | 87.4% | 90.9% |
