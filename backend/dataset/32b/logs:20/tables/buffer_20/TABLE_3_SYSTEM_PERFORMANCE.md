# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 20)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 5043 | 5292 | **+4.9%** |
| **Avg Output Tokens** | 191 | 219 | **+14.5%** |
| **Avg Total Tokens** | 5234 | 5511 | **+5.3%** |
| **Tokens Per Correct Answer** | 7775 | 6600 | **-15.1%** |
| **Avg Latency** | 38.99s | 39.29s | **+0.8%** |
| **Token Compression Rate** | 0% | -5.3% | **0.95x compression** |
| **Cost per Query** | $0.000267 | $0.000282 | **+5.5%** |
| **Cost per 1M Queries** | $267 | $282 | **$+15 (+5.5%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 1617294 | 1702877 | **+5.3% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 373285 | 264906 | **-29.0%** |
| **Avg Tokens per Summarization Probe** | 8681 | 6161 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 1990579 | 1967783 | **-1.1%** |
| **Combined Avg Tokens per Call** | 5655 | 5590 | **-1.1%** |
