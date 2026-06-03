# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 20)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 5386 | 5685 | **+5.6%** |
| **Avg Output Tokens** | 235 | 241 | **+2.5%** |
| **Avg Total Tokens** | 5622 | 5927 | **+5.4%** |
| **Tokens Per Correct Answer** | 35451 | 15389 | **-56.6%** |
| **Avg Latency** | 11.70s | 11.22s | **-4.1%** |
| **Token Compression Rate** | 0% | -5.4% | **0.95x compression** |
| **Cost per Query** | $0.000288 | $0.000304 | **+5.4%** |
| **Cost per 1M Queries** | $288 | $304 | **$+15 (+5.4%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 1737082 | 1831296 | **+5.4% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 336942 | 284817 | **-15.5%** |
| **Avg Tokens per Summarization Probe** | 7836 | 6624 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 2074024 | 2116113 | **+2.0%** |
| **Combined Avg Tokens per Call** | 5892 | 6012 | **+2.0%** |
