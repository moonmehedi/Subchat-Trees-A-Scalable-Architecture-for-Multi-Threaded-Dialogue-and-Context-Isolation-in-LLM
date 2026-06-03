# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 40)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 6252 | 6405 | **+2.5%** |
| **Avg Output Tokens** | 162 | 170 | **+5.0%** |
| **Avg Total Tokens** | 6413 | 6575 | **+2.5%** |
| **Tokens Per Correct Answer** | 10060 | 8833 | **-12.2%** |
| **Avg Latency** | 34.77s | 33.56s | **-3.5%** |
| **Token Compression Rate** | 0% | -2.5% | **0.98x compression** |
| **Cost per Query** | $0.000326 | $0.000334 | **+2.6%** |
| **Cost per 1M Queries** | $326 | $334 | **$+8 (+2.6%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 1981748 | 2031629 | **+2.5% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 324171 | 310617 | **-4.2%** |
| **Avg Tokens per Summarization Probe** | 7539 | 7224 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 2305919 | 2342246 | **+1.6%** |
| **Combined Avg Tokens per Call** | 6551 | 6654 | **+1.6%** |
