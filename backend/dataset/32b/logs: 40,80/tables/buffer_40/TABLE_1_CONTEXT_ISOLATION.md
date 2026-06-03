# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: 40)

## Weighted Average Metrics (Per-Topic Confusion Matrix)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Precision** | 84.9% | 90.0% | **+6.0%** |
| **Recall** | 63.6% | 74.4% | **+16.8%** |
| **F1** | 65.7% | 78.2% | **+19.1%** |
| **Accuracy** | 63.8% | 74.4% | **+16.8%** |
| **Pollution Rate** | 36.2% | 25.6% | **-29.5%** |

## Macro Average Metrics

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Macro Precision** | 78.3% | 88.2% | **+12.7%** |
| **Macro Recall** | 71.6% | 74.0% | **+3.3%** |
| **Macro F1** | 68.4% | 76.7% | **+12.3%** |

## Per-Topic Breakdown


### Baseline - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 100.0% | 70.0% | 82.4% | 7 | 0 | 3 | 10 |
| ai_consciousness | 0.0% | 0.0% | 0.0% | 0 | 4 | 8 | 8 |
| ai_consciousness_friendship | 21.4% | 100.0% | 35.3% | 6 | 22 | 0 | 6 |
| ai_meta | 100.0% | 90.9% | 95.2% | 10 | 0 | 1 | 11 |
| bhutan_travel | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| chess | 70.0% | 100.0% | 82.4% | 7 | 3 | 0 | 7 |
| child_nutrition | 100.0% | 33.3% | 50.0% | 2 | 0 | 4 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 33.3% | 100.0% | 50.0% | 1 | 2 | 0 | 1 |
| cookies_recipe_halving | 50.0% | 33.3% | 40.0% | 1 | 1 | 2 | 3 |
| cookies_recipe_halving_argument | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| cookies_recipe_halving_corrections | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| cookies_recipe_halving_math_errors | 100.0% | 50.0% | 66.7% | 2 | 0 | 2 | 4 |
| covid_safety | 75.0% | 100.0% | 85.7% | 6 | 2 | 0 | 6 |
| covid_safety_hiv_aids | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| dsp_wavelets | 100.0% | 45.5% | 62.5% | 5 | 0 | 6 | 11 |
| dsp_wavelets_c_code | 25.0% | 100.0% | 40.0% | 2 | 6 | 0 | 2 |
| electroculture | 100.0% | 28.6% | 44.4% | 2 | 0 | 5 | 7 |
| emoji_game | 100.0% | 100.0% | 100.0% | 31 | 0 | 0 | 31 |
| game_degree_guess | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| game_twenty_questions | 100.0% | 18.2% | 30.8% | 6 | 0 | 27 | 33 |
| geography_belgium | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| humanity_future_150y | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_astrology | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| indian_astrology_terminology | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| indian_history | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| indian_legal | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_legal_family | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| indian_legal_loans | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| indian_legal_loans_timeline | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| jokes | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| karnataka_elections | 100.0% | 50.0% | 66.7% | 2 | 0 | 2 | 4 |
| linux_audio | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| linux_audio_pipewire | 25.0% | 100.0% | 40.0% | 2 | 6 | 0 | 2 |
| literature_camus | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| llm_knowledge | 100.0% | 40.0% | 57.1% | 4 | 0 | 6 | 10 |
| logic_puzzle | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| lsat | 28.6% | 100.0% | 44.4% | 2 | 5 | 0 | 2 |
| lsat_medical_conference | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| medical_treatments | 66.7% | 100.0% | 80.0% | 2 | 1 | 0 | 2 |
| personas_roleplay | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| physics_blackholes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| physics_cosmology | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| physics_quantum | 20.0% | 100.0% | 33.3% | 1 | 4 | 0 | 1 |
| physics_violin_nanoscale | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| recipes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| repetitive_loop | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| scifi_films | 100.0% | 57.1% | 72.7% | 4 | 0 | 3 | 7 |
| scifi_films_hal9000 | 100.0% | 40.0% | 57.1% | 2 | 0 | 3 | 5 |
| scifi_films_hal9000_games | 100.0% | 100.0% | 100.0% | 11 | 0 | 0 | 11 |
| scifi_films_liu_cixin | 80.0% | 100.0% | 88.9% | 4 | 1 | 0 | 4 |
| scifi_films_space_exploration | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| statistics_multivariate | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| therapy | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| therapy_manipulation | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| wildfires_alberta | 100.0% | 80.0% | 88.9% | 4 | 0 | 1 | 5 |

