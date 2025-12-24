# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: 5)

## Weighted Average Metrics (Per-Topic Confusion Matrix)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Precision** | 87.8% | 81.0% | **-7.7%** |
| **Recall** | 70.1% | 73.7% | **+5.1%** |
| **F1** | 73.7% | 74.4% | **+0.9%** |
| **Accuracy** | 69.0% | 72.5% | **+5.1%** |
| **Pollution Rate** | 31.0% | 27.5% | **-11.3%** |

## Macro Average Metrics

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Macro Precision** | 81.1% | 73.9% | **-8.9%** |
| **Macro Recall** | 69.8% | 69.9% | **+0.1%** |
| **Macro F1** | 70.7% | 69.2% | **-2.2%** |

## Per-Topic Breakdown


### Baseline - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 100.0% | 30.0% | 46.2% | 3 | 0 | 7 | 10 |
| ai_consciousness | 40.0% | 25.0% | 30.8% | 2 | 3 | 6 | 8 |
| ai_consciousness_friendship | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| ai_meta | 100.0% | 45.5% | 62.5% | 5 | 0 | 6 | 11 |
| bhutan_travel | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| chess | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 7 |
| child_nutrition | 100.0% | 33.3% | 50.0% | 2 | 0 | 4 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 33.3% | 100.0% | 50.0% | 1 | 2 | 0 | 1 |
| cookies_recipe_halving | 33.3% | 33.3% | 33.3% | 1 | 2 | 2 | 3 |
| cookies_recipe_halving_argument | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_corrections | 42.9% | 100.0% | 60.0% | 3 | 4 | 0 | 3 |
| cookies_recipe_halving_math_errors | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| covid_safety | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| covid_safety_hiv_aids | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| dsp_wavelets | 100.0% | 36.4% | 53.3% | 4 | 0 | 7 | 11 |
| dsp_wavelets_c_code | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| electroculture | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 7 |
| emoji_game | 100.0% | 100.0% | 100.0% | 31 | 0 | 0 | 31 |
| game_degree_guess | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| game_twenty_questions | 100.0% | 100.0% | 100.0% | 33 | 0 | 0 | 33 |
| geography_belgium | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| humanity_future_150y | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_astrology | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| indian_astrology_terminology | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| indian_history | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| indian_legal | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| indian_legal_family | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_legal_loans | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| indian_legal_loans_timeline | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| jokes | 100.0% | 83.3% | 90.9% | 5 | 0 | 1 | 6 |
| karnataka_elections | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| linux_audio | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| linux_audio_pipewire | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| literature_camus | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| llm_knowledge | 100.0% | 40.0% | 57.1% | 4 | 0 | 6 | 10 |
| logic_puzzle | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| lsat | 40.0% | 100.0% | 57.1% | 2 | 3 | 0 | 2 |
| lsat_medical_conference | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 83.3% | 90.9% | 5 | 0 | 1 | 6 |
| medical_treatments | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| personas_roleplay | 100.0% | 83.3% | 90.9% | 5 | 0 | 1 | 6 |
| physics_blackholes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| physics_cosmology | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| recipes | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| repetitive_loop | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| scifi_films | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| scifi_films_hal9000 | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| scifi_films_hal9000_games | 100.0% | 100.0% | 100.0% | 11 | 0 | 0 | 11 |
| scifi_films_liu_cixin | 100.0% | 50.0% | 66.7% | 2 | 0 | 2 | 4 |
| scifi_films_space_exploration | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| statistics_multivariate | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| therapy | 42.9% | 100.0% | 60.0% | 3 | 4 | 0 | 3 |
| therapy_manipulation | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| wildfires_alberta | 100.0% | 80.0% | 88.9% | 4 | 0 | 1 | 5 |

### Our System - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 100.0% | 50.0% | 66.7% | 5 | 0 | 5 | 10 |
| ai_consciousness | 23.1% | 37.5% | 28.6% | 3 | 10 | 5 | 8 |
| ai_consciousness_friendship | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| ai_meta | 100.0% | 27.3% | 42.9% | 3 | 0 | 8 | 11 |
| bhutan_travel | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| chess | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 7 |
| child_nutrition | 100.0% | 50.0% | 66.7% | 3 | 0 | 3 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| cookies_recipe_halving | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| cookies_recipe_halving_argument | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_corrections | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_math_errors | 44.4% | 100.0% | 61.5% | 4 | 5 | 0 | 4 |
| covid_safety | 46.2% | 100.0% | 63.2% | 6 | 7 | 0 | 6 |
| covid_safety_hiv_aids | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| dsp_wavelets | 100.0% | 36.4% | 53.3% | 4 | 0 | 7 | 11 |
| dsp_wavelets_c_code | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| electroculture | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 7 |
| emoji_game | 100.0% | 100.0% | 100.0% | 31 | 0 | 0 | 31 |
| game_degree_guess | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| game_twenty_questions | 100.0% | 100.0% | 100.0% | 33 | 0 | 0 | 33 |
| geography_belgium | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| humanity_future_150y | 80.0% | 100.0% | 88.9% | 4 | 1 | 0 | 4 |
| indian_astrology | 83.3% | 100.0% | 90.9% | 5 | 1 | 0 | 5 |
| indian_astrology_terminology | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| indian_history | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| indian_legal | 60.0% | 75.0% | 66.7% | 3 | 2 | 1 | 4 |
| indian_legal_family | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_legal_loans | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| indian_legal_loans_timeline | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| jokes | 100.0% | 83.3% | 90.9% | 5 | 0 | 1 | 6 |
| karnataka_elections | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| linux_audio | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| linux_audio_pipewire | 50.0% | 100.0% | 66.7% | 2 | 2 | 0 | 2 |
| literature_camus | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| llm_knowledge | 100.0% | 100.0% | 100.0% | 10 | 0 | 0 | 10 |
| logic_puzzle | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| lsat | 33.3% | 100.0% | 50.0% | 2 | 4 | 0 | 2 |
| lsat_medical_conference | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| medical_treatments | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| personas_roleplay | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| physics_blackholes | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| physics_cosmology | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| recipes | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| repetitive_loop | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| scifi_films | 62.5% | 71.4% | 66.7% | 5 | 3 | 2 | 7 |
| scifi_films_hal9000 | 100.0% | 60.0% | 75.0% | 3 | 0 | 2 | 5 |
| scifi_films_hal9000_games | 100.0% | 100.0% | 100.0% | 11 | 0 | 0 | 11 |
| scifi_films_liu_cixin | 100.0% | 25.0% | 40.0% | 1 | 0 | 3 | 4 |
| scifi_films_space_exploration | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| statistics_multivariate | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| therapy | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| therapy_manipulation | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| wildfires_alberta | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |

## Legacy Raw Counts (LLM Judge TP/FN)
- Baseline: TP=216, TN=0, FP=97, FN=0
- System: TP=227, TN=0, FP=86, FN=0
