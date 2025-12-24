# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: 10)

## Weighted Average Metrics (Per-Topic Confusion Matrix)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Precision** | 93.6% | 100.0% | **+6.8%** |
| **Recall** | 90.9% | 87.9% | **-3.3%** |
| **F1** | 92.2% | 93.4% | **+1.3%** |
| **Accuracy** | 88.2% | 85.3% | **-3.3%** |
| **Pollution Rate** | 11.8% | 14.7% | **+25.0%** |

## Macro Average Metrics

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Macro Precision** | 94.4% | 100.0% | **+5.9%** |
| **Macro Recall** | 92.2% | 89.2% | **-3.3%** |
| **Macro F1** | 93.3% | 94.1% | **+0.9%** |

## Per-Topic Breakdown


### Baseline - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| by_length | 88.9% | 88.9% | 88.9% | 8 | 1 | 1 | 9 |
| histogram | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| move_one_ball | 88.9% | 80.0% | 84.2% | 8 | 1 | 2 | 10 |
| odd_count | 100.0% | 100.0% | 100.0% | 9 | 0 | 0 | 9 |

### Our System - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| by_length | 100.0% | 77.8% | 87.5% | 7 | 0 | 2 | 9 |
| histogram | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| move_one_ball | 100.0% | 90.0% | 94.7% | 9 | 0 | 1 | 10 |
| odd_count | 100.0% | 88.9% | 94.1% | 8 | 0 | 1 | 9 |

## Legacy Raw Counts (LLM Judge TP/FN)
- Baseline: TP=30, TN=0, FP=4, FN=0
- System: TP=29, TN=0, FP=5, FN=0
