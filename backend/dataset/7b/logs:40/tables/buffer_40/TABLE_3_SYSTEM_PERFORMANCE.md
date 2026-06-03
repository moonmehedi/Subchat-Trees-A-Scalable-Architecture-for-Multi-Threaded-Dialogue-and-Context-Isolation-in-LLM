# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 40)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 8107 | 8487 | **+4.7%** |
| **Avg Output Tokens** | 220 | 230 | **+4.5%** |
| **Avg Total Tokens** | 8327 | 8717 | **+4.7%** |
| **Tokens Per Correct Answer** | 102923 | 25899 | **-74.8%** |
| **Avg Latency** | 11.75s | 11.71s | **-0.3%** |
| **Token Compression Rate** | 0% | -4.7% | **0.96x compression** |
| **Cost per Query** | $0.000423 | $0.000443 | **+4.7%** |
| **Cost per 1M Queries** | $423 | $443 | **$+20 (+4.7%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 2573086 | 2693481 | **+4.7% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 472634 | 403852 | **-14.6%** |
| **Avg Tokens per Summarization Probe** | 10991 | 9392 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 3045720 | 3097333 | **+1.7%** |
| **Combined Avg Tokens per Call** | 8653 | 8799 | **+1.7%** |
