# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 10)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.3378 | 0.4201 | **+24.4%** |
| **Avg ROUGE-L (F1)** | 0.1982 | 0.3211 | **+62.0%** |
| **Avg BLEU-2** | 0.0870 | 0.1338 | **+53.8%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 274209 | 156136 | - |
| **Avg Tokens per Probe** | 6377 | 3631 | - |
| **Total Probe Latency** | 1441.6s | 997.1s | - |
| **Avg Probe Latency** | 33.53s | 23.19s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.2399 | 0.3234 | 0.1087 | 0.2196 | 0.0102 | 0.0287 |
| ai_consciousness | 0.2393 | 0.3708 | 0.1288 | 0.2334 | 0.0045 | 0.0333 |
| ai_consciousness_friendship | 0.3854 | 0.4820 | 0.1622 | 0.3122 | 0.0638 | 0.1361 |
| ai_meta | 0.2553 | 0.2653 | 0.1259 | 0.1628 | 0.0134 | 0.0057 |
| bhutan_travel | 0.3620 | 0.3455 | 0.3182 | 0.2964 | 0.0283 | 0.0194 |
| chess | 0.2136 | 0.3079 | 0.1048 | 0.1851 | 0.0004 | 0.0133 |
| child_nutrition | 0.0645 | 0.2653 | 0.0409 | 0.2027 | 0.0000 | 0.0092 |
| cookies_recipe_halving | 0.4463 | 0.8304 | 0.1980 | 0.7435 | 0.1781 | 0.6779 |
| cookies_recipe_halving_argument | 0.5782 | 0.4190 | 0.3050 | 0.2413 | 0.2869 | 0.1026 |
| cookies_recipe_halving_corrections | 0.5455 | 0.5422 | 0.3192 | 0.3675 | 0.2562 | 0.2130 |
| cookies_recipe_halving_math_errors | 0.5022 | 0.4317 | 0.2496 | 0.2620 | 0.2590 | 0.1573 |
| covid_safety | 0.3711 | 0.4786 | 0.2742 | 0.3512 | 0.0353 | 0.1091 |
| covid_safety_hiv_aids | 0.2669 | 0.3147 | 0.1054 | 0.2201 | 0.0379 | 0.0197 |
| dsp_wavelets | 0.1425 | 0.1574 | 0.0757 | 0.1204 | 0.0000 | 0.0000 |
| electroculture | 0.3299 | 0.2496 | 0.2919 | 0.2017 | 0.0182 | 0.0029 |
| emoji_game | 0.2237 | 0.2578 | 0.1311 | 0.1828 | 0.0136 | 0.0112 |
| game_degree_guess | 0.2967 | 0.7091 | 0.1332 | 0.5280 | 0.0688 | 0.5187 |
| game_twenty_questions | 0.2496 | 0.1376 | 0.1342 | 0.0894 | 0.0201 | 0.0000 |
| geography_belgium | 0.6166 | 0.1516 | 0.2951 | 0.0831 | 0.3481 | 0.0005 |
| humanity_future_150y | 0.4989 | 0.4812 | 0.4883 | 0.4742 | 0.1447 | 0.1311 |
| indian_astrology | 0.3511 | 0.2678 | 0.1778 | 0.2448 | 0.0325 | 0.0047 |
| indian_history | 0.1754 | 0.6824 | 0.1345 | 0.5405 | 0.0199 | 0.5262 |
| indian_legal | 0.3074 | 0.4966 | 0.1292 | 0.4139 | 0.0552 | 0.1386 |
| indian_legal_family | 0.2607 | 0.4029 | 0.1326 | 0.3534 | 0.0298 | 0.0545 |
| jokes | 0.1844 | 0.5936 | 0.1206 | 0.5342 | 0.0050 | 0.3503 |
| karnataka_elections | 0.4810 | 0.4940 | 0.2262 | 0.3333 | 0.2206 | 0.1681 |
| linux_audio | 0.7342 | 0.6992 | 0.7167 | 0.6527 | 0.4696 | 0.4476 |
| literature_camus | 0.2500 | 0.4397 | 0.1101 | 0.3838 | 0.0130 | 0.0879 |
| llm_knowledge | 0.3287 | 0.3081 | 0.1389 | 0.2165 | 0.0460 | 0.0132 |
| logic_puzzle | 0.3003 | 0.3687 | 0.1769 | 0.2723 | 0.0471 | 0.0371 |
| lsat_medical_conference | 0.4831 | 0.6859 | 0.2928 | 0.6005 | 0.1947 | 0.4022 |
| lsat_product_codes | 0.1917 | 0.2729 | 0.1362 | 0.2356 | 0.0013 | 0.0066 |
| medical_dsd | 0.3853 | 0.4140 | 0.2873 | 0.3283 | 0.0469 | 0.0643 |
| personas_roleplay | 0.3127 | 0.3097 | 0.1406 | 0.2312 | 0.0471 | 0.0209 |
| physics_cosmology | 0.3138 | 0.4839 | 0.1854 | 0.3320 | 0.1219 | 0.1819 |
| physics_violin_nanoscale | 0.3249 | 0.3952 | 0.1987 | 0.1949 | 0.0999 | 0.1477 |
| scifi_films | 0.2421 | 0.3645 | 0.1135 | 0.2689 | 0.0177 | 0.0374 |
| scifi_films_hal9000 | 0.3003 | 0.4535 | 0.1360 | 0.3012 | 0.0844 | 0.1199 |
| scifi_films_hal9000_games | 0.2326 | 0.2776 | 0.1121 | 0.1506 | 0.0238 | 0.0123 |
| scifi_films_liu_cixin | 0.3933 | 0.5158 | 0.2050 | 0.4087 | 0.1438 | 0.2035 |
| therapy | 0.3125 | 0.6585 | 0.1364 | 0.5528 | 0.0605 | 0.3061 |
| therapy_manipulation | 0.4803 | 0.4704 | 0.3704 | 0.3949 | 0.1180 | 0.0954 |
| wildfires_alberta | 0.3505 | 0.4897 | 0.1525 | 0.3827 | 0.0564 | 0.1378 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 30 topics
- 🔵 **Baseline wins**: 10 topics
- 🟡 **Ties (±0.01)**: 3 topics
