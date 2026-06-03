# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 5)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 2270 | 2205 | **-2.9%** |
| **Avg Output Tokens** | 205 | 164 | **-20.2%** |
| **Avg Total Tokens** | 2476 | 2369 | **-4.3%** |
| **Tokens Per Correct Answer** | 11591 | 4067 | **-64.9%** |
| **Avg Latency** | 12.19s | 10.14s | **-16.8%** |
| **Token Compression Rate** | 0% | 4.3% | **1.04x compression** |
| **Cost per Query** | $0.000130 | $0.000123 | **-5.1%** |
| **Cost per 1M Queries** | $130 | $123 | **$-7 (-5.1%)** |

## Including Recall/Summarization Probes

Recall probes are the summarization-only memory checks. They are excluded from Table 1 F1, but included here for token-cost accounting.

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Normal Conversation Turns** | 309 | 309 | - |
| **Normal Conversation Total Tokens** | 765017 | 732147 | **-4.3% avg/turn** |
| **Summarization Probe Calls** | 43 | 43 | - |
| **Summarization Probe Tokens** | 158043 | 121521 | **-23.1%** |
| **Avg Tokens per Summarization Probe** | 3675 | 2826 | - |
| **Combined Evaluated Calls** | 352 | 352 | - |
| **Combined Total Tokens** | 923060 | 853668 | **-7.5%** |
| **Combined Avg Tokens per Call** | 2622 | 2425 | **-7.5%** |
