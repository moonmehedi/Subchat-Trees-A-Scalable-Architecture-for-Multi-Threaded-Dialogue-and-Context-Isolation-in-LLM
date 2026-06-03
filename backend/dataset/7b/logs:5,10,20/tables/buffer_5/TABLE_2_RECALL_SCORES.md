# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 5)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.2448 | 0.4240 | **+73.2%** |
| **Avg ROUGE-L (F1)** | 0.1270 | 0.3004 | **+136.6%** |
| **Avg BLEU-2** | 0.0364 | 0.1581 | **+333.9%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 158043 | 121521 | - |
| **Avg Tokens per Probe** | 3675 | 2826 | - |
| **Total Probe Latency** | 918.0s | 710.3s | - |
| **Avg Probe Latency** | 21.35s | 16.52s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.2021 | 0.4254 | 0.1276 | 0.2810 | 0.0168 | 0.0916 |
| ai_consciousness | 0.2580 | 0.4540 | 0.1159 | 0.1982 | 0.0119 | 0.1148 |
| ai_consciousness_friendship | 0.3911 | 0.4905 | 0.1508 | 0.2503 | 0.0633 | 0.1564 |
| ai_meta | 0.2663 | 0.2581 | 0.1241 | 0.1263 | 0.0260 | 0.0137 |
| bhutan_travel | 0.2285 | 0.4050 | 0.1183 | 0.3870 | 0.0156 | 0.0300 |
| chess | 0.3337 | 0.3140 | 0.1423 | 0.1433 | 0.0647 | 0.0375 |
| child_nutrition | 0.1623 | 0.3047 | 0.0724 | 0.1439 | 0.0038 | 0.0940 |
| cookies_recipe_halving | 0.3874 | 0.8199 | 0.1635 | 0.7291 | 0.1040 | 0.6555 |
| cookies_recipe_halving_argument | 0.4291 | 0.5270 | 0.2162 | 0.3556 | 0.1375 | 0.2428 |
| cookies_recipe_halving_corrections | 0.3542 | 0.5931 | 0.1644 | 0.3690 | 0.0756 | 0.2668 |
| cookies_recipe_halving_math_errors | 0.3121 | 0.8059 | 0.1545 | 0.6430 | 0.0444 | 0.6123 |
| covid_safety | 0.3567 | 0.3862 | 0.1783 | 0.1501 | 0.0946 | 0.0588 |
| covid_safety_hiv_aids | 0.1604 | 0.3547 | 0.0702 | 0.2993 | 0.0076 | 0.0533 |
| dsp_wavelets | 0.1245 | 0.1577 | 0.0728 | 0.0791 | 0.0000 | 0.0000 |
| electroculture | 0.0892 | 0.2333 | 0.0635 | 0.2119 | 0.0002 | 0.0019 |
| emoji_game | 0.1515 | 0.1117 | 0.1038 | 0.0806 | 0.0023 | 0.0001 |
| game_degree_guess | 0.1891 | 0.4330 | 0.1006 | 0.2108 | 0.0048 | 0.1302 |
| game_twenty_questions | 0.1354 | 0.1918 | 0.0771 | 0.1120 | 0.0003 | 0.0025 |
| geography_belgium | 0.3109 | 0.6798 | 0.1329 | 0.5853 | 0.0573 | 0.3591 |
| humanity_future_150y | 0.3412 | 0.4418 | 0.2547 | 0.3886 | 0.0324 | 0.0825 |
| indian_astrology | 0.1591 | 0.3579 | 0.0829 | 0.2640 | 0.0016 | 0.1511 |
| indian_history | 0.1420 | 0.6154 | 0.0966 | 0.4497 | 0.0320 | 0.3668 |
| indian_legal | 0.2342 | 0.6822 | 0.1155 | 0.6173 | 0.0279 | 0.4208 |
| indian_legal_family | 0.1410 | 0.3434 | 0.0832 | 0.2144 | 0.0017 | 0.0289 |
| jokes | 0.3048 | 0.6551 | 0.1628 | 0.5226 | 0.0869 | 0.4192 |
| karnataka_elections | 0.2515 | 0.3884 | 0.1304 | 0.2810 | 0.0356 | 0.1337 |
| linux_audio | 0.3791 | 0.4970 | 0.1954 | 0.3550 | 0.0843 | 0.1389 |
| literature_camus | 0.2144 | 0.3049 | 0.1067 | 0.2587 | 0.0068 | 0.0100 |
| llm_knowledge | 0.3093 | 0.2710 | 0.1494 | 0.1492 | 0.0532 | 0.0126 |
| logic_puzzle | 0.2775 | 0.7113 | 0.1659 | 0.5798 | 0.0304 | 0.4504 |
| lsat_medical_conference | 0.1429 | 0.7286 | 0.0772 | 0.5771 | 0.0211 | 0.4980 |
| lsat_product_codes | 0.1284 | 0.2628 | 0.0840 | 0.2416 | 0.0019 | 0.0061 |
| medical_dsd | 0.2218 | 0.6041 | 0.0988 | 0.3196 | 0.0055 | 0.2674 |
| personas_roleplay | 0.2727 | 0.4322 | 0.1096 | 0.1648 | 0.0444 | 0.1509 |
| physics_cosmology | 0.3249 | 0.6305 | 0.1861 | 0.4972 | 0.1455 | 0.3288 |
| physics_violin_nanoscale | 0.3377 | 0.1142 | 0.1876 | 0.0913 | 0.0881 | 0.0007 |
| scifi_films | 0.2909 | 0.2210 | 0.1211 | 0.1099 | 0.0328 | 0.0065 |
| scifi_films_hal9000 | 0.1155 | 0.3492 | 0.0878 | 0.1637 | 0.0120 | 0.0741 |
| scifi_films_hal9000_games | 0.1543 | 0.3055 | 0.0874 | 0.1468 | 0.0110 | 0.0420 |
| scifi_films_liu_cixin | 0.2654 | 0.2099 | 0.1503 | 0.1125 | 0.0249 | 0.0205 |
| therapy | 0.2608 | 0.3848 | 0.1365 | 0.3266 | 0.0232 | 0.1376 |
| therapy_manipulation | 0.2090 | 0.3110 | 0.1061 | 0.2736 | 0.0086 | 0.0146 |
| wildfires_alberta | 0.2067 | 0.4619 | 0.1348 | 0.4571 | 0.0249 | 0.1150 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 36 topics
- 🔵 **Baseline wins**: 6 topics
- 🟡 **Ties (±0.01)**: 1 topics
