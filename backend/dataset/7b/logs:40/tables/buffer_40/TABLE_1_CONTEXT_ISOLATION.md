# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: 40)

## Weighted Average Metrics (Per-Topic Confusion Matrix)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Precision** | 21.5% | 76.2% | **+254.8%** |
| **Recall** | 7.8% | 33.4% | **+329.2%** |
| **F1** | 9.8% | 39.3% | **+300.8%** |
| **Accuracy** | 8.1% | 33.7% | **+316.0%** |
| **Pollution Rate** | 91.9% | 66.3% | **-27.8%** |

## Macro Average Metrics

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Macro Precision** | 29.0% | 72.8% | **+150.7%** |
| **Macro Recall** | 17.8% | 41.4% | **+133.3%** |
| **Macro F1** | 19.0% | 46.5% | **+144.2%** |

## Per-Topic Breakdown


### Baseline - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 0.0% | 0.0% | 0.0% | 0 | 0 | 10 | 10 |
| ai_consciousness | 100.0% | 12.5% | 22.2% | 1 | 0 | 7 | 8 |
| ai_consciousness_friendship | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| ai_meta | 100.0% | 18.2% | 30.8% | 2 | 0 | 9 | 11 |
| bhutan_travel | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| chess | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| child_nutrition | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 12.5% | 100.0% | 22.2% | 1 | 7 | 0 | 1 |
| cookies_recipe_halving | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_argument | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| cookies_recipe_halving_corrections | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_math_errors | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| covid_safety | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| covid_safety_hiv_aids | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| dsp_wavelets | 100.0% | 9.1% | 16.7% | 1 | 0 | 10 | 11 |
| dsp_wavelets_c_code | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| electroculture | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| emoji_game | 0.0% | 0.0% | 0.0% | 0 | 0 | 31 | 31 |
| game_degree_guess | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| game_twenty_questions | 0.0% | 0.0% | 0.0% | 0 | 0 | 33 | 33 |
| geography_belgium | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| humanity_future_150y | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| indian_astrology | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| indian_astrology_terminology | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| indian_history | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| indian_legal | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| indian_legal_family | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| indian_legal_loans | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| indian_legal_loans_timeline | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| jokes | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| karnataka_elections | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| linux_audio | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| linux_audio_pipewire | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| literature_camus | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| llm_knowledge | 0.0% | 0.0% | 0.0% | 0 | 0 | 10 | 10 |
| logic_puzzle | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| lsat | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| lsat_medical_conference | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| medical_treatments | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| personas_roleplay | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| physics_blackholes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| physics_cosmology | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| recipes | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| repetitive_loop | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| scifi_films | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| scifi_films_hal9000 | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| scifi_films_hal9000_games | 0.0% | 0.0% | 0.0% | 0 | 0 | 11 | 11 |
| scifi_films_liu_cixin | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| scifi_films_space_exploration | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| statistics_multivariate | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| therapy | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| therapy_manipulation | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| wildfires_alberta | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |

### Our System - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 0.0% | 0.0% | 0.0% | 0 | 0 | 10 | 10 |
| ai_consciousness | 100.0% | 25.0% | 40.0% | 2 | 0 | 6 | 8 |
| ai_consciousness_friendship | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| ai_meta | 100.0% | 54.5% | 70.6% | 6 | 0 | 5 | 11 |
| bhutan_travel | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| chess | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| child_nutrition | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 33.3% | 100.0% | 50.0% | 1 | 2 | 0 | 1 |
| cookies_recipe_halving | 10.0% | 33.3% | 15.4% | 1 | 9 | 2 | 3 |
| cookies_recipe_halving_argument | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_corrections | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_math_errors | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| covid_safety | 100.0% | 33.3% | 50.0% | 2 | 0 | 4 | 6 |
| covid_safety_hiv_aids | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| dsp_wavelets | 100.0% | 9.1% | 16.7% | 1 | 0 | 10 | 11 |
| dsp_wavelets_c_code | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| electroculture | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| emoji_game | 100.0% | 100.0% | 100.0% | 31 | 0 | 0 | 31 |
| game_degree_guess | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| game_twenty_questions | 100.0% | 3.0% | 5.9% | 1 | 0 | 32 | 33 |
| geography_belgium | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| humanity_future_150y | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| indian_astrology | 100.0% | 20.0% | 33.3% | 1 | 0 | 4 | 5 |
| indian_astrology_terminology | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| indian_history | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| indian_legal | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| indian_legal_family | 100.0% | 25.0% | 40.0% | 1 | 0 | 3 | 4 |
| indian_legal_loans | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| indian_legal_loans_timeline | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| jokes | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| karnataka_elections | 100.0% | 25.0% | 40.0% | 1 | 0 | 3 | 4 |
| linux_audio | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| linux_audio_pipewire | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| literature_camus | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| llm_knowledge | 100.0% | 10.0% | 18.2% | 1 | 0 | 9 | 10 |
| logic_puzzle | 100.0% | 25.0% | 40.0% | 1 | 0 | 3 | 4 |
| lsat | 50.0% | 100.0% | 66.7% | 2 | 2 | 0 | 2 |
| lsat_medical_conference | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| medical_treatments | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| personas_roleplay | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| physics_blackholes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| physics_cosmology | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| recipes | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| repetitive_loop | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| scifi_films | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| scifi_films_hal9000 | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| scifi_films_hal9000_games | 0.0% | 0.0% | 0.0% | 0 | 0 | 11 | 11 |
| scifi_films_liu_cixin | 100.0% | 25.0% | 40.0% | 1 | 0 | 3 | 4 |
| scifi_films_space_exploration | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| statistics_multivariate | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| therapy | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| therapy_manipulation | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| wildfires_alberta | 100.0% | 20.0% | 33.3% | 1 | 0 | 4 | 5 |

## Legacy Raw Counts (LLM Judge TP/FN)
- Baseline: TP=25, TN=0, FP=284, FN=0
- System: TP=104, TN=0, FP=205, FN=0
