# TABLE 1: CONTEXT ISOLATION METRICS (Buffer Size: 5)

## Weighted Average Metrics (Per-Topic Confusion Matrix)

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Precision** | 64.5% | 77.8% | **+20.6%** |
| **Recall** | 52.6% | 74.4% | **+41.4%** |
| **F1** | 51.2% | 73.9% | **+44.3%** |
| **Accuracy** | 52.8% | 74.4% | **+41.1%** |
| **Pollution Rate** | 47.2% | 25.6% | **-45.9%** |

## Macro Average Metrics

| Metric | Baseline System | Our System | Improvement |
|--------|----------------|------------|-------------|
| **Macro Precision** | 52.0% | 67.5% | **+29.7%** |
| **Macro Recall** | 52.7% | 68.5% | **+30.1%** |
| **Macro F1** | 48.3% | 65.8% | **+36.1%** |

## Per-Topic Breakdown


### Baseline - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 0.0% | 0.0% | 0.0% | 0 | 0 | 10 | 10 |
| ai_consciousness | 0.0% | 0.0% | 0.0% | 0 | 0 | 8 | 8 |
| ai_consciousness_friendship | 13.3% | 66.7% | 22.2% | 4 | 26 | 2 | 6 |
| ai_meta | 43.5% | 90.9% | 58.8% | 10 | 13 | 1 | 11 |
| bhutan_travel | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| chess | 100.0% | 57.1% | 72.7% | 4 | 0 | 3 | 7 |
| child_nutrition | 100.0% | 50.0% | 66.7% | 3 | 0 | 3 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 33.3% | 100.0% | 50.0% | 1 | 2 | 0 | 1 |
| cookies_recipe_halving | 16.7% | 66.7% | 26.7% | 2 | 10 | 1 | 3 |
| cookies_recipe_halving_argument | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_corrections | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_math_errors | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| covid_safety | 60.0% | 100.0% | 75.0% | 6 | 4 | 0 | 6 |
| covid_safety_hiv_aids | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| dsp_wavelets | 80.0% | 72.7% | 76.2% | 8 | 2 | 3 | 11 |
| dsp_wavelets_c_code | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| electroculture | 85.7% | 85.7% | 85.7% | 6 | 1 | 1 | 7 |
| emoji_game | 100.0% | 100.0% | 100.0% | 31 | 0 | 0 | 31 |
| game_degree_guess | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| game_twenty_questions | 100.0% | 12.1% | 21.6% | 4 | 0 | 29 | 33 |
| geography_belgium | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| humanity_future_150y | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| indian_astrology | 83.3% | 100.0% | 90.9% | 5 | 1 | 0 | 5 |
| indian_astrology_terminology | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| indian_history | 60.0% | 100.0% | 75.0% | 3 | 2 | 0 | 3 |
| indian_legal | 40.0% | 50.0% | 44.4% | 2 | 3 | 2 | 4 |
| indian_legal_family | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| indian_legal_loans | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| indian_legal_loans_timeline | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| jokes | 100.0% | 16.7% | 28.6% | 1 | 0 | 5 | 6 |
| karnataka_elections | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| linux_audio | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| linux_audio_pipewire | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| literature_camus | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| llm_knowledge | 100.0% | 30.0% | 46.2% | 3 | 0 | 7 | 10 |
| logic_puzzle | 40.0% | 100.0% | 57.1% | 4 | 6 | 0 | 4 |
| lsat | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| lsat_medical_conference | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| lsat_piano_recital | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| medical_treatments | 50.0% | 100.0% | 66.7% | 2 | 2 | 0 | 2 |
| personas_roleplay | 75.0% | 100.0% | 85.7% | 6 | 2 | 0 | 6 |
| physics_blackholes | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| physics_cosmology | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| recipes | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| repetitive_loop | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| scifi_films | 28.6% | 28.6% | 28.6% | 2 | 5 | 5 | 7 |
| scifi_films_hal9000 | 100.0% | 60.0% | 75.0% | 3 | 0 | 2 | 5 |
| scifi_films_hal9000_games | 100.0% | 36.4% | 53.3% | 4 | 0 | 7 | 11 |
| scifi_films_liu_cixin | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| scifi_films_space_exploration | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| statistics_multivariate | 66.7% | 100.0% | 80.0% | 2 | 1 | 0 | 2 |
| therapy | 42.9% | 100.0% | 60.0% | 3 | 4 | 0 | 3 |
| therapy_manipulation | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| wildfires_alberta | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |

### Our System - Per-Topic Metrics

