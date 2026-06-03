# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 40)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.1557 | 0.3545 | **+127.7%** |
| **Avg ROUGE-L (F1)** | 0.0861 | 0.2574 | **+199.0%** |
| **Avg BLEU-2** | 0.0172 | 0.1142 | **+565.3%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 472634 | 403852 | - |
| **Avg Tokens per Probe** | 10991 | 9392 | - |
| **Total Probe Latency** | 723.5s | 703.1s | - |
| **Avg Probe Latency** | 16.82s | 16.35s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.1821 | 0.2635 | 0.0802 | 0.1579 | 0.0087 | 0.0126 |
| ai_consciousness | 0.1662 | 0.3648 | 0.0803 | 0.3455 | 0.0016 | 0.0352 |
| ai_consciousness_friendship | 0.3581 | 0.5567 | 0.1266 | 0.3264 | 0.0600 | 0.1982 |
| ai_meta | 0.1769 | 0.3214 | 0.0750 | 0.1923 | 0.0031 | 0.0148 |
| bhutan_travel | 0.3304 | 0.5440 | 0.1550 | 0.4456 | 0.0804 | 0.1759 |
| chess | 0.2354 | 0.4324 | 0.1111 | 0.3430 | 0.0255 | 0.1829 |
| child_nutrition | 0.1934 | 0.1596 | 0.0889 | 0.1138 | 0.0082 | 0.0000 |
| cookies_recipe_halving | 0.0841 | 0.6293 | 0.0664 | 0.4829 | 0.0000 | 0.3456 |
| cookies_recipe_halving_argument | 0.2921 | 0.6237 | 0.1445 | 0.3041 | 0.0649 | 0.3063 |
| cookies_recipe_halving_corrections | 0.1684 | 0.6911 | 0.1006 | 0.3740 | 0.0030 | 0.4252 |
| cookies_recipe_halving_math_errors | 0.2279 | 0.6458 | 0.1348 | 0.5432 | 0.0074 | 0.3792 |
| covid_safety | 0.1893 | 0.0698 | 0.0930 | 0.0640 | 0.0006 | 0.0000 |
| covid_safety_hiv_aids | 0.0599 | 0.1566 | 0.0434 | 0.1398 | 0.0000 | 0.0000 |
| dsp_wavelets | 0.0609 | 0.0963 | 0.0359 | 0.0713 | 0.0000 | 0.0000 |
| electroculture | 0.0591 | 0.3274 | 0.0456 | 0.3265 | 0.0000 | 0.0187 |
| emoji_game | 0.0419 | 0.3000 | 0.0389 | 0.1529 | 0.0000 | 0.0394 |
| game_degree_guess | 0.1073 | 0.4763 | 0.0683 | 0.3312 | 0.0001 | 0.1302 |
| game_twenty_questions | 0.0499 | 0.3575 | 0.0369 | 0.3238 | 0.0000 | 0.0558 |
| geography_belgium | 0.1328 | 0.6110 | 0.0945 | 0.3808 | 0.0000 | 0.3593 |
| humanity_future_150y | 0.0458 | 0.4304 | 0.0316 | 0.4094 | 0.0000 | 0.0846 |
| indian_astrology | 0.0424 | 0.0185 | 0.0306 | 0.0139 | 0.0000 | 0.0000 |
| indian_history | 0.1618 | 0.5185 | 0.1225 | 0.4233 | 0.0238 | 0.3107 |
| indian_legal | 0.2389 | 0.3860 | 0.1194 | 0.2202 | 0.0337 | 0.0452 |
| indian_legal_family | 0.1953 | 0.0270 | 0.1316 | 0.0180 | 0.0592 | 0.0000 |
| jokes | 0.2804 | 0.6638 | 0.1771 | 0.5319 | 0.1276 | 0.5105 |
| karnataka_elections | 0.2916 | 0.2995 | 0.1434 | 0.2047 | 0.0659 | 0.0100 |
| linux_audio | 0.3300 | 0.0591 | 0.1449 | 0.0432 | 0.0518 | 0.0000 |
| literature_camus | 0.2126 | 0.0270 | 0.0937 | 0.0240 | 0.0069 | 0.0000 |
| llm_knowledge | 0.0194 | 0.2085 | 0.0141 | 0.1513 | 0.0000 | 0.0008 |
| logic_puzzle | 0.1870 | 0.6263 | 0.1220 | 0.4811 | 0.0353 | 0.3373 |
| lsat_medical_conference | 0.1206 | 0.6977 | 0.0778 | 0.6487 | 0.0111 | 0.3805 |
| lsat_product_codes | 0.0762 | 0.2708 | 0.0557 | 0.2610 | 0.0000 | 0.0060 |
| medical_dsd | 0.1974 | 0.3406 | 0.1138 | 0.1339 | 0.0046 | 0.0222 |
| personas_roleplay | 0.0653 | 0.4448 | 0.0435 | 0.2517 | 0.0000 | 0.1763 |
| physics_cosmology | 0.2125 | 0.4503 | 0.1324 | 0.3874 | 0.0257 | 0.0943 |
| physics_violin_nanoscale | 0.1557 | 0.2977 | 0.1107 | 0.2558 | 0.0016 | 0.0180 |
| scifi_films | 0.0601 | 0.2759 | 0.0384 | 0.2287 | 0.0000 | 0.0058 |
| scifi_films_hal9000 | 0.0791 | 0.4857 | 0.0494 | 0.2491 | 0.0000 | 0.1530 |
| scifi_films_hal9000_games | 0.0462 | 0.2645 | 0.0361 | 0.1391 | 0.0000 | 0.0074 |
| scifi_films_liu_cixin | 0.0996 | 0.3695 | 0.0630 | 0.2516 | 0.0000 | 0.0496 |
| therapy | 0.1086 | 0.0428 | 0.0658 | 0.0293 | 0.0000 | 0.0000 |
| therapy_manipulation | 0.0984 | 0.0867 | 0.0679 | 0.0559 | 0.0000 | 0.0000 |
| wildfires_alberta | 0.2525 | 0.3232 | 0.0957 | 0.2352 | 0.0273 | 0.0186 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 34 topics
- 🔵 **Baseline wins**: 8 topics
- 🟡 **Ties (±0.01)**: 1 topics
