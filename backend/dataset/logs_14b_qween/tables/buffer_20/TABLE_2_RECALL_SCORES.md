# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 20)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.2440 | 0.3924 | **+60.8%** |
| **Avg ROUGE-L (F1)** | 0.1199 | 0.2921 | **+143.6%** |
| **Avg BLEU-2** | 0.0455 | 0.1007 | **+121.3%** |

| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 342216 | 258275 | - |
| **Total Probe Latency** | 1216.9s | 1056.4s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.3396 | 0.2875 | 0.1362 | 0.1991 | 0.0468 | 0.0103 |
| ai_consciousness | 0.3098 | 0.3192 | 0.1409 | 0.1815 | 0.0202 | 0.0218 |
| ai_consciousness_friendship | 0.4961 | 0.3936 | 0.2502 | 0.2756 | 0.1303 | 0.0534 |
| ai_meta | 0.3489 | 0.2394 | 0.1277 | 0.1213 | 0.0531 | 0.0071 |
| bhutan_travel | 0.2719 | 0.4152 | 0.1410 | 0.3771 | 0.0420 | 0.0443 |
| chess | 0.3612 | 0.4277 | 0.1431 | 0.2915 | 0.0363 | 0.1046 |
| child_nutrition | 0.2817 | 0.3303 | 0.1086 | 0.2402 | 0.0195 | 0.0203 |
| cookies_recipe_halving | 0.3529 | 0.4550 | 0.1345 | 0.4013 | 0.0648 | 0.1376 |
| cookies_recipe_halving_argument | 0.0657 | 0.3920 | 0.0584 | 0.2658 | 0.0000 | 0.0502 |
| cookies_recipe_halving_corrections | 0.2067 | 0.5673 | 0.1229 | 0.3558 | 0.0070 | 0.2718 |
| cookies_recipe_halving_math_errors | 0.0621 | 0.5123 | 0.0395 | 0.2865 | 0.0000 | 0.1968 |
| covid_safety | 0.3198 | 0.3592 | 0.1518 | 0.2851 | 0.0196 | 0.0323 |
| covid_safety_hiv_aids | 0.2133 | 0.3164 | 0.0959 | 0.2326 | 0.0060 | 0.0283 |
| dsp_wavelets | 0.1657 | 0.1415 | 0.0810 | 0.1012 | 0.0001 | 0.0000 |
| electroculture | 0.2367 | 0.3042 | 0.1170 | 0.2896 | 0.0049 | 0.0123 |
| emoji_game | 0.0528 | 0.1851 | 0.0435 | 0.1718 | 0.0000 | 0.0014 |
| game_degree_guess | 0.2913 | 0.7666 | 0.1146 | 0.7249 | 0.0357 | 0.5637 |
| game_twenty_questions | 0.2764 | 0.2360 | 0.1539 | 0.1714 | 0.0251 | 0.0067 |
| geography_belgium | 0.3751 | 0.3161 | 0.1834 | 0.1945 | 0.0943 | 0.0233 |
| humanity_future_150y | 0.0178 | 0.4768 | 0.0143 | 0.4645 | 0.0000 | 0.1257 |
| indian_astrology | 0.1053 | 0.2449 | 0.0683 | 0.2090 | 0.0000 | 0.0033 |
| indian_history | 0.1853 | 0.3802 | 0.1144 | 0.2510 | 0.0177 | 0.2029 |
| indian_legal | 0.3151 | 0.4851 | 0.1306 | 0.3807 | 0.0461 | 0.1237 |
| indian_legal_family | 0.3601 | 0.3759 | 0.1897 | 0.2814 | 0.1113 | 0.0435 |
| jokes | 0.2460 | 0.5438 | 0.1462 | 0.4608 | 0.0420 | 0.2558 |
| karnataka_elections | 0.0371 | 0.4637 | 0.0304 | 0.3419 | 0.0000 | 0.1419 |
| linux_audio | 0.5000 | 0.2792 | 0.2029 | 0.1574 | 0.1736 | 0.0142 |
| literature_camus | 0.2244 | 0.3432 | 0.1036 | 0.2394 | 0.0091 | 0.0216 |
| llm_knowledge | 0.3190 | 0.3059 | 0.1336 | 0.2285 | 0.0412 | 0.0127 |
| logic_puzzle | 0.2572 | 0.5317 | 0.1378 | 0.3720 | 0.0447 | 0.1725 |
| lsat_medical_conference | 0.0305 | 0.5897 | 0.0203 | 0.5224 | 0.0000 | 0.2754 |
| lsat_product_codes | 0.0081 | 0.2649 | 0.0081 | 0.2326 | 0.0000 | 0.0055 |
| medical_dsd | 0.0206 | 0.4656 | 0.0144 | 0.2672 | 0.0000 | 0.1024 |
| personas_roleplay | 0.2792 | 0.2033 | 0.1208 | 0.1016 | 0.0406 | 0.0057 |
| physics_cosmology | 0.0404 | 0.6232 | 0.0269 | 0.5619 | 0.0000 | 0.3364 |
| physics_violin_nanoscale | 0.6696 | 0.3502 | 0.4758 | 0.1919 | 0.4797 | 0.0465 |
| scifi_films | 0.2941 | 0.3824 | 0.1239 | 0.3322 | 0.0263 | 0.0431 |
| scifi_films_hal9000 | 0.3159 | 0.3716 | 0.1393 | 0.1621 | 0.0601 | 0.1260 |
| scifi_films_hal9000_games | 0.1987 | 0.1857 | 0.1145 | 0.1179 | 0.0099 | 0.0006 |
| scifi_films_liu_cixin | 0.4377 | 0.5899 | 0.2328 | 0.5106 | 0.1804 | 0.2947 |
| therapy | 0.3050 | 0.4833 | 0.1352 | 0.3211 | 0.0443 | 0.1277 |
| therapy_manipulation | 0.0191 | 0.4890 | 0.0121 | 0.4566 | 0.0000 | 0.1398 |
| wildfires_alberta | 0.2770 | 0.4780 | 0.1165 | 0.2280 | 0.0238 | 0.1211 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 31 topics
- 🔵 **Baseline wins**: 11 topics
- 🟡 **Ties (±0.01)**: 1 topics
