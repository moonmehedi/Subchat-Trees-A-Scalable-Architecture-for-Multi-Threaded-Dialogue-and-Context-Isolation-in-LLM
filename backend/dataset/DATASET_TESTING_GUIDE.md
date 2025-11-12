# Dataset Testing Guide

## 🚀 Quick Start

### Prerequisites

1. **Backend server running** on `http://localhost:8000`
2. **Python dependencies installed**:
   ```bash
   cd backend
   pip install colorama  # For colored terminal output
   ```

### Run All Scenarios

```bash
cd backend/dataset
python run_dataset.py
```

This will:
- Execute all 12 scenarios sequentially
- Validate 38+ retrieval tests
- Test context isolation
- Generate comprehensive reports
- Save logs to `logs/dataset-results/`

### Run Specific Scenario

```bash
# Run just the Python ambiguity test
python run_dataset.py --scenario 02_python_ambiguity

# Run without delays (faster but may hit rate limits)
python run_dataset.py --skip-delay

# Use different API URL
python run_dataset.py --base-url http://localhost:3000
```

---

## 📁 File Structure

```
backend/dataset/
├── run_dataset.py              # Main execution script
├── dataset_logger.py           # Logging and validation
├── DATASET_STRUCTURE.md        # Visual tree documentation
├── DATASET_TESTING_GUIDE.md    # This file
│
├── scenarios/                  # Test scenarios (JSON)
│   ├── 01_personal_intro.json
│   ├── 02_python_ambiguity.json
│   ├── 03_quantum_project.json
│   ├── 04_adhd_support.json
│   ├── 05_travel_stories.json
│   ├── 06_cooking_recipes.json
│   ├── 07_fitness_journey.json
│   ├── 08_tech_stack.json
│   ├── 09_book_recommendations.json
│   ├── 10_career_goals.json
│   ├── 11_music_preferences.json
│   └── 12_coding_challenges.json
│
└── logs/dataset-results/       # Generated during execution
    ├── scenarios/              # Per-scenario JSON logs
    │   ├── Personal_Introduction_&_Hobbies.json
    │   ├── Python_Ambiguity_-_Context_Isolation_Test.json
    │   └── ...
    ├── FINAL_REPORT_[timestamp].txt
    └── results_[timestamp].json
```

---

## 📊 Understanding Results

### Terminal Output

During execution, you'll see:

```
================================================================================
🧪 SCENARIO: Python Ambiguity - Context Isolation Test
Tests context isolation between main tree and subchats when discussing 'python' (snake vs programming)
================================================================================

[Step 1] MAIN
  User: How do you kill a python snake safely?
  AI: Python snakes are constrictors and not venomous...

✅ TEST PASSED (Step 7): response_check

[Step 4] ACTION: CREATE_SUBCHAT
  Creating subchat 'Python Programming' from main

[Step 13] SUBCHAT_1
  User: What did I ask about Python earlier in this conversation?
  AI: You asked about writing Python code for beginners...

✅ TEST PASSED (Step 13): context_isolation

--------------------------------------------------------------------------------
📊 SCENARIO SUMMARY: Python Ambiguity - Context Isolation Test
  Duration: 15.34s
  Total Tests: 3
  ✅ Passed: 3/3 (100%)
--------------------------------------------------------------------------------
```

### Test Status Icons

- ✅ **Green checkmark**: Test passed
- ❌ **Red X**: Test failed
- ⚠️ **Yellow warning**: Non-critical issue
- 🧪 **Test tube**: Scenario started
- 📊 **Chart**: Summary/report

### What Gets Validated

1. **Expected Keywords** (`expected_response_contains`):
   - Checks if AI response contains specific words
   - Example: "What's my name?" should contain "Alex"

2. **Forbidden Keywords** (`should_not_contain`):
   - Checks for context pollution
   - Example: Programming subchat shouldn't mention "snake"

3. **Retrieval Keywords** (`expected_retrieval`):
   - Verifies RAG retrieved correct information
   - Example: "favorite food" should retrieve "paella"

---

## 📈 Final Report

After all scenarios complete, you'll get:

### Console Report

```
================================================================================
📋 DATASET TESTING FINAL REPORT
================================================================================
Generated: 2025-10-05 14:30:45

📊 OVERALL STATISTICS
--------------------------------------------------------------------------------
Total Scenarios: 12
Total Tests: 38
✅ Passed: 36 (94.7%)
❌ Failed: 2 (5.3%)
⏱️  Total Duration: 180.45s (3.01 minutes)

🧪 SCENARIO BREAKDOWN
--------------------------------------------------------------------------------

1. ✅ Personal Introduction & Hobbies
   Tests: 3/3 passed (100%)
   Duration: 12.34s

2. ❌ Python Ambiguity - Context Isolation Test
   Tests: 2/3 passed (66.7%)
   Duration: 15.67s
   Failures:
     ❌ Step 13: context_isolation
        └─ Found forbidden keyword: 'snake' (context pollution)

... (continues for all scenarios)

================================================================================
⚠️  SOME TESTS FAILED
Please review the failures above and check logs for details.
================================================================================
```

### Generated Files

1. **`FINAL_REPORT_[timestamp].txt`**
   - Human-readable summary
   - All pass/fail details
   - Failure explanations

2. **`results_[timestamp].json`**
   - Machine-readable results
   - Detailed test data
   - Can be parsed by other tools

3. **`scenarios/[Scenario_Name].json`**
   - Per-scenario detailed logs
   - Every message and response
   - Timestamps for debugging

---

## 🔍 Debugging Failed Tests

### Step 1: Check the Final Report

