# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 10)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 3384 | 3556 | **+5.1%** |
| **Avg Output Tokens** | 214 | 235 | **+9.8%** |
| **Avg Total Tokens** | 3598 | 3791 | **+5.4%** |
| **Tokens Per Correct Answer** | 9038 | 8191 | **-9.4%** |
| **Avg Latency** | 10.62s | 10.55s | **-0.7%** |
| **Token Compression Rate** | 0% | -5.4% | **0.95x compression** |
| **Cost per Query** | $0.000186 | $0.000197 | **+5.5%** |
| **Cost per 1M Queries** | $186 | $197 | **$+10 (+5.5%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 1111680 | 1171373 | **+5.4% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 252519 | 188722 | **-25.3%** |
| **Avg Tokens per Summarization Probe** | 5873 | 4389 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 1364199 | 1360095 | **-0.3%** |
| **Combined Avg Tokens per Call** | 3876 | 3864 | **-0.3%** |
