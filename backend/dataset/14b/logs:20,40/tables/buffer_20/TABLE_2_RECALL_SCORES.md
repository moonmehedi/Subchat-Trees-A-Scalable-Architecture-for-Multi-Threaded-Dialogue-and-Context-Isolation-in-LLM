# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 20)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.2476 | 0.4187 | **+69.1%** |
| **Avg ROUGE-L (F1)** | 0.1320 | 0.3143 | **+138.2%** |
| **Avg BLEU-2** | 0.0516 | 0.1237 | **+139.6%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 322902 | 269171 | - |
| **Avg Tokens per Probe** | 7509 | 6260 | - |
| **Total Probe Latency** | 1284.6s | 1196.1s | - |
| **Avg Probe Latency** | 29.87s | 27.82s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.2600 | 0.3084 | 0.1196 | 0.1834 | 0.0146 | 0.0153 |
| ai_consciousness | 0.3301 | 0.3407 | 0.2706 | 0.2488 | 0.0241 | 0.0244 |
| ai_consciousness_friendship | 0.4914 | 0.3919 | 0.2275 | 0.1939 | 0.1404 | 0.0494 |
| ai_meta | 0.2773 | 0.2542 | 0.1203 | 0.1292 | 0.0187 | 0.0049 |
| bhutan_travel | 0.2670 | 0.3578 | 0.1263 | 0.2836 | 0.0132 | 0.0234 |
| chess | 0.3286 | 0.3164 | 0.1301 | 0.2210 | 0.0528 | 0.0148 |
| child_nutrition | 0.1847 | 0.1591 | 0.0793 | 0.1155 | 0.0037 | 0.0000 |
| cookies_recipe_halving | 0.4433 | 0.5869 | 0.1873 | 0.4820 | 0.1476 | 0.2447 |
| cookies_recipe_halving_argument | 0.5882 | 0.3776 | 0.3205 | 0.2587 | 0.3142 | 0.0434 |
| cookies_recipe_halving_corrections | 0.5263 | 0.5215 | 0.3158 | 0.3954 | 0.2683 | 0.1991 |
| cookies_recipe_halving_math_errors | 0.0601 | 0.5876 | 0.0420 | 0.4068 | 0.0000 | 0.2211 |
| covid_safety | 0.3068 | 0.3505 | 0.1546 | 0.2762 | 0.0178 | 0.0283 |
| covid_safety_hiv_aids | 0.1855 | 0.2898 | 0.0940 | 0.1870 | 0.0032 | 0.0222 |
| dsp_wavelets | 0.1225 | 0.1488 | 0.0625 | 0.1038 | 0.0000 | 0.0000 |
| electroculture | 0.1563 | 0.3105 | 0.0901 | 0.2993 | 0.0002 | 0.0138 |
| emoji_game | 0.1969 | 0.1227 | 0.1205 | 0.1078 | 0.0175 | 0.0025 |
| game_degree_guess | 0.3461 | 0.7200 | 0.1336 | 0.5557 | 0.0729 | 0.4783 |
| game_twenty_questions | 0.1858 | 0.1557 | 0.1048 | 0.1123 | 0.0021 | 0.0003 |
| geography_belgium | 0.3885 | 0.6626 | 0.2500 | 0.4736 | 0.2031 | 0.3440 |
| humanity_future_150y | 0.0258 | 0.4957 | 0.0159 | 0.4769 | 0.0000 | 0.1458 |
| indian_astrology | 0.1743 | 0.3361 | 0.0890 | 0.2954 | 0.0017 | 0.0230 |
| indian_history | 0.1889 | 0.7087 | 0.1556 | 0.5827 | 0.0123 | 0.4971 |
| indian_legal | 0.2822 | 0.5000 | 0.1349 | 0.4018 | 0.0453 | 0.1413 |
| indian_legal_family | 0.0270 | 0.5334 | 0.0187 | 0.3727 | 0.0000 | 0.1683 |
| jokes | 0.1852 | 0.7105 | 0.1222 | 0.6694 | 0.0308 | 0.5097 |
| karnataka_elections | 0.1914 | 0.4581 | 0.1222 | 0.3877 | 0.0076 | 0.1458 |
| linux_audio | 0.4084 | 0.5210 | 0.2073 | 0.2093 | 0.1207 | 0.1922 |
| literature_camus | 0.2137 | 0.3065 | 0.1031 | 0.2319 | 0.0103 | 0.0127 |
| llm_knowledge | 0.3302 | 0.3605 | 0.1338 | 0.3065 | 0.0388 | 0.0337 |
| logic_puzzle | 0.2439 | 0.4073 | 0.1341 | 0.2826 | 0.0596 | 0.0719 |
| lsat_medical_conference | 0.0942 | 0.6933 | 0.0659 | 0.6392 | 0.0001 | 0.3661 |
| lsat_product_codes | 0.0222 | 0.2556 | 0.0169 | 0.2035 | 0.0000 | 0.0056 |
| medical_dsd | 0.0182 | 0.4112 | 0.0114 | 0.3270 | 0.0000 | 0.0648 |
| personas_roleplay | 0.2711 | 0.4118 | 0.1133 | 0.2762 | 0.0274 | 0.0929 |
| physics_cosmology | 0.0361 | 0.5460 | 0.0206 | 0.3658 | 0.0000 | 0.2040 |
| physics_violin_nanoscale | 0.5492 | 0.3971 | 0.4249 | 0.2249 | 0.2751 | 0.1499 |
| scifi_films | 0.2878 | 0.3446 | 0.1200 | 0.2779 | 0.0183 | 0.0215 |
| scifi_films_hal9000 | 0.2899 | 0.4344 | 0.1318 | 0.2339 | 0.0593 | 0.1071 |
| scifi_films_hal9000_games | 0.1924 | 0.2086 | 0.0929 | 0.1396 | 0.0067 | 0.0004 |
| scifi_films_liu_cixin | 0.3931 | 0.5862 | 0.2184 | 0.5081 | 0.1278 | 0.2541 |
| therapy | 0.2588 | 0.5422 | 0.1280 | 0.3222 | 0.0207 | 0.2017 |
| therapy_manipulation | 0.0119 | 0.4891 | 0.0119 | 0.4457 | 0.0000 | 0.1376 |
| wildfires_alberta | 0.3036 | 0.3812 | 0.1328 | 0.3013 | 0.0427 | 0.0407 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 34 topics
- 🔵 **Baseline wins**: 8 topics
- 🟡 **Ties (±0.01)**: 1 topics
