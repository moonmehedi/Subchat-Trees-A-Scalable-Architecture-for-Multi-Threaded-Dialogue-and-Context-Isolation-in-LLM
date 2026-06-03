# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: 40)

## Weighted Average Metrics (Per-Topic Confusion Matrix)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Precision** | 81.6% | 85.3% | **+4.5%** |
| **Recall** | 55.8% | 69.5% | **+24.4%** |
| **F1** | 59.8% | 73.1% | **+22.3%** |
| **Accuracy** | 56.0% | 69.6% | **+24.3%** |
| **Pollution Rate** | 44.0% | 30.4% | **-30.9%** |

## Macro Average Metrics

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Macro Precision** | 73.4% | 79.5% | **+8.2%** |
| **Macro Recall** | 61.8% | 65.3% | **+5.7%** |
| **Macro F1** | 61.4% | 67.9% | **+10.5%** |

## Per-Topic Breakdown


### Baseline - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 100.0% | 70.0% | 82.4% | 7 | 0 | 3 | 10 |
| ai_consciousness | 9.5% | 25.0% | 13.8% | 2 | 19 | 6 | 8 |
| ai_consciousness_friendship | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| ai_meta | 56.2% | 81.8% | 66.7% | 9 | 7 | 2 | 11 |
| bhutan_travel | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| chess | 63.6% | 100.0% | 77.8% | 7 | 4 | 0 | 7 |
| child_nutrition | 100.0% | 33.3% | 50.0% | 2 | 0 | 4 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 50.0% | 100.0% | 66.7% | 1 | 1 | 0 | 1 |
| cookies_recipe_halving | 16.7% | 66.7% | 26.7% | 2 | 10 | 1 | 3 |
| cookies_recipe_halving_argument | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_corrections | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_math_errors | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| covid_safety | 66.7% | 100.0% | 80.0% | 6 | 3 | 0 | 6 |
| covid_safety_hiv_aids | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| dsp_wavelets | 100.0% | 36.4% | 53.3% | 4 | 0 | 7 | 11 |
| dsp_wavelets_c_code | 28.6% | 100.0% | 44.4% | 2 | 5 | 0 | 2 |
| electroculture | 100.0% | 28.6% | 44.4% | 2 | 0 | 5 | 7 |
| emoji_game | 100.0% | 80.6% | 89.3% | 25 | 0 | 6 | 31 |
| game_degree_guess | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| game_twenty_questions | 100.0% | 18.2% | 30.8% | 6 | 0 | 27 | 33 |
| geography_belgium | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| humanity_future_150y | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_astrology | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| indian_astrology_terminology | 0.0% | 0.0% | 0.0% | 0 | 2 | 1 | 1 |
| indian_history | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| indian_legal | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| indian_legal_family | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| indian_legal_loans | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| indian_legal_loans_timeline | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| jokes | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| karnataka_elections | 100.0% | 50.0% | 66.7% | 2 | 0 | 2 | 4 |
| linux_audio | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| linux_audio_pipewire | 28.6% | 100.0% | 44.4% | 2 | 5 | 0 | 2 |
| literature_camus | 100.0% | 33.3% | 50.0% | 2 | 0 | 4 | 6 |
| llm_knowledge | 100.0% | 40.0% | 57.1% | 4 | 0 | 6 | 10 |
| logic_puzzle | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| lsat | 33.3% | 100.0% | 50.0% | 2 | 4 | 0 | 2 |
| lsat_medical_conference | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| lsat_piano_recital | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 33.3% | 50.0% | 2 | 0 | 4 | 6 |
| medical_treatments | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| personas_roleplay | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| physics_blackholes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| physics_cosmology | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| recipes | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| repetitive_loop | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| scifi_films | 100.0% | 71.4% | 83.3% | 5 | 0 | 2 | 7 |
| scifi_films_hal9000 | 100.0% | 80.0% | 88.9% | 4 | 0 | 1 | 5 |
| scifi_films_hal9000_games | 100.0% | 100.0% | 100.0% | 11 | 0 | 0 | 11 |
| scifi_films_liu_cixin | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| scifi_films_space_exploration | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| statistics_multivariate | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| therapy | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| therapy_manipulation | 80.0% | 100.0% | 88.9% | 4 | 1 | 0 | 4 |
| wildfires_alberta | 100.0% | 60.0% | 75.0% | 3 | 0 | 2 | 5 |

