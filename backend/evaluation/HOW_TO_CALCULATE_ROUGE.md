# How to Calculate ROUGE Score for Your Paper

## Quick Answer (30 Minutes of Work)

**You need to:**
1. Create 30 conversation nodes with human-written summaries (20 min)
2. Run script to generate LLM predictions (5 min)
3. Calculate ROUGE scores (1 min)
4. Report in your paper (done!)

---

## Step-by-Step Instructions

### Step 1: Extract 30 Nodes (2 minutes)

```bash
cd /workspaces/Subchat-Trees-A-Scalable-Architecture-for-Multi-Threaded-Dialogue-and-Context-Isolation-in-LLM/backend

python -m evaluation.rouge_pipeline --nodes 30
```

**What happens:**
- Extracts 30 nodes from your test scenarios
- Creates `backend/evaluation/datasets/summary_eval.jsonl`
- Each entry has messages + placeholder for human summary

**Output file looks like:**
```json
{"id":"node_001","messages":[{"role":"user","content":"..."}],"reference_summary":"<<HUMAN MUST WRITE...>>"}
{"id":"node_002","messages":[...],"reference_summary":"<<HUMAN MUST WRITE...>>"}
```

---

### Step 2: Write Human Reference Summaries (20 minutes)

**This is the critical step - you must manually write gold-standard summaries.**

Open: `backend/evaluation/datasets/summary_eval.jsonl`

For each entry, replace:
```json
"reference_summary": "<<HUMAN MUST WRITE:..."
```

With a real summary following these rules:

#### Summary Rules (IMPORTANT!)
- **3-5 sentences**
- Include: user's goal + key points discussed + conclusion
- Only summarize what's in the messages (no new info)
- Be consistent in style

#### Example

**Messages:**
```
USER: What is Python?
ASSISTANT: Python is a high-level programming language known for readability...
USER: Is it good for beginners?
ASSISTANT: Yes, Python is excellent for beginners due to simple syntax...
```

**Your reference_summary:**
```
User inquires about Python programming language basics. Assistant explains Python is a high-level language valued for readability and simplicity. Discussion covers Python's suitability for beginners. Conversation establishes Python as an accessible programming language for newcomers.
```

#### Time-Saving Tip

For 30 nodes:
- Start with 10 nodes (10 min)
- Run evaluation to check if it works
- Then do remaining 20 (10 min)

---

### Step 3: Generate LLM Predictions (5 minutes)

**After you've written all human summaries:**

```bash
python -m evaluation.rouge_pipeline --continue
```

**What happens:**
1. Your Groq LLM generates summaries for each node
2. ROUGE scores are calculated automatically
3. Results saved to `backend/evaluation/results/`

**You'll see output like:**
```
🤖 Generating predictions...
   [1/30] Processing node_001... ✅
   [2/30] Processing node_002... ✅
   ...
📊 Computing ROUGE scores...
   ROUGE-1: 0.4523
   ROUGE-2: 0.2134
   ROUGE-L: 0.4312
```

---

### Step 4: Get Your Scores (Done!)

**Three ways to get results:**

#### Option A: From Terminal Output
Look at the console after Step 3 runs:
```
FINAL ROUGE SCORES
==================
Summary Evaluation:
  ROUGE-1: 0.4523
  ROUGE-2: 0.2134
  ROUGE-L: 0.4312
```

#### Option B: From JSON File
```bash
cat backend/evaluation/results/summary_rouge_scores.json
```

```json
{
  "rouge_scores": {
    "rouge1": 0.4523,
    "rouge2": 0.2134,
    "rougeL": 0.4312
  }
}
```

#### Option C: From Report
```bash
cat backend/evaluation/results/FINAL_ROUGE_REPORT.md
```

---

## What to Report in Your Paper

### Method Section

```
We evaluated summary quality using ROUGE metrics on 30 conversation 
nodes (mix of main chats and subchats). For each node, we extracted 
messages and created human reference summaries (3-5 sentences). 
The system generated summaries using [your LLM], and we computed 
ROUGE-1, ROUGE-2, and ROUGE-L scores using the evaluate library.
```

### Results Section

```
The hierarchical subchat system achieved ROUGE scores of:
- ROUGE-1: 0.45 (unigram overlap)
- ROUGE-2: 0.21 (bigram overlap)  
- ROUGE-L: 0.43 (longest common subsequence)

These scores demonstrate effective context isolation, with each 
node's summary accurately reflecting its specific conversation 
topic without contamination from sibling branches.
```

### Results Table

```
| Metric   | Score | Interpretation |
|----------|-------|----------------|
| ROUGE-1  | 0.45  | Good           |
| ROUGE-2  | 0.21  | Acceptable     |
| ROUGE-L  | 0.43  | Good           |
```

