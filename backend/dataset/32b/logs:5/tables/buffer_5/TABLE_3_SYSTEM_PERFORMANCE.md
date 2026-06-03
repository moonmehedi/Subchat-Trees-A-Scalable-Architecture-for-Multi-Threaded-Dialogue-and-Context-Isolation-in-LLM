# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 5)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 2038 | 2119 | **+3.9%** |
| **Avg Output Tokens** | 139 | 158 | **+14.4%** |
| **Avg Total Tokens** | 2177 | 2277 | **+4.6%** |
| **Tokens Per Correct Answer** | 3363 | 2738 | **-18.6%** |
| **Avg Latency** | 36.91s | 35.86s | **-2.8%** |
| **Token Compression Rate** | 0% | -4.6% | **0.96x compression** |
| **Cost per Query** | $0.000113 | $0.000119 | **+5.0%** |
| **Cost per 1M Queries** | $113 | $119 | **$+6 (+5.0%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 672623 | 703603 | **+4.6% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 119832 | 131487 | **+9.7%** |
| **Avg Tokens per Summarization Probe** | 2787 | 3058 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 792455 | 835090 | **+5.4%** |
| **Combined Avg Tokens per Call** | 2251 | 2372 | **+5.4%** |
