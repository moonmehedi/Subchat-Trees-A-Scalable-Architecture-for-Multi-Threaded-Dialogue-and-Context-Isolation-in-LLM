# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 40)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 5685 | 5981 | **+5.2%** |
| **Avg Output Tokens** | 148 | 160 | **+8.5%** |
| **Avg Total Tokens** | 5833 | 6141 | **+5.3%** |
| **Tokens Per Correct Answer** | 10418 | 8826 | **-15.3%** |
| **Avg Latency** | 14.58s | 14.64s | **+0.4%** |
| **Token Compression Rate** | 0% | -5.3% | **0.95x compression** |
| **Cost per Query** | $0.000296 | $0.000312 | **+5.3%** |
| **Cost per 1M Queries** | $296 | $312 | **$+16 (+5.3%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 1802333 | 1897579 | **+5.3% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 359355 | 304196 | **-15.3%** |
| **Avg Tokens per Summarization Probe** | 8357 | 7074 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 2161688 | 2201775 | **+1.9%** |
| **Combined Avg Tokens per Call** | 6141 | 6255 | **+1.9%** |