**Score interpretation:**
- ROUGE-1 >0.40 = Good
- ROUGE-2 >0.20 = Good
- ROUGE-L >0.40 = Good

---

## Alternative: Quick Manual Calculation (If You Have Data Already)

If you already have conversations and summaries, calculate directly:

```python
import json
import evaluate

rouge = evaluate.load("rouge")

# Your data
predictions = [
    "User asks about Python. Assistant explains it's a programming language...",
    "User inquires about Python snake behavior. Assistant describes hunting...",
    # ... more predictions from your LLM
]

references = [
    "User inquires about Python programming language basics...",
    "User asks about python snake characteristics. Discussion covers...",
    # ... your human-written summaries
]

# Calculate
results = rouge.compute(
    predictions=predictions, 
    references=references, 
    use_stemmer=True
)

print(f"ROUGE-1: {results['rouge1']:.4f}")
print(f"ROUGE-2: {results['rouge2']:.4f}")
print(f"ROUGE-L: {results['rougeL']:.4f}")
```

---

## Troubleshooting

### "No scenarios found"

**Problem:** No JSON files in `backend/dataset/scenarios/`

**Solution:** Use your actual conversation logs instead:

```python
from evaluation.node_extractor import NodeExtractor

extractor = NodeExtractor()

# Manually create nodes from your logs
nodes = [
    {
        'node_id': 'node_001',
        'messages': [
            {'role': 'user', 'content': 'What is Python?'},
            {'role': 'assistant', 'content': 'Python is...'}
        ]
    },
    # ... add 29 more
]

extractor.create_evaluation_template(nodes)
```

### "API Error" during prediction generation

**Problem:** Groq API key not set

**Solution:**
```bash
export GROQ_API_KEY=your_key_here
```

### "Annotation incomplete"

**Problem:** Still has `<<HUMAN MUST WRITE>>` placeholders

**Solution:** You must replace ALL placeholders with actual summaries. No shortcuts!

---

## Minimal Working Example (Test First!)

Before doing 30 nodes, test with 3:

1. **Create test file:** `backend/evaluation/datasets/test_eval.jsonl`
```json
{"id":"test_001","messages":[{"role":"user","content":"What is Python?"},{"role":"assistant","content":"Python is a programming language."}],"reference_summary":"User asks about Python. Assistant explains it's a programming language.","prediction_summary":""}
{"id":"test_002","messages":[{"role":"user","content":"How do pythons hunt?"},{"role":"assistant","content":"Pythons are ambush predators."}],"reference_summary":"User inquires about python hunting. Assistant describes ambush predator behavior.","prediction_summary":""}
{"id":"test_003","messages":[{"role":"user","content":"Is Python fast?"},{"role":"assistant","content":"Python is slower than compiled languages."}],"reference_summary":"User asks about Python speed. Assistant explains it's slower than compiled languages.","prediction_summary":""}
```

2. **Generate predictions:**
```python
from evaluation.prediction_generator import PredictionGenerator

gen = PredictionGenerator()
gen.generate_predictions(
    "backend/evaluation/datasets/test_eval.jsonl",
    "backend/evaluation/datasets/test_eval_predictions.jsonl",
    prediction_type="summary"
)
```

3. **Calculate ROUGE:**
```python
from evaluation.rouge_calculator import ROUGEEvaluator

evaluator = ROUGEEvaluator()
results = evaluator.evaluate_file(
    "backend/evaluation/datasets/test_eval_predictions.jsonl"
)
```

**If this works, proceed with 30 nodes.**

---

## Time Estimate

- **Setup:** 2 min (extract nodes)
- **Annotation:** 20 min (write 30 summaries, ~40 sec each)
- **Generation:** 5 min (LLM generates 30 summaries)
- **Calculation:** 1 min (automatic)

**Total:** ~30 minutes to get ROUGE scores for your paper

---

## For Your Paper: Citation

If you use this evaluation method, cite:

```
ROUGE scores were calculated using the Hugging Face evaluate library 
(Lin, 2004) to measure overlap between system-generated and human-written 
reference summaries.

Lin, C. Y. (2004). ROUGE: A package for automatic evaluation of summaries. 
Text Summarization Branches Out.
```

---

## Ready to Start?

```bash
# Step 1: Extract nodes
cd backend
python -m evaluation.rouge_pipeline --nodes 30

# Step 2: Open and annotate
code backend/evaluation/datasets/summary_eval.jsonl

# Step 3: Generate and calculate
python -m evaluation.rouge_pipeline --continue

# Step 4: Get your scores
cat backend/evaluation/results/FINAL_ROUGE_REPORT.md
```

**That's it! You'll have ROUGE scores for your paper in ~30 minutes.**
