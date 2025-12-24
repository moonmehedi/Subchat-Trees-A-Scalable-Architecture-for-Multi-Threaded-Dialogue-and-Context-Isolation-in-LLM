# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: 10)

## Weighted Average Metrics (Per-Topic Confusion Matrix)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Precision** | 94.9% | 100.0% | **+5.3%** |
| **Recall** | 93.9% | 100.0% | **+6.5%** |
| **F1** | 93.8% | 100.0% | **+6.6%** |
| **Accuracy** | 0.0% | 0.0% | **+0.0%** |
| **Pollution Rate** | 100.0% | 100.0% | **+0.0%** |

## Macro Average Metrics

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Macro Precision** | 95.8% | 100.0% | **+4.3%** |
| **Macro Recall** | 94.4% | 100.0% | **+5.9%** |
| **Macro F1** | 94.6% | 100.0% | **+5.7%** |

## Per-Topic Breakdown


### Baseline - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| by_length | 100.0% | 77.8% | 87.5% | 7 | 0 | 2 | 9 |
| histogram | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| move_one_ball | 83.3% | 100.0% | 90.9% | 10 | 2 | 0 | 10 |
| odd_count | 100.0% | 100.0% | 100.0% | 9 | 0 | 0 | 9 |

### Our System - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| by_length | 100.0% | 100.0% | 100.0% | 9 | 0 | 0 | 9 |
| histogram | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| move_one_ball | 100.0% | 100.0% | 100.0% | 10 | 0 | 0 | 10 |
| odd_count | 100.0% | 100.0% | 100.0% | 9 | 0 | 0 | 9 |

## Legacy Raw Counts (LLM Judge TP/FN)
- Baseline: TP=0, TN=0, FP=34, FN=0
- System: TP=0, TN=0, FP=34, FN=0
