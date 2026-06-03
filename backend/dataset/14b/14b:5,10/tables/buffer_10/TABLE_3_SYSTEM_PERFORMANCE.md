# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 10)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 3152 | 3092 | **-1.9%** |
| **Avg Output Tokens** | 170 | 182 | **+7.2%** |
| **Avg Total Tokens** | 3321 | 3274 | **-1.4%** |
| **Tokens Per Correct Answer** | 5548 | 4079 | **-26.5%** |
| **Avg Latency** | 15.00s | 13.58s | **-9.5%** |
| **Token Compression Rate** | 0% | 1.4% | **1.01x compression** |
| **Cost per Query** | $0.000171 | $0.000169 | **-1.2%** |
| **Cost per 1M Queries** | $171 | $169 | **$-2 (-1.2%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 1026292 | 1011686 | **-1.4% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 274209 | 156136 | **-43.1%** |
| **Avg Tokens per Summarization Probe** | 6377 | 3631 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 1300501 | 1167822 | **-10.2%** |
| **Combined Avg Tokens per Call** | 3695 | 3318 | **-10.2%** |
