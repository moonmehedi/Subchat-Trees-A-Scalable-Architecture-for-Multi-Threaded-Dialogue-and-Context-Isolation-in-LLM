# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 20)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 4659 | 5396 | **+15.8%** |
| **Avg Output Tokens** | 177 | 215 | **+21.4%** |
| **Avg Total Tokens** | 4837 | 5611 | **+16.0%** |
| **Tokens Per Correct Answer** | 8036 | 6853 | **-14.7%** |
| **Avg Latency** | 16.06s | 17.69s | **+10.2%** |
| **Token Compression Rate** | 0% | -16.0% | **0.86x compression** |
| **Cost per Query** | $0.000247 | $0.000287 | **+16.1%** |
| **Cost per 1M Queries** | $247 | $287 | **$+40 (+16.1%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 1494607 | 1733862 | **+16.0% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 322902 | 269171 | **-16.6%** |
| **Avg Tokens per Summarization Probe** | 7509 | 6260 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 1817509 | 2003033 | **+10.2%** |
| **Combined Avg Tokens per Call** | 5163 | 5690 | **+10.2%** |
