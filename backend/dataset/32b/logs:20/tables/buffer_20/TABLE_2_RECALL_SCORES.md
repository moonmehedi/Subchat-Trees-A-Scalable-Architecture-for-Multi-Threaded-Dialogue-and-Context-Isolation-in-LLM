# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 20)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.3338 | 0.4283 | **+28.3%** |
| **Avg ROUGE-L (F1)** | 0.2009 | 0.3016 | **+50.1%** |
| **Avg BLEU-2** | 0.0731 | 0.1247 | **+70.7%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 373285 | 264906 | - |
| **Avg Tokens per Probe** | 8681 | 6161 | - |
| **Total Probe Latency** | 3002.4s | 2796.5s | - |
| **Avg Probe Latency** | 69.82s | 65.04s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.2252 | 0.3455 | 0.1026 | 0.2435 | 0.0072 | 0.0158 |
| ai_consciousness | 0.2391 | 0.2936 | 0.1195 | 0.1808 | 0.0048 | 0.0109 |
| ai_consciousness_friendship | 0.3721 | 0.4308 | 0.1697 | 0.2893 | 0.0414 | 0.0744 |
| ai_meta | 0.3302 | 0.3252 | 0.1336 | 0.2127 | 0.0367 | 0.0202 |
| bhutan_travel | 0.2359 | 0.3370 | 0.1454 | 0.2806 | 0.0051 | 0.0268 |
| chess | 0.3053 | 0.3150 | 0.1371 | 0.1752 | 0.0524 | 0.0120 |
| child_nutrition | 0.2978 | 0.2587 | 0.2286 | 0.2040 | 0.0095 | 0.0029 |
| cookies_recipe_halving | 0.3452 | 0.5273 | 0.1548 | 0.3682 | 0.0427 | 0.2121 |
| cookies_recipe_halving_argument | 0.5615 | 0.5908 | 0.3102 | 0.3415 | 0.2123 | 0.2724 |
| cookies_recipe_halving_corrections | 0.4885 | 0.5215 | 0.3155 | 0.3110 | 0.1654 | 0.2065 |
| cookies_recipe_halving_math_errors | 0.3725 | 0.6658 | 0.2118 | 0.4465 | 0.0492 | 0.3809 |
| covid_safety | 0.4353 | 0.3837 | 0.2902 | 0.2531 | 0.0853 | 0.0390 |
| covid_safety_hiv_aids | 0.2540 | 0.3451 | 0.2021 | 0.2619 | 0.0081 | 0.0390 |
| dsp_wavelets | 0.0889 | 0.1393 | 0.0650 | 0.0898 | 0.0000 | 0.0000 |
| electroculture | 0.2393 | 0.2780 | 0.1439 | 0.2691 | 0.0013 | 0.0065 |
| emoji_game | 0.2295 | 0.2025 | 0.1538 | 0.1805 | 0.0109 | 0.0008 |
| game_degree_guess | 0.2430 | 0.5520 | 0.1229 | 0.2724 | 0.0162 | 0.2464 |
| game_twenty_questions | 0.1781 | 0.2983 | 0.1205 | 0.2496 | 0.0037 | 0.0253 |
| geography_belgium | 0.7337 | 0.6773 | 0.6586 | 0.5550 | 0.5051 | 0.3415 |
| humanity_future_150y | 0.4013 | 0.5255 | 0.1692 | 0.4986 | 0.0525 | 0.1549 |
| indian_astrology | 0.3303 | 0.2766 | 0.1619 | 0.2618 | 0.0339 | 0.0073 |
| indian_history | 0.4674 | 0.7200 | 0.3370 | 0.5000 | 0.2199 | 0.4842 |
| indian_legal | 0.2718 | 0.4604 | 0.1332 | 0.3915 | 0.0268 | 0.0997 |
| indian_legal_family | 0.4031 | 0.3633 | 0.3260 | 0.2110 | 0.0560 | 0.0367 |
| jokes | 0.2282 | 0.6022 | 0.1456 | 0.4696 | 0.0608 | 0.3134 |
| karnataka_elections | 0.6195 | 0.5926 | 0.4040 | 0.3951 | 0.3306 | 0.2920 |
| linux_audio | 0.4305 | 0.6247 | 0.2007 | 0.3317 | 0.1055 | 0.2957 |
| literature_camus | 0.2489 | 0.3654 | 0.1121 | 0.2248 | 0.0112 | 0.0404 |
| llm_knowledge | 0.3465 | 0.3035 | 0.2333 | 0.2312 | 0.0312 | 0.0103 |
| logic_puzzle | 0.3732 | 0.5411 | 0.1964 | 0.3539 | 0.1006 | 0.2282 |
| lsat_medical_conference | 0.5304 | 0.5755 | 0.3749 | 0.4929 | 0.1897 | 0.2320 |
| lsat_product_codes | 0.1482 | 0.2594 | 0.1159 | 0.2340 | 0.0000 | 0.0061 |
| medical_dsd | 0.3178 | 0.4941 | 0.1944 | 0.3222 | 0.0141 | 0.1551 |
| personas_roleplay | 0.2461 | 0.3614 | 0.1157 | 0.2290 | 0.0117 | 0.0661 |
| physics_cosmology | 0.3183 | 0.5584 | 0.2200 | 0.3206 | 0.0968 | 0.2486 |
| physics_violin_nanoscale | 0.3333 | 0.4191 | 0.2143 | 0.2058 | 0.1217 | 0.1732 |
| scifi_films | 0.2366 | 0.2978 | 0.1205 | 0.2285 | 0.0129 | 0.0110 |
| scifi_films_hal9000 | 0.3339 | 0.4161 | 0.1948 | 0.2484 | 0.0852 | 0.1141 |
| scifi_films_hal9000_games | 0.2246 | 0.3794 | 0.1184 | 0.2638 | 0.0070 | 0.0341 |
| scifi_films_liu_cixin | 0.3903 | 0.5851 | 0.1963 | 0.4946 | 0.0797 | 0.2703 |
| therapy | 0.1860 | 0.4114 | 0.1023 | 0.2547 | 0.0078 | 0.0683 |
| therapy_manipulation | 0.2313 | 0.3978 | 0.1215 | 0.3115 | 0.0076 | 0.0456 |
| wildfires_alberta | 0.5624 | 0.3991 | 0.3455 | 0.3097 | 0.2224 | 0.0433 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 32 topics
- 🔵 **Baseline wins**: 9 topics
- 🟡 **Ties (±0.01)**: 2 topics