| Topic | Precision | Recall | F1 | TP | FP | FN | Support |
|-------|-----------|--------|----|----|----|----|--------|
| ai_chat_tools | 100.0% | 100.0% | 100.0% | 10 | 0 | 0 | 10 |
| ai_consciousness | 40.0% | 100.0% | 57.1% | 8 | 12 | 0 | 8 |
| ai_consciousness_friendship | 0.0% | 0.0% | 0.0% | 0 | 0 | 6 | 6 |
| ai_meta | 100.0% | 90.9% | 95.2% | 10 | 0 | 1 | 11 |
| bhutan_travel | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| chess | 100.0% | 85.7% | 92.3% | 6 | 0 | 1 | 7 |
| child_nutrition | 100.0% | 50.0% | 66.7% | 3 | 0 | 3 | 6 |
| cookies_preferences | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| cookies_recipe | 33.3% | 100.0% | 50.0% | 1 | 2 | 0 | 1 |
| cookies_recipe_halving | 50.0% | 33.3% | 40.0% | 1 | 1 | 2 | 3 |
| cookies_recipe_halving_argument | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_corrections | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| cookies_recipe_halving_math_errors | 33.3% | 75.0% | 46.2% | 3 | 6 | 1 | 4 |
| covid_safety | 60.0% | 100.0% | 75.0% | 6 | 4 | 0 | 6 |
| covid_safety_hiv_aids | 0.0% | 0.0% | 0.0% | 0 | 0 | 7 | 7 |
| dsp_wavelets | 100.0% | 27.3% | 42.9% | 3 | 0 | 8 | 11 |
| dsp_wavelets_c_code | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| electroculture | 100.0% | 85.7% | 92.3% | 6 | 0 | 1 | 7 |
| emoji_game | 100.0% | 100.0% | 100.0% | 31 | 0 | 0 | 31 |
| game_degree_guess | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| game_twenty_questions | 100.0% | 87.9% | 93.5% | 29 | 0 | 4 | 33 |
| geography_belgium | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| humanity_future_150y | 80.0% | 100.0% | 88.9% | 4 | 1 | 0 | 4 |
| indian_astrology | 83.3% | 100.0% | 90.9% | 5 | 1 | 0 | 5 |
| indian_astrology_terminology | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| indian_history | 75.0% | 100.0% | 85.7% | 3 | 1 | 0 | 3 |
| indian_legal | 50.0% | 50.0% | 50.0% | 2 | 2 | 2 | 4 |
| indian_legal_family | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| indian_legal_loans | 0.0% | 0.0% | 0.0% | 0 | 0 | 2 | 2 |
| indian_legal_loans_timeline | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| jokes | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| karnataka_elections | 100.0% | 75.0% | 85.7% | 3 | 0 | 1 | 4 |
| linux_audio | 100.0% | 100.0% | 100.0% | 3 | 0 | 0 | 3 |
| linux_audio_pipewire | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| literature_camus | 100.0% | 66.7% | 80.0% | 4 | 0 | 2 | 6 |
| llm_knowledge | 100.0% | 80.0% | 88.9% | 8 | 0 | 2 | 10 |
| logic_puzzle | 100.0% | 100.0% | 100.0% | 4 | 0 | 0 | 4 |
| lsat | 66.7% | 100.0% | 80.0% | 2 | 1 | 0 | 2 |
| lsat_medical_conference | 0.0% | 0.0% | 0.0% | 0 | 0 | 3 | 3 |
| lsat_piano_recital | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| lsat_product_codes | 0.0% | 0.0% | 0.0% | 0 | 0 | 5 | 5 |
| medical_dsd | 100.0% | 83.3% | 90.9% | 5 | 0 | 1 | 6 |
| medical_treatments | 40.0% | 100.0% | 57.1% | 2 | 3 | 0 | 2 |
| personas_roleplay | 100.0% | 100.0% | 100.0% | 6 | 0 | 0 | 6 |
| physics_blackholes | 66.7% | 100.0% | 80.0% | 2 | 1 | 0 | 2 |
| physics_cosmology | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| physics_quantum | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| physics_violin_nanoscale | 100.0% | 66.7% | 80.0% | 2 | 0 | 1 | 3 |
| recipes | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| repetitive_loop | 0.0% | 0.0% | 0.0% | 0 | 0 | 1 | 1 |
| scifi_films | 60.0% | 85.7% | 70.6% | 6 | 4 | 1 | 7 |
| scifi_films_hal9000 | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |
| scifi_films_hal9000_games | 100.0% | 100.0% | 100.0% | 11 | 0 | 0 | 11 |
| scifi_films_liu_cixin | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| scifi_films_space_exploration | 100.0% | 100.0% | 100.0% | 1 | 0 | 0 | 1 |
| statistics_multivariate | 100.0% | 100.0% | 100.0% | 2 | 0 | 0 | 2 |
| therapy | 42.9% | 100.0% | 60.0% | 3 | 4 | 0 | 3 |
| therapy_manipulation | 0.0% | 0.0% | 0.0% | 0 | 0 | 4 | 4 |
| wildfires_alberta | 100.0% | 100.0% | 100.0% | 5 | 0 | 0 | 5 |

## Legacy Raw Counts (LLM Judge TP/FN)
- Baseline: TP=163, TN=0, FP=146, FN=0
- System: TP=230, TN=0, FP=79, FN=0