Look at which tests failed and why:

```
❌ Step 13: context_isolation
   └─ Found forbidden keyword: 'snake' (context pollution)
```

This tells you:
- **Step 13**: Which conversation turn failed
- **context_isolation**: Type of test
- **'snake'**: The problematic keyword found

### Step 2: Check Scenario Log

Open the specific scenario JSON:

```bash
cat logs/dataset-results/scenarios/Python_Ambiguity_-_Context_Isolation_Test.json
```

Look for the failing test:

```json
{
  "step": 13,
  "type": "context_isolation",
  "query": "What did I ask about Python earlier?",
  "response": "You asked about python snakes and how to handle them...",
  "passed": false,
  "failures": [
    "Found forbidden keyword: 'snake' (context pollution)"
  ]
}
```

This shows the **exact response** that caused the failure.

### Step 3: Check Component Logs

The system also generates detailed logs in `logs/component-testing/`:

```bash
# Check what was retrieved
cat logs/component-testing/RETRIEVAL.log

# Check buffer state
cat logs/component-testing/BUFFER.log

# Check vector store contents
cat logs/component-testing/VECTOR_STORE.log
```

### Step 4: Identify Root Cause

Common failure patterns:

| Failure Message | Root Cause | Where to Look |
|----------------|------------|---------------|
| Missing expected keyword: 'X' | RAG didn't retrieve the right info | `RETRIEVAL.log` - check sub-queries |
| Found forbidden keyword: 'X' | Context pollution between trees | `BUFFER.log` - check node isolation |
| Expected retrieval keyword not found | Message not in vector store | `VECTOR_STORE.log` - verify indexing |
| No response / timeout | API issue | Check server logs |

---

## 🎯 Critical Tests

### Context Isolation Tests

These are the most important tests - they verify that subchats don't leak context:

1. **Scenario 2: Python Ambiguity**
   - Main: Snake discussions
   - Subchat 1: Programming discussions
   - **Critical**: Programming subchat should NOT mention snakes

2. **Scenario 4: ADHD Support**
   - Main: General ADHD info
   - Subchat: Personal ADHD struggles
   - **Critical**: Main tree should NOT know personal details

3. **Scenario 5: Travel Stories**
   - Main: Japan trip (2023)
   - Subchat: Italy plans (2026)
   - **Critical**: Italy subchat should NOT mention Japan

### Retrieval Accuracy Tests

Verify RAG finds correct information:

- **Exact facts**: "What's my name?" → "Alex Rodriguez"
- **Numbers**: "How many qubits?" → "8"
- **Technical terms**: "Which algorithms?" → "Grover's, Shor's"
- **Preferences**: "Favorite genre?" → "Progressive rock"

### Long-term Memory Tests

Information from >10 messages ago:

- **Scenario 1**: Ask about name after 6 other messages
- **Scenario 6**: Ask about cookie secret after 8 other messages
- **Scenario 11**: Ask about concerts after 9 other messages

---

## 🛠️ Troubleshooting

### "Cannot connect to API"

```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it
cd backend
uvicorn main:app --reload
```

### "ModuleNotFoundError: No module named 'colorama'"

```bash
pip install colorama
```

### Tests are failing but logs look correct

1. Check if keywords are case-sensitive (they're not - we use `.lower()`)
2. Verify partial matches (we use `in` operator, not exact match)
3. Check for typos in expected keywords in scenario JSON

### Rate limit errors (429)

```bash
# Add delays between requests
python run_dataset.py  # Default 1s delay

# Or reduce delay (may cause issues)
python run_dataset.py --skip-delay  # No delays
```

### Vector store seems empty

```bash
# Check if database mode is "research" (clears on restart)
grep "MODE" backend/src/models/tree.py

# If research mode, vector store clears on server restart
# Re-run the dataset to repopulate
```

---

## 📋 Expected Results

If everything works perfectly:

```
✅ ALL TESTS PASSED!
The hierarchical subchat system is working perfectly! ✨
```

This means:
- ✅ Context isolation works (no pollution between trees)
- ✅ RAG retrieval is accurate (finds correct information)
- ✅ Buffer management works (10 messages per node)
- ✅ Sub-query generation is semantic (relevant queries)
- ✅ Re-ranking prioritizes correctly
- ✅ Long-term memory works (facts from >10 messages ago)

---

## 🔬 Advanced Usage

### Run Scenarios in Different Order

```bash
python run_dataset.py --scenario 12_coding_challenges
python run_dataset.py --scenario 02_python_ambiguity
# etc.
```

### Modify Scenarios

Edit JSON files in `scenarios/` to:
- Add more test cases
- Change expected keywords
- Adjust conversation flow
- Add new topics

### Parse Results Programmatically

```python
import json

with open('logs/dataset-results/results_[timestamp].json') as f:
    results = json.load(f)

# Get pass rate
pass_rate = results['pass_rate']

# Get failed scenarios
failed = [s for s in results['scenarios'] if s['failed'] > 0]

# Print failure details
for scenario in failed:
    print(f"Scenario: {scenario['name']}")
    for test in scenario['tests']:
        if not test['passed']:
            print(f"  Failed: {test['query']}")
            print(f"  Reason: {test['failures']}")
```

---

## 📞 Support

If tests are consistently failing:

1. **Check component logs** in `logs/component-testing/`
2. **Review RETRIEVAL.log** to see what's being retrieved
3. **Check VECTOR_STORE.log** to verify indexing
4. **Examine BUFFER.log** to see buffer state
5. **Read COT_THINKING.log** to see LLM decisions

The enhanced logging system will show you exactly where things are breaking! 🔍
