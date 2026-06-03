# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: 10)

## Weighted Average Metrics (Per-Topic Confusion Matrix)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Precision** | 81.2% | 93.2% | **+14.8%** |
| **Recall** | 59.7% | 80.2% | **+34.2%** |
| **F1** | 64.3% | 83.4% | **+29.7%** |
| **Accuracy** | 59.9% | 80.3% | **+34.1%** |
| **Pollution Rate** | 40.1% | 19.7% | **-50.8%** |

## Macro Average Metrics

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Macro Precision** | 75.7% | 88.1% | **+16.4%** |
| **Macro Recall** | 67.3% | 78.7% | **+17.0%** |
| **Macro F1** | 67.1% | 80.1% | **+19.3%** |

## Per-Topic Breakdown


### Baseline - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 100.0% | 20.0% | 33.3% | 2 | 0 | 8 | 10 |
| ai_consciousness | 33.3% | 25.0% | 28.6% | 2 | 4 | 6 | 8 |
| ai_consciousness_friendship | 25.0% | 66.7% | 36.4% | 4 | 12 | 2 | 6 |
| ai_meta | 100.0% | 45.5% | 62.5% | 5 | 0 | 6 | 11 |
| bhutan_travel | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| chess | 36.4% | 57.1% | 44.4% | 4 | 7 | 3 | 7 |
| child_nutrition | 100.0% | 50.0% | 66.7% | 3 | 0 | 3 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| cookies_recipe_halving | 33.3% | 100.0% | 50.0% | 3 | 6 | 0 | 3 |
| cookies_recipe_halving_argument | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| cookies_recipe_halving_corrections | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_math_errors | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| covid_safety | 60.0% | 100.0% | 75.0% | 6 | 4 | 0 | 6 |
| covid_safety_hiv_aids | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| dsp_wavelets | 100.0% | 36.4% | 53.3% | 4 | 0 | 7 | 11 |
| dsp_wavelets_c_code | 28.6% | 100.0% | 44.4% | 2 | 5 | 0 | 2 |
| electroculture | 80.0% | 57.1% | 66.7% | 4 | 1 | 3 | 7 |
| emoji_game | 100.0% | 100.0% | 100.0% | 31 | 0 | 0 | 31 |
| game_degree_guess | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| game_twenty_questions | 100.0% | 36.4% | 53.3% | 12 | 0 | 21 | 33 |
| geography_belgium | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| humanity_future_150y | 100.0% | 50.0% | 66.7% | 2 | 0 | 2 | 4 |
| indian_astrology | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| indian_astrology_terminology | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| indian_history | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| indian_legal | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| indian_legal_family | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_legal_loans | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| indian_legal_loans_timeline | 50.0% | 100.0% | 66.7% | 1 | 1 | 0 | 1 |
| jokes | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| karnataka_elections | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| linux_audio | 60.0% | 100.0% | 75.0% | 3 | 2 | 0 | 3 |
| linux_audio_pipewire | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| literature_camus | 100.0% | 50.0% | 66.7% | 3 | 0 | 3 | 6 |
| llm_knowledge | 100.0% | 60.0% | 75.0% | 6 | 0 | 4 | 10 |
| logic_puzzle | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| lsat | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| lsat_medical_conference | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 66.7% | 80.0% | 4 | 0 | 2 | 6 |
| medical_treatments | 40.0% | 100.0% | 57.1% | 2 | 3 | 0 | 2 |
| personas_roleplay | 100.0% | 66.7% | 80.0% | 4 | 0 | 2 | 6 |
| physics_blackholes | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| physics_cosmology | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| recipes | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| repetitive_loop | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| scifi_films | 100.0% | 42.9% | 60.0% | 3 | 0 | 4 | 7 |
| scifi_films_hal9000 | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| scifi_films_hal9000_games | 100.0% | 36.4% | 53.3% | 4 | 0 | 7 | 11 |
| scifi_films_liu_cixin | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| scifi_films_space_exploration | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| statistics_multivariate | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| therapy | 42.9% | 100.0% | 60.0% | 3 | 4 | 0 | 3 |
| therapy_manipulation | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| wildfires_alberta | 100.0% | 60.0% | 75.0% | 3 | 0 | 2 | 5 |

### Our System - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 100.0% | 70.0% | 82.4% | 7 | 0 | 3 | 10 |
| ai_consciousness | 100.0% | 75.0% | 85.7% | 6 | 0 | 2 | 8 |
| ai_consciousness_friendship | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| ai_meta | 100.0% | 81.8% | 90.0% | 9 | 0 | 2 | 11 |
| bhutan_travel | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| chess | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 7 |
| child_nutrition | 100.0% | 33.3% | 50.0% | 2 | 0 | 4 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 33.3% | 100.0% | 50.0% | 1 | 2 | 0 | 1 |
| cookies_recipe_halving | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| cookies_recipe_halving_argument | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_corrections | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| cookies_recipe_halving_math_errors | 57.1% | 100.0% | 72.7% | 4 | 3 | 0 | 4 |
| covid_safety | 66.7% | 100.0% | 80.0% | 6 | 3 | 0 | 6 |
| covid_safety_hiv_aids | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| dsp_wavelets | 100.0% | 90.9% | 95.2% | 10 | 0 | 1 | 11 |
| dsp_wavelets_c_code | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| electroculture | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 7 |
| emoji_game | 100.0% | 83.9% | 91.2% | 26 | 0 | 5 | 31 |
| game_degree_guess | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| game_twenty_questions | 100.0% | 100.0% | 100.0% | 33 | 0 | 0 | 33 |
| geography_belgium | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| humanity_future_150y | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_astrology | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| indian_astrology_terminology | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| indian_history | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| indian_legal | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_legal_family | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_legal_loans | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| indian_legal_loans_timeline | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| jokes | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| karnataka_elections | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| linux_audio | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| linux_audio_pipewire | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| literature_camus | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| llm_knowledge | 100.0% | 30.0% | 46.2% | 3 | 0 | 7 | 10 |
| logic_puzzle | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| lsat | 66.7% | 100.0% | 80.0% | 2 | 1 | 0 | 2 |
| lsat_medical_conference | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| medical_treatments | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| personas_roleplay | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| physics_blackholes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| physics_cosmology | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| recipes | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| repetitive_loop | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| scifi_films | 100.0% | 71.4% | 83.3% | 5 | 0 | 2 | 7 |
| scifi_films_hal9000 | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| scifi_films_hal9000_games | 100.0% | 100.0% | 100.0% | 11 | 0 | 0 | 11 |
| scifi_films_liu_cixin | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| scifi_films_space_exploration | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| statistics_multivariate | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| therapy | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| therapy_manipulation | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| wildfires_alberta | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |

## Legacy Raw Counts (LLM Judge TP/FN)
- Baseline: TP=185, TN=0, FP=124, FN=0
- System: TP=248, TN=0, FP=61, FN=0
