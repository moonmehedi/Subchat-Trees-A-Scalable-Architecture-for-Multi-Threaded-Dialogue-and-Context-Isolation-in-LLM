# TABLE 2: TOPIC RECALL SCORES (Buffer Size: 10)

Measures how well each system retains topic-specific information via ROUGE/BLEU scoring.
Higher scores indicate better recall of topic content from conversation history.

## Aggregate Scores

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Avg ROUGE-1 (F1)** | 0.3674 | 0.4206 | **+14.5%** |
| **Avg ROUGE-L (F1)** | 0.2274 | 0.2982 | **+31.1%** |
| **Avg BLEU-2** | 0.1023 | 0.1253 | **+22.5%** |

## Summarization Probe Cost

| Metric | Baseline System | Our System | Difference |
|--------|----------------|------------|------------|
| **Topics Probed** | 43 | 43 | - |
| **Total Probe Tokens** | 249908 | 175875 | - |
| **Avg Tokens per Probe** | 5812 | 4090 | - |
| **Total Probe Latency** | 2965.5s | 2722.8s | - |
| **Avg Probe Latency** | 68.96s | 63.32s | - |

## Per-Topic Breakdown

| Topic | BL ROUGE-1 | SYS ROUGE-1 | BL ROUGE-L | SYS ROUGE-L | BL BLEU | SYS BLEU |
|-------|-----------|------------|-----------|------------|---------|--------|
| ai_chat_tools | 0.3653 | 0.4000 | 0.2037 | 0.2397 | 0.0397 | 0.0510 |
| ai_consciousness | 0.2690 | 0.3389 | 0.1368 | 0.1885 | 0.0128 | 0.0232 |
| ai_consciousness_friendship | 0.4780 | 0.3983 | 0.2537 | 0.2318 | 0.1927 | 0.0575 |
| ai_meta | 0.2543 | 0.3714 | 0.1518 | 0.2337 | 0.0067 | 0.0461 |
| bhutan_travel | 0.3073 | 0.3465 | 0.2703 | 0.3242 | 0.0091 | 0.0160 |
| chess | 0.2213 | 0.3636 | 0.1277 | 0.1935 | 0.0080 | 0.0537 |
| child_nutrition | 0.2080 | 0.3421 | 0.1350 | 0.2606 | 0.0014 | 0.0235 |
| cookies_recipe_halving | 0.4158 | 0.4301 | 0.2013 | 0.2826 | 0.1124 | 0.1197 |
| cookies_recipe_halving_argument | 0.5490 | 0.5207 | 0.2876 | 0.2781 | 0.2612 | 0.1855 |
| cookies_recipe_halving_corrections | 0.4379 | 0.5014 | 0.2438 | 0.3215 | 0.1810 | 0.2390 |
| cookies_recipe_halving_math_errors | 0.4378 | 0.4779 | 0.2242 | 0.2726 | 0.1382 | 0.1478 |
| covid_safety | 0.2711 | 0.3954 | 0.1295 | 0.2747 | 0.0061 | 0.0462 |
| covid_safety_hiv_aids | 0.3945 | 0.2798 | 0.3423 | 0.1840 | 0.0562 | 0.0253 |
| dsp_wavelets | 0.1858 | 0.1408 | 0.1577 | 0.1021 | 0.0001 | 0.0000 |
| electroculture | 0.3422 | 0.3136 | 0.3105 | 0.2616 | 0.0221 | 0.0135 |
| emoji_game | 0.0714 | 0.1611 | 0.0602 | 0.1316 | 0.0001 | 0.0004 |
| game_degree_guess | 0.4760 | 0.5303 | 0.2579 | 0.3509 | 0.2233 | 0.2389 |
| game_twenty_questions | 0.2625 | 0.2580 | 0.1702 | 0.2095 | 0.0190 | 0.0117 |
| geography_belgium | 0.7831 | 0.7617 | 0.7367 | 0.7224 | 0.6837 | 0.5830 |
| humanity_future_150y | 0.4314 | 0.5175 | 0.3327 | 0.5030 | 0.0686 | 0.1525 |
| indian_astrology | 0.2398 | 0.4101 | 0.1358 | 0.2275 | 0.0024 | 0.0537 |
| indian_history | 0.4598 | 0.6909 | 0.3218 | 0.5164 | 0.2062 | 0.4688 |
| indian_legal | 0.3402 | 0.5200 | 0.2019 | 0.4145 | 0.0720 | 0.1419 |
| indian_legal_family | 0.3778 | 0.3916 | 0.3082 | 0.2819 | 0.0411 | 0.0444 |
| jokes | 0.3401 | 0.5741 | 0.1814 | 0.5237 | 0.1232 | 0.4182 |
| karnataka_elections | 0.6090 | 0.5541 | 0.3851 | 0.4326 | 0.3479 | 0.2507 |
| linux_audio | 0.2950 | 0.7880 | 0.1475 | 0.5671 | 0.0308 | 0.5697 |
| literature_camus | 0.2305 | 0.3801 | 0.1099 | 0.2255 | 0.0056 | 0.0497 |
| llm_knowledge | 0.3029 | 0.2781 | 0.1464 | 0.2258 | 0.0227 | 0.0069 |
| logic_puzzle | 0.3270 | 0.4738 | 0.1761 | 0.2939 | 0.0820 | 0.1127 |
| lsat_medical_conference | 0.4884 | 0.5458 | 0.3159 | 0.4230 | 0.2212 | 0.1903 |
| lsat_product_codes | 0.3030 | 0.2417 | 0.2100 | 0.1869 | 0.0158 | 0.0026 |
| medical_dsd | 0.3523 | 0.4580 | 0.1869 | 0.2563 | 0.0281 | 0.0931 |
| personas_roleplay | 0.3643 | 0.3044 | 0.1783 | 0.1948 | 0.0940 | 0.0297 |
| physics_cosmology | 0.6006 | 0.5472 | 0.3571 | 0.4306 | 0.3539 | 0.2033 |
| physics_violin_nanoscale | 0.6553 | 0.2805 | 0.3925 | 0.1789 | 0.3353 | 0.0398 |
| scifi_films | 0.3040 | 0.3259 | 0.1761 | 0.1673 | 0.0258 | 0.0211 |
| scifi_films_hal9000 | 0.3800 | 0.3768 | 0.1700 | 0.1988 | 0.0670 | 0.1095 |
| scifi_films_hal9000_games | 0.2249 | 0.2076 | 0.1065 | 0.1213 | 0.0042 | 0.0027 |
| scifi_films_liu_cixin | 0.4684 | 0.6078 | 0.2928 | 0.5120 | 0.1404 | 0.2925 |
| therapy | 0.2214 | 0.5247 | 0.1195 | 0.3692 | 0.0090 | 0.1663 |
| therapy_manipulation | 0.2782 | 0.3647 | 0.1429 | 0.2199 | 0.0062 | 0.0406 |
| wildfires_alberta | 0.4730 | 0.3929 | 0.2809 | 0.2881 | 0.1193 | 0.0444 |

## Topic Winners (System vs Baseline)

- 🟢 **System wins**: 27 topics
- 🔵 **Baseline wins**: 14 topics
- 🟡 **Ties (±0.01)**: 2 topics
