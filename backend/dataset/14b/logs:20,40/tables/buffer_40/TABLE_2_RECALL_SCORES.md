# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 40)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.1745 | 0.3725 | **+113.5%** |
| **Avg ROUGE-L (F1)** | 0.0997 | 0.2648 | **+165.5%** |
| **Avg BLEU-2** | 0.0182 | 0.1315 | **+622.1%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 359355 | 304196 | - |
| **Avg Tokens per Probe** | 8357 | 7074 | - |
| **Total Probe Latency** | 943.7s | 957.3s | - |
| **Avg Probe Latency** | 21.95s | 22.26s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.2542 | 0.4631 | 0.1134 | 0.2548 | 0.0184 | 0.0926 |
| ai_consciousness | 0.2873 | 0.4522 | 0.1205 | 0.4032 | 0.0131 | 0.0875 |
| ai_consciousness_friendship | 0.4393 | 0.6308 | 0.2401 | 0.3135 | 0.0917 | 0.3078 |
| ai_meta | 0.3800 | 0.2896 | 0.1458 | 0.1805 | 0.0685 | 0.0125 |
| bhutan_travel | 0.0536 | 0.3580 | 0.0383 | 0.3128 | 0.0000 | 0.0237 |
| chess | 0.1699 | 0.0541 | 0.0949 | 0.0461 | 0.0008 | 0.0000 |
| child_nutrition | 0.0636 | 0.2512 | 0.0430 | 0.2077 | 0.0000 | 0.0055 |
| cookies_recipe_halving | 0.1142 | 0.5869 | 0.0803 | 0.4820 | 0.0001 | 0.2447 |
| cookies_recipe_halving_argument | 0.2657 | 0.4026 | 0.1538 | 0.2468 | 0.0037 | 0.0972 |
| cookies_recipe_halving_corrections | 0.1986 | 0.5100 | 0.1206 | 0.3152 | 0.0035 | 0.1989 |
| cookies_recipe_halving_math_errors | 0.2765 | 0.5876 | 0.1415 | 0.4068 | 0.0161 | 0.2211 |
| covid_safety | 0.2076 | 0.0042 | 0.0908 | 0.0042 | 0.0018 | 0.0000 |
| covid_safety_hiv_aids | 0.2060 | 0.2313 | 0.1166 | 0.1349 | 0.0007 | 0.0150 |
| dsp_wavelets | 0.0733 | 0.1285 | 0.0520 | 0.0940 | 0.0000 | 0.0000 |
| electroculture | 0.1112 | 0.5948 | 0.0748 | 0.5302 | 0.0000 | 0.2963 |
| emoji_game | 0.1229 | 0.2469 | 0.1102 | 0.2147 | 0.0016 | 0.0413 |
| game_degree_guess | 0.1608 | 0.2519 | 0.0863 | 0.1679 | 0.0013 | 0.0096 |
| game_twenty_questions | 0.0856 | 0.2444 | 0.0589 | 0.1881 | 0.0000 | 0.0042 |
| geography_belgium | 0.2201 | 0.2827 | 0.1292 | 0.1538 | 0.0046 | 0.1007 |
| humanity_future_150y | 0.0386 | 0.4494 | 0.0305 | 0.4226 | 0.0000 | 0.0976 |
| indian_astrology | 0.1135 | 0.6588 | 0.0922 | 0.4461 | 0.0031 | 0.3342 |
| indian_history | 0.1823 | 0.7525 | 0.1042 | 0.4746 | 0.0173 | 0.6198 |
| indian_legal | 0.2462 | 0.3847 | 0.1343 | 0.2621 | 0.0506 | 0.0437 |
| indian_legal_family | 0.1333 | 0.0503 | 0.1079 | 0.0294 | 0.0069 | 0.0000 |
| jokes | 0.2451 | 0.7034 | 0.1383 | 0.6667 | 0.0361 | 0.5080 |
| karnataka_elections | 0.1667 | 0.6508 | 0.1190 | 0.4190 | 0.0061 | 0.3900 |
| linux_audio | 0.4132 | 0.5544 | 0.2369 | 0.2280 | 0.1654 | 0.2537 |
| literature_camus | 0.0444 | 0.0279 | 0.0317 | 0.0259 | 0.0000 | 0.0000 |
| llm_knowledge | 0.0665 | 0.3344 | 0.0463 | 0.2121 | 0.0000 | 0.0341 |
| logic_puzzle | 0.1748 | 0.6639 | 0.1100 | 0.4844 | 0.0040 | 0.3404 |
| lsat_medical_conference | 0.0993 | 0.4019 | 0.0722 | 0.3690 | 0.0009 | 0.0542 |
| lsat_product_codes | 0.1023 | 0.0164 | 0.0671 | 0.0104 | 0.0001 | 0.0000 |
| medical_dsd | 0.2974 | 0.0194 | 0.1250 | 0.0194 | 0.0757 | 0.0000 |
| personas_roleplay | 0.2355 | 0.4390 | 0.1038 | 0.3039 | 0.0160 | 0.1076 |
| physics_cosmology | 0.0532 | 0.4037 | 0.0380 | 0.3421 | 0.0000 | 0.0571 |
| physics_violin_nanoscale | 0.3101 | 0.4575 | 0.2119 | 0.2484 | 0.0914 | 0.1320 |
| scifi_films | 0.1211 | 0.0518 | 0.0781 | 0.0345 | 0.0001 | 0.0000 |
| scifi_films_hal9000 | 0.0444 | 0.4400 | 0.0333 | 0.2050 | 0.0000 | 0.1765 |
| scifi_films_hal9000_games | 0.0856 | 0.2585 | 0.0638 | 0.1355 | 0.0000 | 0.0058 |
| scifi_films_liu_cixin | 0.0440 | 0.1220 | 0.0440 | 0.0871 | 0.0000 | 0.0000 |
| therapy | 0.1864 | 0.7239 | 0.1017 | 0.5654 | 0.0052 | 0.5191 |
| therapy_manipulation | 0.0340 | 0.5561 | 0.0212 | 0.4634 | 0.0000 | 0.2028 |
| wildfires_alberta | 0.3733 | 0.3257 | 0.1659 | 0.2733 | 0.0783 | 0.0182 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 34 topics
- 🔵 **Baseline wins**: 9 topics
- 🟡 **Ties (±0.01)**: 0 topics
