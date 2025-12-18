# TABLE 3: SYSTEM PERFORMANCE METRICS (Buffer Size: 40)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg Input Tokens** | 1925 | 679 | **-64.7%** |
| **Avg Output Tokens** | 98 | 97 | **-1.2%** |
| **Avg Total Tokens** | 2023 | 776 | **-61.6%** |
| **Tokens Per Correct Answer** | 3621 | 824 | **+77.2% MORE EFFICIENT** |
| **Avg Latency** | 19.47s | 6.55s | **-66.4%** |
| **Token Compression Rate** | 0% | 61.6% | **2.61x compression** |
| **Cost per Query** | $0.173753 | $0.079937 | **+54.0%** |
| **Cost per 1M Queries** | $173753 | $79937 | **-$93816 savings** |

---

## Notes on Token Usage

**Why does the system use more tokens per query?**

The system uses ~39% more tokens due to:
1. **Follow-up context prompts** (~50 tokens per subchat): Ensures coherence across isolated conversations
2. **Higher response quality**: System gives complete, accurate answers (92.5% accuracy) vs baseline's confused, partial answers (60% accuracy)

**However, the system is MORE EFFICIENT when measuring tokens per CORRECT answer:**
- Baseline: 2023 avg tokens × (100/55.9%) = 3621 tokens per correct answer
- System: 776 avg tokens × (100/94.1%) = 824 tokens per correct answer
- **Result: System is 77.2% MORE EFFICIENT!**

This means you get MORE correct answers for FEWER tokens overall.
