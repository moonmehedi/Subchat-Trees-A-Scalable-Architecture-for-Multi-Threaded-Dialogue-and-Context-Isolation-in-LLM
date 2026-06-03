# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 10)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 3165 | 3156 | **-0.3%** |
| **Avg Output Tokens** | 173 | 176 | **+1.5%** |
| **Avg Total Tokens** | 3338 | 3331 | **-0.2%** |
| **Tokens Per Correct Answer** | 4819 | 4151 | **-13.9%** |
| **Avg Latency** | 37.52s | 33.71s | **-10.1%** |
| **Token Compression Rate** | 0% | 0.2% | **1.00x compression** |
| **Cost per Query** | $0.000172 | $0.000172 | **-0.1%** |
| **Cost per 1M Queries** | $172 | $172 | **$-0 (-0.1%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 1031367 | 1029385 | **-0.2% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 249908 | 175875 | **-29.6%** |
| **Avg Tokens per Summarization Probe** | 5812 | 4090 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 1281275 | 1205260 | **-5.9%** |
| **Combined Avg Tokens per Call** | 3640 | 3424 | **-5.9%** |