### Our System - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 70.0% | 70.0% | 70.0% | 7 | 3 | 3 | 10 |
| ai_consciousness | 63.6% | 87.5% | 73.7% | 7 | 4 | 1 | 8 |
| ai_consciousness_friendship | 100.0% | 33.3% | 50.0% | 2 | 0 | 4 | 6 |
| ai_meta | 100.0% | 81.8% | 90.0% | 9 | 0 | 2 | 11 |
| bhutan_travel | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| chess | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 7 |
| child_nutrition | 100.0% | 66.7% | 80.0% | 4 | 0 | 2 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 33.3% | 100.0% | 50.0% | 1 | 2 | 0 | 1 |
| cookies_recipe_halving | 9.1% | 33.3% | 14.3% | 1 | 10 | 2 | 3 |
| cookies_recipe_halving_argument | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_corrections | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_math_errors | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| covid_safety | 62.5% | 83.3% | 71.4% | 5 | 3 | 1 | 6 |
| covid_safety_hiv_aids | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| dsp_wavelets | 100.0% | 45.5% | 62.5% | 5 | 0 | 6 | 11 |
| dsp_wavelets_c_code | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| electroculture | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| emoji_game | 100.0% | 100.0% | 100.0% | 31 | 0 | 0 | 31 |
| game_degree_guess | 0.0% | 0.0% | 0.0% | 0 | 1 | 3 | 3 |
| game_twenty_questions | 100.0% | 97.0% | 98.5% | 32 | 0 | 1 | 33 |
| geography_belgium | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| humanity_future_150y | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_astrology | 100.0% | 40.0% | 57.1% | 2 | 0 | 3 | 5 |
| indian_astrology_terminology | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| indian_history | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| indian_legal | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_legal_family | 100.0% | 25.0% | 40.0% | 1 | 0 | 3 | 4 |
| indian_legal_loans | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| indian_legal_loans_timeline | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| jokes | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| karnataka_elections | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| linux_audio | 66.7% | 66.7% | 66.7% | 2 | 1 | 1 | 3 |
| linux_audio_pipewire | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| literature_camus | 100.0% | 66.7% | 80.0% | 4 | 0 | 2 | 6 |
| llm_knowledge | 0.0% | 0.0% | 0.0% | 0 | 0 | 10 | 10 |
| logic_puzzle | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| lsat | 66.7% | 100.0% | 80.0% | 2 | 1 | 0 | 2 |
| lsat_medical_conference | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 83.3% | 90.9% | 5 | 0 | 1 | 6 |
| medical_treatments | 50.0% | 100.0% | 66.7% | 2 | 2 | 0 | 2 |
| personas_roleplay | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| physics_blackholes | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| physics_cosmology | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| physics_quantum | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| physics_violin_nanoscale | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| recipes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| repetitive_loop | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| scifi_films | 100.0% | 28.6% | 44.4% | 2 | 0 | 5 | 7 |
| scifi_films_hal9000 | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| scifi_films_hal9000_games | 100.0% | 100.0% | 100.0% | 11 | 0 | 0 | 11 |
| scifi_films_liu_cixin | 100.0% | 50.0% | 66.7% | 2 | 0 | 2 | 4 |
| scifi_films_space_exploration | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| statistics_multivariate | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| therapy | 66.7% | 66.7% | 66.7% | 2 | 1 | 1 | 3 |
| therapy_manipulation | 100.0% | 50.0% | 66.7% | 2 | 0 | 2 | 4 |
| wildfires_alberta | 100.0% | 60.0% | 75.0% | 3 | 0 | 2 | 5 |

## Legacy Raw Counts (LLM Judge TP/FN)
- Baseline: TP=173, TN=0, FP=136, FN=0
- System: TP=215, TN=0, FP=94, FN=0
