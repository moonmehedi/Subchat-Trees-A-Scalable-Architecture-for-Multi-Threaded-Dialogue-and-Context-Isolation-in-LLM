# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 20)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.1811 | 0.4056 | **+124.0%** |
| **Avg ROUGE-L (F1)** | 0.1016 | 0.3194 | **+214.3%** |
| **Avg BLEU-2** | 0.0205 | 0.1325 | **+547.3%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 336942 | 284817 | - |
| **Avg Tokens per Probe** | 7836 | 6624 | - |
| **Total Probe Latency** | 767.6s | 792.7s | - |
| **Avg Probe Latency** | 17.85s | 18.44s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.1660 | 0.2949 | 0.0779 | 0.1909 | 0.0034 | 0.0071 |
| ai_consciousness | 0.1476 | 0.2366 | 0.0779 | 0.1840 | 0.0010 | 0.0023 |
| ai_consciousness_friendship | 0.2624 | 0.4216 | 0.1239 | 0.3253 | 0.0331 | 0.0756 |
| ai_meta | 0.1513 | 0.2757 | 0.0798 | 0.1892 | 0.0020 | 0.0072 |
| bhutan_travel | 0.3182 | 0.0975 | 0.3094 | 0.0796 | 0.0164 | 0.0000 |
| chess | 0.2256 | 0.3418 | 0.0986 | 0.2852 | 0.0125 | 0.0463 |
| child_nutrition | 0.1610 | 0.2655 | 0.0744 | 0.2157 | 0.0015 | 0.0057 |
| cookies_recipe_halving | 0.2359 | 0.6293 | 0.1303 | 0.4829 | 0.0241 | 0.3456 |
| cookies_recipe_halving_argument | 0.2213 | 0.6188 | 0.1270 | 0.4094 | 0.0232 | 0.3317 |
| cookies_recipe_halving_corrections | 0.0661 | 0.6736 | 0.0555 | 0.3473 | 0.0000 | 0.4033 |
| cookies_recipe_halving_math_errors | 0.0911 | 0.6458 | 0.0771 | 0.5432 | 0.0000 | 0.3792 |
| covid_safety | 0.2354 | 0.0880 | 0.1050 | 0.0773 | 0.0100 | 0.0000 |
| covid_safety_hiv_aids | 0.1710 | 0.3229 | 0.0895 | 0.3091 | 0.0027 | 0.0246 |
| dsp_wavelets | 0.1588 | 0.1950 | 0.0812 | 0.1269 | 0.0001 | 0.0003 |
| electroculture | 0.0149 | 0.3496 | 0.0100 | 0.3391 | 0.0000 | 0.0268 |
| emoji_game | 0.2063 | 0.3143 | 0.1375 | 0.2738 | 0.0140 | 0.0386 |
| game_degree_guess | 0.2200 | 0.6593 | 0.1087 | 0.5149 | 0.0510 | 0.3866 |
| game_twenty_questions | 0.1749 | 0.4551 | 0.0885 | 0.3913 | 0.0006 | 0.1385 |
| geography_belgium | 0.4461 | 0.4358 | 0.2032 | 0.4071 | 0.1489 | 0.1770 |
| humanity_future_150y | 0.1368 | 0.4710 | 0.0815 | 0.4684 | 0.0001 | 0.1089 |
| indian_astrology | 0.0289 | 0.2203 | 0.0246 | 0.1735 | 0.0000 | 0.0011 |
| indian_history | 0.1869 | 0.6870 | 0.1121 | 0.4609 | 0.0358 | 0.4292 |
| indian_legal | 0.2108 | 0.3882 | 0.1197 | 0.3173 | 0.0341 | 0.0443 |
| indian_legal_family | 0.2343 | 0.6025 | 0.1179 | 0.5665 | 0.0231 | 0.2784 |
| jokes | 0.1901 | 0.5973 | 0.1281 | 0.4887 | 0.0371 | 0.3817 |
| karnataka_elections | 0.0278 | 0.3956 | 0.0199 | 0.2706 | 0.0000 | 0.0543 |
| linux_audio | 0.2950 | 0.4704 | 0.1605 | 0.2391 | 0.0599 | 0.1208 |
| literature_camus | 0.1765 | 0.3049 | 0.0858 | 0.2018 | 0.0033 | 0.0155 |
| llm_knowledge | 0.1585 | 0.2670 | 0.0784 | 0.2137 | 0.0011 | 0.0045 |
| logic_puzzle | 0.2430 | 0.4903 | 0.1371 | 0.3666 | 0.0229 | 0.1455 |
| lsat_medical_conference | 0.0938 | 0.6478 | 0.0704 | 0.6337 | 0.0068 | 0.3204 |
| lsat_product_codes | 0.0268 | 0.1056 | 0.0255 | 0.1035 | 0.0000 | 0.0000 |
| medical_dsd | 0.2271 | 0.3125 | 0.0939 | 0.2199 | 0.0043 | 0.0153 |
| personas_roleplay | 0.2337 | 0.7983 | 0.1116 | 0.7344 | 0.0360 | 0.6437 |
| physics_cosmology | 0.2785 | 0.0990 | 0.2089 | 0.0921 | 0.0774 | 0.0000 |
| physics_violin_nanoscale | 0.2473 | 0.4119 | 0.1649 | 0.2348 | 0.0830 | 0.1179 |
| scifi_films | 0.0148 | 0.1974 | 0.0121 | 0.1268 | 0.0000 | 0.0003 |
| scifi_films_hal9000 | 0.2331 | 0.4793 | 0.1084 | 0.4247 | 0.0210 | 0.1106 |
| scifi_films_hal9000_games | 0.1588 | 0.3373 | 0.0907 | 0.2099 | 0.0062 | 0.0116 |
| scifi_films_liu_cixin | 0.3026 | 0.4444 | 0.1655 | 0.3670 | 0.0368 | 0.1520 |
| therapy | 0.3206 | 0.5734 | 0.1283 | 0.4230 | 0.0470 | 0.2326 |
| therapy_manipulation | 0.0466 | 0.4167 | 0.0361 | 0.3913 | 0.0000 | 0.0529 |
| wildfires_alberta | 0.0396 | 0.4011 | 0.0321 | 0.3140 | 0.0000 | 0.0594 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 39 topics
- 🔵 **Baseline wins**: 4 topics
- 🟡 **Ties (±0.01)**: 0 topics