### Our System - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 40.0% | 20.0% | 26.7% | 2 | 3 | 8 | 10 |
| ai_consciousness | 66.7% | 100.0% | 80.0% | 8 | 4 | 0 | 8 |
| ai_consciousness_friendship | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| ai_meta | 100.0% | 90.9% | 95.2% | 10 | 0 | 1 | 11 |
| bhutan_travel | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| chess | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 7 |
| child_nutrition | 100.0% | 33.3% | 50.0% | 2 | 0 | 4 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 33.3% | 100.0% | 50.0% | 1 | 2 | 0 | 1 |
| cookies_recipe_halving | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| cookies_recipe_halving_argument | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| cookies_recipe_halving_corrections | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| cookies_recipe_halving_math_errors | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| covid_safety | 66.7% | 100.0% | 80.0% | 6 | 3 | 0 | 6 |
| covid_safety_hiv_aids | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| dsp_wavelets | 100.0% | 45.5% | 62.5% | 5 | 0 | 6 | 11 |
| dsp_wavelets_c_code | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| electroculture | 100.0% | 57.1% | 72.7% | 4 | 0 | 3 | 7 |
| emoji_game | 100.0% | 100.0% | 100.0% | 31 | 0 | 0 | 31 |
| game_degree_guess | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| game_twenty_questions | 100.0% | 84.8% | 91.8% | 28 | 0 | 5 | 33 |
| geography_belgium | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| humanity_future_150y | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_astrology | 100.0% | 60.0% | 75.0% | 3 | 0 | 2 | 5 |
| indian_astrology_terminology | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| indian_history | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| indian_legal | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_legal_family | 100.0% | 25.0% | 40.0% | 1 | 0 | 3 | 4 |
| indian_legal_loans | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| indian_legal_loans_timeline | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| jokes | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| karnataka_elections | 100.0% | 50.0% | 66.7% | 2 | 0 | 2 | 4 |
| linux_audio | 66.7% | 66.7% | 66.7% | 2 | 1 | 1 | 3 |
| linux_audio_pipewire | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| literature_camus | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| llm_knowledge | 100.0% | 60.0% | 75.0% | 6 | 0 | 4 | 10 |
| logic_puzzle | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| lsat | 66.7% | 100.0% | 80.0% | 2 | 1 | 0 | 2 |
| lsat_medical_conference | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| medical_treatments | 66.7% | 100.0% | 80.0% | 2 | 1 | 0 | 2 |
| personas_roleplay | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| physics_blackholes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| physics_cosmology | 100.0% | 33.3% | 50.0% | 1 | 0 | 2 | 3 |
| physics_quantum | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| physics_violin_nanoscale | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| recipes | 100.0% | 50.0% | 66.7% | 1 | 0 | 1 | 2 |
| repetitive_loop | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| scifi_films | 100.0% | 14.3% | 25.0% | 1 | 0 | 6 | 7 |
| scifi_films_hal9000 | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| scifi_films_hal9000_games | 100.0% | 100.0% | 100.0% | 11 | 0 | 0 | 11 |
| scifi_films_liu_cixin | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| scifi_films_space_exploration | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| statistics_multivariate | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| therapy | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| therapy_manipulation | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| wildfires_alberta | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |

## Legacy Raw Counts (LLM Judge TP/FN)
- Baseline: TP=197, TN=0, FP=112, FN=0
- System: TP=230, TN=0, FP=79, FN=0
