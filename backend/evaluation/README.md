# ROUGE Evaluation - Your Exact Specifications Implemented

This implements your ROUGE evaluation requirements exactly as you described.

## ✅ What's Implemented

All steps from your instructions:

### Step 1: Definition ✅
- **Summary of a node** = summary of all messages inside that node only
- **Max messages**: Last 20 messages
- **Node-only** (not path summary)

### Step 2: Collect Examples ✅
Script: `node_extractor.py`
- Picks 30 nodes (mix of main + subchats + sub-subchats)
- Saves: node_id, messages list (role + content)
- Creates: `summary_eval.jsonl`

### Step 3: Human Reference Summaries ✅
Format: JSONL with placeholders
- You must write `reference_summary` for each node
- Rules:
  - 3-5 sentences
  - Include: user goal + key points + conclusion
  - Don't add new info not in chat

### Step 4: Generate Model Summaries ✅
Script: `prediction_generator.py`
- Uses your Groq LLM
- Prompt: "Summarize this conversation in 3-5 sentences focusing on intent, key facts, and conclusion"
- Saves as `prediction_summary`

### Step 5: Compute ROUGE ✅
Script: `rouge_calculator.py`
- Library: Hugging Face `evaluate`
- Code exactly as you specified:
```python
import json, evaluate

rouge = evaluate.load("rouge")

preds, refs = [], []
with open("summary_eval.jsonl","r",encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        preds.append(row["prediction_summary"])
        refs.append(row["reference_summary"])

print(rouge.compute(predictions=preds, references=refs, use_stemmer=True))
```

### Step 6: Report Final Score ✅
Reports:
- ROUGE-1
- ROUGE-2
- ROUGE-L
- Number of nodes evaluated (N)
- Summary length constraint (3-5 sentences)
- Whether summarized node-only or path (node-only)

## 🚀 How to Use

### Step 1-2: Extract Nodes and Create Template

```bash
cd backend
python -m evaluation.rouge_pipeline --nodes 30
```

This creates `backend/evaluation/datasets/summary_eval.jsonl` with 30 nodes.

### Step 3: Annotate (Human Work Required)

Open `backend/evaluation/datasets/summary_eval.jsonl` and replace:

```json
"reference_summary": "<<HUMAN MUST WRITE:..."
```

With actual summaries following the rules:
- 3-5 sentences
- User goal + key points + conclusion
- No new information

Example:
```json
"reference_summary": "User inquires about Python programming language basics. Assistant explains Python is a high-level, interpreted language known for readability. Discussion covers Python's use in data science and web development. Conversation establishes foundational understanding of Python's versatility and beginner-friendliness."
```

### Step 4-6: Generate Predictions and Calculate ROUGE

After annotation is complete:

```bash
python -m evaluation.rouge_pipeline --continue
```

This will:
1. Generate model summaries using your Groq LLM
2. Compute ROUGE scores
3. Generate final report

## 📊 Output Files

```
backend/evaluation/
├── datasets/
│   ├── summary_eval.jsonl              # After Step 2 (template)
│   ├── summary_eval_predictions.jsonl  # After Step 4 (with predictions)
│   └── title_eval_predictions.jsonl    # Bonus: title evaluation
└── results/
    ├── summary_rouge_scores.json       # ROUGE scores as JSON
    ├── title_rouge_scores.json         # Title ROUGE scores
    └── FINAL_ROUGE_REPORT.md           # Human-readable report
```

## What Makes This "Hierarchical"?

Your project's key novelty is **context isolation**. We evaluate on nodes that include:

- Main chat about "Python programming"
- Subchat about "Python snake"  
- Another subchat about "use of Python"

**Expected result:**
- Summary for main chat = programming only
- Summary for subchat = snake only
- No contamination between branches

**If context isolation works:** ROUGE scores will be high (>0.4) because summaries match references.

**If context bleeds:** ROUGE scores drop because summaries mix topics.

## Minimal Checklist (Your Exact Words)

- [x] Pick 30 nodes (mix of main + subchats + sub-subchats)
- [x] Export messages for each node into summary_eval.jsonl
- [ ] Write reference_summary for each (HUMAN WORK)
- [x] Generate prediction_summary using your LLM summarizer
- [x] Compute ROUGE and average
- [x] Same steps for titles

## Libraries Used

✅ `evaluate` (easiest, as you recommended)

## File Schema

### summary_eval.jsonl (After annotation)
```json
{"id":"node_001","messages":[{"role":"user","content":"..."},{"role":"assistant","content":"..."}],"reference_summary":"..."}
{"id":"node_002","messages":[{"role":"user","content":"..."}],"reference_summary":"..."}
```

### summary_eval_predictions.jsonl (After Step 4)
```json
{"id":"node_001","messages":[...],"reference_summary":"...","prediction_summary":"..."}
```

## Quick Start

```bash
# Install dependency
pip install --no-cache-dir evaluate

# Run Steps 1-2 (extract nodes)
cd backend
python -m evaluation.rouge_pipeline --nodes 30

# Do Step 3 (human annotation) manually
# Edit backend/evaluation/datasets/summary_eval.jsonl

# Run Steps 4-6 (predict + evaluate)
python -m evaluation.rouge_pipeline --continue
```

## Expected ROUGE Scores

If context isolation works:
- ROUGE-1: >0.40 (good)
- ROUGE-2: >0.20 (good)
- ROUGE-L: >0.40 (good)

If context bleeds:
- ROUGE-1: <0.30 (poor)
- ROUGE-2: <0.15 (poor)

---

**This implements your exact specifications. No extra features, just what you asked for.**
