# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 40)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.1503 | 0.3918 | **+160.6%** |
| **Avg ROUGE-L (F1)** | 0.0878 | 0.2624 | **+198.9%** |
| **Avg BLEU-2** | 0.0234 | 0.1206 | **+415.6%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 324171 | 310617 | - |
| **Avg Tokens per Probe** | 7539 | 7224 | - |
| **Total Probe Latency** | 1888.5s | 2288.3s | - |
| **Avg Probe Latency** | 43.92s | 53.22s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.1798 | 0.3985 | 0.0986 | 0.2798 | 0.0010 | 0.0507 |
| ai_consciousness | 0.3008 | 0.3789 | 0.2061 | 0.2197 | 0.0140 | 0.0447 |
| ai_consciousness_friendship | 0.4514 | 0.5257 | 0.2069 | 0.3204 | 0.1491 | 0.1902 |
| ai_meta | 0.2917 | 0.3237 | 0.1329 | 0.1871 | 0.0171 | 0.0212 |
| bhutan_travel | 0.2375 | 0.3178 | 0.1625 | 0.2877 | 0.0194 | 0.0137 |
| chess | 0.2119 | 0.3994 | 0.0984 | 0.1895 | 0.0072 | 0.0664 |
| child_nutrition | 0.0932 | 0.1436 | 0.0529 | 0.0764 | 0.0000 | 0.0001 |
| cookies_recipe_halving | 0.2761 | 0.4919 | 0.1448 | 0.3573 | 0.0225 | 0.1917 |
| cookies_recipe_halving_argument | 0.0746 | 0.5483 | 0.0672 | 0.3133 | 0.0000 | 0.2352 |
| cookies_recipe_halving_corrections | 0.4712 | 0.6383 | 0.2670 | 0.4113 | 0.2178 | 0.3684 |
| cookies_recipe_halving_math_errors | 0.0625 | 0.6711 | 0.0573 | 0.4430 | 0.0000 | 0.3860 |
| covid_safety | 0.0105 | 0.0278 | 0.0105 | 0.0232 | 0.0000 | 0.0000 |
| covid_safety_hiv_aids | 0.0425 | 0.1702 | 0.0243 | 0.0947 | 0.0000 | 0.0039 |
| dsp_wavelets | 0.1619 | 0.1412 | 0.0813 | 0.1045 | 0.0002 | 0.0000 |
| electroculture | 0.0274 | 0.4615 | 0.0229 | 0.2418 | 0.0000 | 0.0969 |
| emoji_game | 0.1935 | 0.3711 | 0.1505 | 0.3286 | 0.0210 | 0.0531 |
| game_degree_guess | 0.2832 | 0.4530 | 0.1358 | 0.3328 | 0.0235 | 0.1251 |
| game_twenty_questions | 0.0848 | 0.2668 | 0.0633 | 0.1783 | 0.0000 | 0.0155 |
| geography_belgium | 0.0315 | 0.4696 | 0.0210 | 0.3000 | 0.0000 | 0.2922 |
| humanity_future_150y | 0.1046 | 0.5148 | 0.0624 | 0.4598 | 0.0000 | 0.1271 |
| indian_astrology | 0.0158 | 0.3860 | 0.0095 | 0.3465 | 0.0000 | 0.0615 |
| indian_history | 0.0348 | 0.6828 | 0.0348 | 0.3724 | 0.0000 | 0.4438 |
| indian_legal | 0.3042 | 0.4163 | 0.1458 | 0.2881 | 0.0632 | 0.0603 |
| indian_legal_family | 0.0952 | 0.0862 | 0.0714 | 0.0682 | 0.0010 | 0.0000 |
| jokes | 0.2323 | 0.6625 | 0.1333 | 0.4984 | 0.0369 | 0.3528 |
| karnataka_elections | 0.0519 | 0.5620 | 0.0461 | 0.4147 | 0.0000 | 0.2861 |
| linux_audio | 0.4551 | 0.5430 | 0.1993 | 0.2921 | 0.1563 | 0.2753 |
| literature_camus | 0.2259 | 0.1739 | 0.1146 | 0.1234 | 0.0110 | 0.0002 |
| llm_knowledge | 0.0167 | 0.2689 | 0.0167 | 0.1974 | 0.0000 | 0.0052 |
| logic_puzzle | 0.2595 | 0.5215 | 0.1628 | 0.2893 | 0.0554 | 0.1900 |
| lsat_medical_conference | 0.0389 | 0.5687 | 0.0278 | 0.5375 | 0.0000 | 0.2213 |
| lsat_product_codes | 0.0091 | 0.0149 | 0.0079 | 0.0081 | 0.0000 | 0.0000 |
| medical_dsd | 0.1636 | 0.4150 | 0.1273 | 0.2916 | 0.0066 | 0.0716 |
| personas_roleplay | 0.0453 | 0.3707 | 0.0302 | 0.2356 | 0.0000 | 0.0639 |
| physics_cosmology | 0.3599 | 0.2720 | 0.2271 | 0.2184 | 0.1576 | 0.0117 |
| physics_violin_nanoscale | 0.0645 | 0.3710 | 0.0323 | 0.2039 | 0.0000 | 0.1243 |
| scifi_films | 0.0216 | 0.3197 | 0.0108 | 0.2211 | 0.0000 | 0.0162 |
| scifi_films_hal9000 | 0.2787 | 0.5191 | 0.1434 | 0.2977 | 0.0251 | 0.2024 |
| scifi_films_hal9000_games | 0.0868 | 0.3407 | 0.0615 | 0.2044 | 0.0000 | 0.0264 |
| scifi_films_liu_cixin | 0.0361 | 0.5776 | 0.0301 | 0.3448 | 0.0000 | 0.3287 |
| therapy | 0.0187 | 0.1756 | 0.0187 | 0.1311 | 0.0000 | 0.0004 |
| therapy_manipulation | 0.0424 | 0.5239 | 0.0424 | 0.2374 | 0.0000 | 0.1329 |
| wildfires_alberta | 0.0171 | 0.3627 | 0.0146 | 0.3116 | 0.0000 | 0.0291 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 38 topics
- 🔵 **Baseline wins**: 3 topics
- 🟡 **Ties (±0.01)**: 2 topics
