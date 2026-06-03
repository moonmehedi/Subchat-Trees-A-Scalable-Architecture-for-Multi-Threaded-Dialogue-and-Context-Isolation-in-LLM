# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 10)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.2369 | 0.4094 | **+72.8%** |
| **Avg ROUGE-L (F1)** | 0.1349 | 0.3097 | **+129.5%** |
| **Avg BLEU-2** | 0.0324 | 0.1259 | **+288.4%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 252519 | 188722 | - |
| **Avg Tokens per Probe** | 5873 | 4389 | - |
| **Total Probe Latency** | 814.8s | 776.9s | - |
| **Avg Probe Latency** | 18.95s | 18.07s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.2410 | 0.2101 | 0.1480 | 0.0922 | 0.0131 | 0.0100 |
| ai_consciousness | 0.1501 | 0.2671 | 0.0746 | 0.1786 | 0.0001 | 0.0053 |
| ai_consciousness_friendship | 0.2495 | 0.4639 | 0.1083 | 0.3138 | 0.0126 | 0.1082 |
| ai_meta | 0.2994 | 0.3636 | 0.1465 | 0.2466 | 0.0201 | 0.0341 |
| bhutan_travel | 0.1547 | 0.4433 | 0.0889 | 0.3488 | 0.0030 | 0.0650 |
| chess | 0.1864 | 0.5036 | 0.0993 | 0.4331 | 0.0044 | 0.2899 |
| child_nutrition | 0.2113 | 0.2341 | 0.0999 | 0.1448 | 0.0112 | 0.0058 |
| cookies_recipe_halving | 0.4431 | 0.5997 | 0.3096 | 0.4749 | 0.1880 | 0.3241 |
| cookies_recipe_halving_argument | 0.3927 | 0.4427 | 0.2024 | 0.2710 | 0.1045 | 0.1009 |
| cookies_recipe_halving_corrections | 0.3301 | 0.6345 | 0.2300 | 0.4655 | 0.0508 | 0.3583 |
| cookies_recipe_halving_math_errors | 0.4259 | 0.6610 | 0.2630 | 0.5428 | 0.1414 | 0.4137 |
| covid_safety | 0.2496 | 0.3871 | 0.1110 | 0.2979 | 0.0088 | 0.0487 |
| covid_safety_hiv_aids | 0.2304 | 0.1854 | 0.1130 | 0.1440 | 0.0166 | 0.0015 |
| dsp_wavelets | 0.1007 | 0.1582 | 0.0597 | 0.0910 | 0.0000 | 0.0000 |
| electroculture | 0.1120 | 0.2422 | 0.0744 | 0.2382 | 0.0001 | 0.0024 |
| emoji_game | 0.1811 | 0.2156 | 0.1274 | 0.1540 | 0.0057 | 0.0155 |
| game_degree_guess | 0.2290 | 0.5918 | 0.1279 | 0.4014 | 0.0337 | 0.3565 |
| game_twenty_questions | 0.2139 | 0.2957 | 0.1262 | 0.1632 | 0.0060 | 0.0107 |
| geography_belgium | 0.3982 | 0.5222 | 0.1663 | 0.4182 | 0.0846 | 0.1555 |
| humanity_future_150y | 0.2256 | 0.4732 | 0.1213 | 0.4630 | 0.0117 | 0.1073 |
| indian_astrology | 0.1761 | 0.2527 | 0.0999 | 0.2097 | 0.0021 | 0.0043 |
| indian_history | 0.1211 | 0.5679 | 0.0895 | 0.3580 | 0.0041 | 0.3288 |
| indian_legal | 0.2560 | 0.4519 | 0.1351 | 0.4182 | 0.0366 | 0.0891 |
| indian_legal_family | 0.2133 | 0.4432 | 0.1343 | 0.3735 | 0.0178 | 0.0827 |
| jokes | 0.1566 | 0.6627 | 0.1325 | 0.6209 | 0.0154 | 0.4894 |
| karnataka_elections | 0.3563 | 0.7264 | 0.1987 | 0.6430 | 0.0713 | 0.5329 |
| linux_audio | 0.3067 | 0.5253 | 0.1488 | 0.2373 | 0.0395 | 0.2167 |
| literature_camus | 0.1960 | 0.2961 | 0.0993 | 0.2663 | 0.0026 | 0.0088 |
| llm_knowledge | 0.2396 | 0.3205 | 0.1125 | 0.1700 | 0.0095 | 0.0167 |
| logic_puzzle | 0.0833 | 0.6097 | 0.0702 | 0.5306 | 0.0145 | 0.2920 |
| lsat_medical_conference | 0.1687 | 0.4985 | 0.1139 | 0.4758 | 0.0504 | 0.1472 |
| lsat_product_codes | 0.1806 | 0.2555 | 0.1213 | 0.2247 | 0.0164 | 0.0035 |
| medical_dsd | 0.1549 | 0.3869 | 0.0896 | 0.2373 | 0.0032 | 0.0567 |
| personas_roleplay | 0.2299 | 0.4697 | 0.1236 | 0.3371 | 0.0421 | 0.1342 |
| physics_cosmology | 0.3117 | 0.4609 | 0.2315 | 0.2868 | 0.0892 | 0.1347 |
| physics_violin_nanoscale | 0.3416 | 0.3005 | 0.2067 | 0.1897 | 0.1040 | 0.0966 |
| scifi_films | 0.2248 | 0.2548 | 0.1172 | 0.1471 | 0.0102 | 0.0030 |
| scifi_films_hal9000 | 0.2967 | 0.3358 | 0.1540 | 0.1810 | 0.0420 | 0.0844 |
| scifi_films_hal9000_games | 0.2009 | 0.2618 | 0.1112 | 0.1527 | 0.0109 | 0.0337 |
| scifi_films_liu_cixin | 0.2943 | 0.3290 | 0.1625 | 0.2857 | 0.0420 | 0.0241 |
| therapy | 0.2003 | 0.4561 | 0.1202 | 0.3894 | 0.0168 | 0.0857 |
| therapy_manipulation | 0.1898 | 0.4475 | 0.1005 | 0.3151 | 0.0078 | 0.0849 |
| wildfires_alberta | 0.2640 | 0.3957 | 0.1305 | 0.3828 | 0.0287 | 0.0488 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 40 topics
- 🔵 **Baseline wins**: 3 topics
- 🟡 **Ties (±0.01)**: 0 topics
