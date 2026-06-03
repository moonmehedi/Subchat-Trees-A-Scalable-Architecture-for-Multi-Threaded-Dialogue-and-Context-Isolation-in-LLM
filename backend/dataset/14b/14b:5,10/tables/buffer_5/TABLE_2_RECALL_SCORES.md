# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 5)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.3428 | 0.3896 | **+13.6%** |
| **Avg ROUGE-L (F1)** | 0.2179 | 0.2634 | **+20.9%** |
| **Avg BLEU-2** | 0.0967 | 0.1099 | **+13.8%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 136045 | 104023 | - |
| **Avg Tokens per Probe** | 3164 | 2419 | - |
| **Total Probe Latency** | 1155.5s | 989.8s | - |
| **Avg Probe Latency** | 26.87s | 23.02s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.2148 | 0.3284 | 0.1074 | 0.1834 | 0.0055 | 0.0352 |
| ai_consciousness | 0.3278 | 0.3130 | 0.3026 | 0.1396 | 0.0256 | 0.0166 |
| ai_consciousness_friendship | 0.4958 | 0.4367 | 0.2266 | 0.1606 | 0.1301 | 0.0978 |
| ai_meta | 0.3203 | 0.2989 | 0.1797 | 0.1663 | 0.0372 | 0.0150 |
| bhutan_travel | 0.2604 | 0.5093 | 0.1571 | 0.3628 | 0.0076 | 0.1192 |
| chess | 0.3145 | 0.3860 | 0.1331 | 0.2616 | 0.0280 | 0.0101 |
| child_nutrition | 0.0597 | 0.2338 | 0.0392 | 0.0956 | 0.0000 | 0.0088 |
| cookies_recipe_halving | 0.3681 | 0.2827 | 0.1813 | 0.1653 | 0.1018 | 0.0147 |
| cookies_recipe_halving_argument | 0.5306 | 0.4528 | 0.2857 | 0.3270 | 0.2416 | 0.1021 |
| cookies_recipe_halving_corrections | 0.4375 | 0.4103 | 0.2500 | 0.2500 | 0.1573 | 0.1257 |
| cookies_recipe_halving_math_errors | 0.3690 | 0.4563 | 0.2222 | 0.2586 | 0.0893 | 0.1331 |
| covid_safety | 0.3472 | 0.3182 | 0.1856 | 0.1316 | 0.0422 | 0.0241 |
| covid_safety_hiv_aids | 0.2908 | 0.2367 | 0.2370 | 0.1243 | 0.0247 | 0.0199 |
| dsp_wavelets | 0.1456 | 0.1837 | 0.1249 | 0.1030 | 0.0000 | 0.0003 |
| electroculture | 0.2797 | 0.1461 | 0.2510 | 0.0897 | 0.0065 | 0.0001 |
| emoji_game | 0.2098 | 0.1628 | 0.1422 | 0.1074 | 0.0153 | 0.0024 |
| game_degree_guess | 0.1818 | 0.3028 | 0.0973 | 0.1655 | 0.0025 | 0.0403 |
| game_twenty_questions | 0.1682 | 0.0996 | 0.1027 | 0.0681 | 0.0008 | 0.0000 |
| geography_belgium | 0.6840 | 0.6197 | 0.6061 | 0.4361 | 0.4252 | 0.3883 |
| humanity_future_150y | 0.6165 | 0.4975 | 0.5938 | 0.4608 | 0.2943 | 0.1373 |
| indian_astrology | 0.2555 | 0.3868 | 0.1294 | 0.2221 | 0.0052 | 0.0488 |
| indian_history | 0.3762 | 0.5625 | 0.2475 | 0.4625 | 0.1571 | 0.3048 |
| indian_legal | 0.3273 | 0.4579 | 0.1955 | 0.3175 | 0.0681 | 0.0985 |
| indian_legal_family | 0.4045 | 0.4332 | 0.3669 | 0.3946 | 0.0578 | 0.0886 |
| jokes | 0.0833 | 0.5138 | 0.0606 | 0.4266 | 0.0005 | 0.3785 |
| karnataka_elections | 0.4453 | 0.3189 | 0.3047 | 0.2054 | 0.1348 | 0.0372 |
| linux_audio | 0.7019 | 0.5343 | 0.6374 | 0.4979 | 0.4441 | 0.1668 |
| literature_camus | 0.2219 | 0.3341 | 0.0989 | 0.2334 | 0.0075 | 0.0205 |
| llm_knowledge | 0.3154 | 0.2412 | 0.1228 | 0.1216 | 0.0237 | 0.0043 |
| logic_puzzle | 0.2078 | 0.5396 | 0.1299 | 0.4075 | 0.0163 | 0.2133 |
| lsat_medical_conference | 0.3557 | 0.5696 | 0.1816 | 0.5198 | 0.0730 | 0.2202 |
| lsat_product_codes | 0.1998 | 0.2197 | 0.1199 | 0.1907 | 0.0029 | 0.0010 |
| medical_dsd | 0.3864 | 0.3557 | 0.1813 | 0.1541 | 0.0696 | 0.1232 |
| personas_roleplay | 0.3044 | 0.3812 | 0.1629 | 0.2525 | 0.0581 | 0.0466 |
| physics_cosmology | 0.5671 | 0.4351 | 0.2960 | 0.3839 | 0.3036 | 0.1249 |
| physics_violin_nanoscale | 0.7542 | 0.8120 | 0.5767 | 0.6466 | 0.6226 | 0.6431 |
| scifi_films | 0.2425 | 0.3483 | 0.1104 | 0.1826 | 0.0142 | 0.0308 |
| scifi_films_hal9000 | 0.3087 | 0.3922 | 0.1417 | 0.1905 | 0.1116 | 0.1118 |
| scifi_films_hal9000_games | 0.2065 | 0.2346 | 0.1196 | 0.1404 | 0.0155 | 0.0026 |
| scifi_films_liu_cixin | 0.4177 | 0.4797 | 0.1994 | 0.3140 | 0.1551 | 0.2025 |
| therapy | 0.3477 | 0.6481 | 0.1508 | 0.4341 | 0.0728 | 0.3720 |
| therapy_manipulation | 0.3819 | 0.3748 | 0.2596 | 0.1635 | 0.0472 | 0.0375 |
| wildfires_alberta | 0.3077 | 0.5054 | 0.1506 | 0.4087 | 0.0591 | 0.1593 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 24 topics
- 🔵 **Baseline wins**: 18 topics
- 🟡 **Ties (±0.01)**: 1 topics
