# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 20)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.2925 | 0.4066 | **+39.0%** |
| **Avg ROUGE-L (F1)** | 0.1743 | 0.2758 | **+58.2%** |
| **Avg BLEU-2** | 0.0609 | 0.1163 | **+91.1%** |

| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 316610 | 265083 | - |
| **Total Probe Latency** | 2795.6s | 2777.9s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.2125 | 0.3163 | 0.1092 | 0.1432 | 0.0074 | 0.0356 |
| ai_consciousness | 0.2749 | 0.3005 | 0.1529 | 0.1693 | 0.0073 | 0.0108 |
| ai_consciousness_friendship | 0.3262 | 0.4276 | 0.1426 | 0.2897 | 0.0215 | 0.0754 |
| ai_meta | 0.2526 | 0.3215 | 0.1225 | 0.1314 | 0.0081 | 0.0267 |
| bhutan_travel | 0.3100 | 0.4419 | 0.2644 | 0.4227 | 0.0063 | 0.0607 |
| chess | 0.3082 | 0.3269 | 0.1388 | 0.2011 | 0.0390 | 0.0133 |
| child_nutrition | 0.3367 | 0.2687 | 0.1816 | 0.2179 | 0.0221 | 0.0064 |
| cookies_recipe_halving | 0.3297 | 0.4988 | 0.1418 | 0.3658 | 0.0501 | 0.2049 |
| cookies_recipe_halving_argument | 0.6242 | 0.5826 | 0.3253 | 0.3119 | 0.3800 | 0.2945 |
| cookies_recipe_halving_corrections | 0.4649 | 0.5734 | 0.2725 | 0.3532 | 0.1546 | 0.2866 |
| cookies_recipe_halving_math_errors | 0.4682 | 0.5348 | 0.2197 | 0.3857 | 0.1425 | 0.2154 |
| covid_safety | 0.1367 | 0.3359 | 0.1300 | 0.2274 | 0.0000 | 0.0185 |
| covid_safety_hiv_aids | 0.2041 | 0.2365 | 0.1617 | 0.1755 | 0.0017 | 0.0041 |
| dsp_wavelets | 0.0055 | 0.1013 | 0.0044 | 0.0734 | 0.0000 | 0.0000 |
| electroculture | 0.2615 | 0.2804 | 0.2405 | 0.2084 | 0.0048 | 0.0073 |
| emoji_game | 0.0840 | 0.1565 | 0.0610 | 0.1194 | 0.0000 | 0.0001 |
| game_degree_guess | 0.1552 | 0.6954 | 0.0975 | 0.5492 | 0.0003 | 0.4915 |
| game_twenty_questions | 0.2534 | 0.1462 | 0.1416 | 0.1038 | 0.0150 | 0.0002 |
| geography_belgium | 0.4753 | 0.1859 | 0.3247 | 0.0929 | 0.2381 | 0.0021 |
| humanity_future_150y | 0.4532 | 0.4071 | 0.4474 | 0.2022 | 0.0857 | 0.0594 |
| indian_astrology | 0.3002 | 0.3627 | 0.1609 | 0.3327 | 0.0169 | 0.0355 |
| indian_history | 0.2946 | 0.4246 | 0.2326 | 0.2523 | 0.0434 | 0.1902 |
| indian_legal | 0.3878 | 0.5073 | 0.2235 | 0.3993 | 0.0825 | 0.1382 |
| indian_legal_family | 0.4940 | 0.3589 | 0.4127 | 0.1747 | 0.1307 | 0.0308 |
| jokes | 0.2678 | 0.6253 | 0.1421 | 0.4806 | 0.0077 | 0.3651 |
| karnataka_elections | 0.5668 | 0.5610 | 0.3811 | 0.3833 | 0.2679 | 0.2819 |
| linux_audio | 0.3631 | 0.5429 | 0.1789 | 0.3099 | 0.0734 | 0.1960 |
| literature_camus | 0.1143 | 0.3454 | 0.0648 | 0.1938 | 0.0001 | 0.0240 |
| llm_knowledge | 0.2547 | 0.3100 | 0.1258 | 0.1934 | 0.0080 | 0.0120 |
| logic_puzzle | 0.2500 | 0.6466 | 0.1434 | 0.4932 | 0.0367 | 0.3572 |
| lsat_medical_conference | 0.4105 | 0.5973 | 0.2824 | 0.5566 | 0.1044 | 0.2523 |
| lsat_product_codes | 0.0105 | 0.1935 | 0.0105 | 0.1732 | 0.0000 | 0.0004 |
| medical_dsd | 0.3622 | 0.4789 | 0.1715 | 0.2772 | 0.0498 | 0.1332 |
| personas_roleplay | 0.3156 | 0.3671 | 0.1338 | 0.2055 | 0.0372 | 0.0890 |
| physics_cosmology | 0.3684 | 0.5492 | 0.1967 | 0.4197 | 0.1663 | 0.1886 |
| physics_violin_nanoscale | 0.3949 | 0.6451 | 0.2215 | 0.3113 | 0.1281 | 0.3309 |
| scifi_films | 0.2379 | 0.3385 | 0.1059 | 0.2660 | 0.0087 | 0.0202 |
| scifi_films_hal9000 | 0.3533 | 0.4288 | 0.1587 | 0.2111 | 0.0991 | 0.1242 |
| scifi_films_hal9000_games | 0.0639 | 0.2830 | 0.0447 | 0.2137 | 0.0000 | 0.0071 |
| scifi_films_liu_cixin | 0.4174 | 0.5437 | 0.2140 | 0.4284 | 0.1118 | 0.1984 |
| therapy | 0.0154 | 0.3067 | 0.0103 | 0.2558 | 0.0000 | 0.0121 |
| therapy_manipulation | 0.0159 | 0.5423 | 0.0123 | 0.3459 | 0.0000 | 0.1713 |
| wildfires_alberta | 0.3828 | 0.3852 | 0.1879 | 0.2377 | 0.0603 | 0.0298 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 35 topics
- 🔵 **Baseline wins**: 6 topics
- 🟡 **Ties (±0.01)**: 2 topics
