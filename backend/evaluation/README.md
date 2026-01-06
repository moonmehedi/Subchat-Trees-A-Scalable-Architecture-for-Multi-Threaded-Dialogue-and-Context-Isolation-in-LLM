# Multi-Metric Summary Evaluation System

Comprehensive evaluation using **ROUGE**, **METEOR**, and **BERTScore** for branch-level conversation summaries.

## 🎯 What This Evaluates

**Branch-level conversation summaries** in hierarchical subchat trees:
- ✅ **ROUGE**: Lexical overlap (n-gram matching)
- ✅ **METEOR**: Alignment with synonym matching via WordNet
- ✅ **BERTScore**: Semantic similarity using contextual embeddings

## ⚡ Quick Start (2.5 hours total)

### 1. Install Dependencies (5 min)

```bash
cd backend/evaluation
pip install -r requirements.txt
```

### 2. Extract 30 Nodes (2 min)

```bash
cd ..
python -m evaluation.rouge_pipeline --nodes 30
```

Creates `backend/evaluation/datasets/summary_eval.jsonl`

### 3. Write Reference Summaries (2 hours)

Open `summary_eval.jsonl` and replace:
```json
"reference_summary": "<<HUMAN MUST WRITE..."
```

With 3-5 sentence summaries (user goal + key points + conclusion)

### 4. Run Evaluation (15 min)

```bash
python -m evaluation.rouge_pipeline --continue --use-all-metrics
```

Generates paper-ready results with all three metrics!

---

## 📊 Expected Scores

### Good Performance (context isolation working):
- **ROUGE-1**: >0.40 | **ROUGE-2**: >0.20 | **ROUGE-L**: >0.40
- **METEOR**: >0.35 | **BERTScore F1**: >0.85

### Poor Performance (context bleeding):
- **ROUGE-1**: <0.30 | **ROUGE-2**: <0.15 | **ROUGE-L**: <0.30
- **METEOR**: <0.25 | **BERTScore F1**: <0.75

---

## 📁 Files

- **summary_evaluator.py**: Multi-metric evaluation engine
- **rouge_pipeline.py**: End-to-end orchestration
- **prediction_generator.py**: LLM prediction generation
- **requirements.txt**: All dependencies

**Documentation:**
- **HOW_TO_CALCULATE_ROUGE.md**: Step-by-step tutorial
- **PAPER_WRITING_GUIDE.md**: LaTeX templates for your paper
- **QUICK_REFERENCE.md**: Decision tree
- **REFERENCE_SUMMARY_OPTIONS.md**: Annotation guidelines

---

## 🔬 For Your Paper

After running evaluation, use the generated LaTeX table:

```latex
\begin{table}[h]
\centering
\caption{Summary quality on hierarchical dataset (N=30)}
\begin{tabular}{lcccccc}
\hline
\textbf{Method} & \textbf{R-1} & \textbf{R-2} & \textbf{R-L} & \textbf{METEOR} & \textbf{BERTScore} \\
\hline
Subchat Trees & 0.45 & 0.21 & 0.43 & 0.38 & 0.87 \\
\hline
\end{tabular}
\end{table}
```

**Why three metrics?** ROUGE (lexical) + METEOR (paraphrasing) + BERTScore (semantic) = comprehensive evaluation following modern NLP standards.
