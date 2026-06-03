# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: 5)

## Weighted Average Metrics (Per-Topic Confusion Matrix)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Precision** | 44.7% | 84.0% | **+87.7%** |
| **Recall** | 21.1% | 58.1% | **+175.4%** |
| **F1** | 24.3% | 62.9% | **+158.6%** |
| **Accuracy** | 21.4% | 58.3% | **+172.7%** |
| **Pollution Rate** | 78.6% | 41.7% | **-46.9%** |

## Macro Average Metrics

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Macro Precision** | 48.5% | 74.4% | **+53.2%** |
| **Macro Recall** | 33.7% | 59.6% | **+76.6%** |
| **Macro F1** | 35.2% | 60.8% | **+73.0%** |

## Per-Topic Breakdown


### Baseline - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 0.0% | 0.0% | 0.0% | 0 | 0 | 10 | 10 |
| ai_consciousness | 0.0% | 0.0% | 0.0% | 0 | 0 | 8 | 8 |
| ai_consciousness_friendship | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| ai_meta | 100.0% | 9.1% | 16.7% | 1 | 0 | 10 | 11 |
| bhutan_travel | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| chess | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| child_nutrition | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| cookies_preferences | 16.7% | 100.0% | 28.6% | 2 | 10 | 0 | 2 |
| cookies_recipe | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| cookies_recipe_halving | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| cookies_recipe_halving_argument | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| cookies_recipe_halving_corrections | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_math_errors | 100.0% | 25.0% | 40.0% | 1 | 0 | 3 | 4 |
| covid_safety | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| covid_safety_hiv_aids | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| dsp_wavelets | 100.0% | 9.1% | 16.7% | 1 | 0 | 10 | 11 |
| dsp_wavelets_c_code | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| electroculture | 100.0% | 57.1% | 72.7% | 4 | 0 | 3 | 7 |
| emoji_game | 100.0% | 16.1% | 27.8% | 5 | 0 | 26 | 31 |
| game_degree_guess | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| game_twenty_questions | 0.0% | 0.0% | 0.0% | 0 | 0 | 33 | 33 |
| geography_belgium | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| humanity_future_150y | 100.0% | 25.0% | 40.0% | 1 | 0 | 3 | 4 |
| indian_astrology | 100.0% | 40.0% | 57.1% | 2 | 0 | 3 | 5 |
| indian_astrology_terminology | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| indian_history | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| indian_legal | 75.0% | 75.0% | 75.0% | 3 | 1 | 1 | 4 |
| indian_legal_family | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| indian_legal_loans | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| indian_legal_loans_timeline | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| jokes | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| karnataka_elections | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| linux_audio | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| linux_audio_pipewire | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| literature_camus | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| llm_knowledge | 0.0% | 0.0% | 0.0% | 0 | 0 | 10 | 10 |
| logic_puzzle | 50.0% | 100.0% | 66.7% | 4 | 4 | 0 | 4 |
| lsat | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| lsat_medical_conference | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 66.7% | 80.0% | 4 | 0 | 2 | 6 |
| medical_treatments | 22.2% | 100.0% | 36.4% | 2 | 7 | 0 | 2 |
| personas_roleplay | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| physics_blackholes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| physics_cosmology | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| recipes | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| repetitive_loop | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| scifi_films | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| scifi_films_hal9000 | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| scifi_films_hal9000_games | 0.0% | 0.0% | 0.0% | 0 | 0 | 11 | 11 |
| scifi_films_liu_cixin | 100.0% | 50.0% | 66.7% | 2 | 0 | 2 | 4 |
| scifi_films_space_exploration | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| statistics_multivariate | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| therapy | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| therapy_manipulation | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| wildfires_alberta | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |

### Our System - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 100.0% | 60.0% | 75.0% | 6 | 0 | 4 | 10 |
| ai_consciousness | 40.0% | 25.0% | 30.8% | 2 | 3 | 6 | 8 |
| ai_consciousness_friendship | 100.0% | 66.7% | 80.0% | 4 | 0 | 2 | 6 |
| ai_meta | 100.0% | 27.3% | 42.9% | 3 | 0 | 8 | 11 |
| bhutan_travel | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| chess | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 7 |
| child_nutrition | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 33.3% | 100.0% | 50.0% | 1 | 2 | 0 | 1 |
| cookies_recipe_halving | 50.0% | 33.3% | 40.0% | 1 | 1 | 2 | 3 |
| cookies_recipe_halving_argument | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_corrections | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_math_errors | 42.9% | 75.0% | 54.5% | 3 | 4 | 1 | 4 |
| covid_safety | 71.4% | 83.3% | 76.9% | 5 | 2 | 1 | 6 |
| covid_safety_hiv_aids | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| dsp_wavelets | 100.0% | 18.2% | 30.8% | 2 | 0 | 9 | 11 |
| dsp_wavelets_c_code | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| electroculture | 100.0% | 85.7% | 92.3% | 6 | 0 | 1 | 7 |
| emoji_game | 100.0% | 100.0% | 100.0% | 31 | 0 | 0 | 31 |
| game_degree_guess | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| game_twenty_questions | 100.0% | 27.3% | 42.9% | 9 | 0 | 24 | 33 |
| geography_belgium | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| humanity_future_150y | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_astrology | 83.3% | 100.0% | 90.9% | 5 | 1 | 0 | 5 |
| indian_astrology_terminology | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| indian_history | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| indian_legal | 60.0% | 75.0% | 66.7% | 3 | 2 | 1 | 4 |
| indian_legal_family | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| indian_legal_loans | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| indian_legal_loans_timeline | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| jokes | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| karnataka_elections | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| linux_audio | 23.1% | 100.0% | 37.5% | 3 | 10 | 0 | 3 |
| linux_audio_pipewire | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| literature_camus | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| llm_knowledge | 100.0% | 40.0% | 57.1% | 4 | 0 | 6 | 10 |
| logic_puzzle | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| lsat | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| lsat_medical_conference | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| lsat_piano_recital | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| medical_treatments | 50.0% | 50.0% | 50.0% | 1 | 1 | 1 | 2 |
| personas_roleplay | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| physics_blackholes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| physics_cosmology | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| recipes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| repetitive_loop | 33.3% | 100.0% | 50.0% | 1 | 2 | 0 | 1 |
| scifi_films | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| scifi_films_hal9000 | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| scifi_films_hal9000_games | 100.0% | 100.0% | 100.0% | 11 | 0 | 0 | 11 |
| scifi_films_liu_cixin | 100.0% | 25.0% | 40.0% | 1 | 0 | 3 | 4 |
| scifi_films_space_exploration | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| statistics_multivariate | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| therapy | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| therapy_manipulation | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| wildfires_alberta | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |

## Legacy Raw Counts (LLM Judge TP/FN)
- Baseline: TP=66, TN=0, FP=243, FN=0
- System: TP=180, TN=0, FP=129, FN=0
