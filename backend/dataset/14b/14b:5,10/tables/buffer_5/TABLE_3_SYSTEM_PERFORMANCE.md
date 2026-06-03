# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 5)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 1818 | 1919 | **+5.5%** |
| **Avg Output Tokens** | 133 | 145 | **+8.9%** |
| **Avg Total Tokens** | 1952 | 2064 | **+5.8%** |
| **Tokens Per Correct Answer** | 3700 | 2773 | **-25.0%** |
| **Avg Latency** | 16.71s | 16.16s | **-3.3%** |
| **Token Compression Rate** | 0% | -5.8% | **0.95x compression** |
| **Cost per Query** | $0.000102 | $0.000108 | **+5.9%** |
| **Cost per 1M Queries** | $102 | $108 | **$+6 (+5.9%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 603033 | 637814 | **+5.8% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 136045 | 104023 | **-23.5%** |
| **Avg Tokens per Summarization Probe** | 3164 | 2419 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 739078 | 741837 | **+0.4%** |
| **Combined Avg Tokens per Call** | 2100 | 2107 | **+0.4%** |
