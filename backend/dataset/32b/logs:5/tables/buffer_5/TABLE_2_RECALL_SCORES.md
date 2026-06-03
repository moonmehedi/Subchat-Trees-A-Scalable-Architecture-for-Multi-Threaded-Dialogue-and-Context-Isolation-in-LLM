# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 5)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.2687 | 0.4328 | **+61.1%** |
| **Avg ROUGE-L (F1)** | 0.1767 | 0.2830 | **+60.2%** |
| **Avg BLEU-2** | 0.0502 | 0.1452 | **+189.4%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 119832 | 131487 | - |
| **Avg Tokens per Probe** | 2787 | 3058 | - |
| **Total Probe Latency** | 1959.9s | 2495.1s | - |
| **Avg Probe Latency** | 45.58s | 58.03s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.3593 | 0.2817 | 0.1629 | 0.1596 | 0.0435 | 0.0100 |
| ai_consciousness | 0.2589 | 0.2945 | 0.1431 | 0.1848 | 0.0076 | 0.0153 |
| ai_consciousness_friendship | 0.3647 | 0.4213 | 0.1563 | 0.2272 | 0.0723 | 0.0778 |
| ai_meta | 0.3122 | 0.2893 | 0.1306 | 0.1736 | 0.0359 | 0.0140 |
| bhutan_travel | 0.0681 | 0.4394 | 0.0481 | 0.3653 | 0.0000 | 0.0490 |
| chess | 0.1337 | 0.2837 | 0.0840 | 0.1576 | 0.0003 | 0.0124 |
| child_nutrition | 0.0638 | 0.4402 | 0.0435 | 0.2912 | 0.0000 | 0.1020 |
| cookies_recipe_halving | 0.2179 | 0.2867 | 0.1401 | 0.1470 | 0.0086 | 0.0246 |
| cookies_recipe_halving_argument | 0.4920 | 0.5110 | 0.2812 | 0.2912 | 0.1584 | 0.1943 |
| cookies_recipe_halving_corrections | 0.3374 | 0.4641 | 0.1963 | 0.2762 | 0.0532 | 0.1553 |
| cookies_recipe_halving_math_errors | 0.2980 | 0.3601 | 0.1806 | 0.1918 | 0.0368 | 0.0641 |
| covid_safety | 0.0666 | 0.3727 | 0.0378 | 0.1660 | 0.0000 | 0.0334 |
| covid_safety_hiv_aids | 0.2625 | 0.2839 | 0.2179 | 0.1986 | 0.0045 | 0.0292 |
| dsp_wavelets | 0.0219 | 0.1659 | 0.0170 | 0.1068 | 0.0000 | 0.0001 |
| electroculture | 0.3497 | 0.3807 | 0.3174 | 0.3150 | 0.0230 | 0.0398 |
| emoji_game | 0.0530 | 0.2049 | 0.0419 | 0.1449 | 0.0000 | 0.0047 |
| game_degree_guess | 0.2363 | 0.5035 | 0.1519 | 0.2517 | 0.0021 | 0.2231 |
| game_twenty_questions | 0.0622 | 0.3232 | 0.0470 | 0.2216 | 0.0000 | 0.0378 |
| geography_belgium | 0.2431 | 0.7078 | 0.1389 | 0.5994 | 0.0092 | 0.5862 |
| humanity_future_150y | 0.0726 | 0.4762 | 0.0495 | 0.3692 | 0.0000 | 0.1126 |
| indian_astrology | 0.2117 | 0.3719 | 0.1696 | 0.2049 | 0.0014 | 0.0445 |
| indian_history | 0.4359 | 0.5957 | 0.3333 | 0.4574 | 0.2017 | 0.3420 |
| indian_legal | 0.2776 | 0.5057 | 0.2310 | 0.4211 | 0.0164 | 0.1489 |
| indian_legal_family | 0.3731 | 0.4562 | 0.2533 | 0.4253 | 0.0383 | 0.1027 |
| jokes | 0.1695 | 0.5631 | 0.1186 | 0.4725 | 0.0036 | 0.3549 |
| karnataka_elections | 0.5378 | 0.4565 | 0.3761 | 0.3130 | 0.2233 | 0.1528 |
| linux_audio | 0.3931 | 0.6580 | 0.1792 | 0.5152 | 0.0654 | 0.4264 |
| literature_camus | 0.4306 | 0.4123 | 0.3375 | 0.1921 | 0.0827 | 0.0621 |
| llm_knowledge | 0.3466 | 0.2486 | 0.2470 | 0.2336 | 0.0315 | 0.0035 |
| logic_puzzle | 0.1705 | 0.6264 | 0.1172 | 0.4451 | 0.0113 | 0.2971 |
| lsat_medical_conference | 0.3634 | 0.5178 | 0.2782 | 0.4139 | 0.0791 | 0.1617 |
| lsat_product_codes | 0.1460 | 0.1701 | 0.0902 | 0.1438 | 0.0008 | 0.0003 |
| medical_dsd | 0.5132 | 0.6422 | 0.3383 | 0.3028 | 0.1895 | 0.3432 |
| personas_roleplay | 0.1545 | 0.3648 | 0.0935 | 0.2240 | 0.0017 | 0.0723 |
| physics_cosmology | 0.1074 | 0.7212 | 0.0785 | 0.3806 | 0.0016 | 0.5549 |
| physics_violin_nanoscale | 0.1750 | 0.6464 | 0.1125 | 0.3802 | 0.0024 | 0.4295 |
| scifi_films | 0.1024 | 0.3740 | 0.0599 | 0.2044 | 0.0000 | 0.0470 |
| scifi_films_hal9000 | 0.2781 | 0.4240 | 0.1716 | 0.2026 | 0.0298 | 0.1229 |
| scifi_films_hal9000_games | 0.2012 | 0.2663 | 0.1096 | 0.1341 | 0.0025 | 0.0124 |
| scifi_films_liu_cixin | 0.4142 | 0.5891 | 0.2973 | 0.3492 | 0.0652 | 0.3296 |
| therapy | 0.4405 | 0.4694 | 0.3688 | 0.2985 | 0.1285 | 0.1151 |
| therapy_manipulation | 0.3303 | 0.5221 | 0.1920 | 0.3417 | 0.0197 | 0.1637 |
| wildfires_alberta | 0.7071 | 0.5173 | 0.4591 | 0.2747 | 0.5053 | 0.1687 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 37 topics
- 🔵 **Baseline wins**: 6 topics
- 🟡 **Ties (±0.01)**: 0 topics
