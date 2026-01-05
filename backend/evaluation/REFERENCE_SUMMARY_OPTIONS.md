# Reference Summary Options for ROUGE Evaluation

## ❓ Do I REALLY need human-written summaries?

**Short answer:** Yes, in principle — but there are practical alternatives.

ROUGE is defined as **overlap between system output and reference summaries**. Without reference text, ROUGE has no meaning. However, the reference doesn't have to be written entirely by you.

---

## 📊 Options Ranked (Best → Weakest)

### ✅ Option A: Use Public Datasets (BEST, if applicable)

**What it is:**
- Use existing datasets with human-written summaries
- Examples: SAMSum (dialogue), DialogSum (conversations), CNN/DailyMail (documents)

**How to adapt for your hierarchical system:**
1. Treat each dialogue/segment as a "branch"
2. Generate summaries with:
   - Linear context (baseline)
   - Hierarchical context (your method)
3. Compare both against existing human summaries

**✅ Pros:**
- Gold summaries already exist
- Reviewers LOVE this
- No annotation effort
- Proves generalization

**❌ Cons:**
- Dataset not naturally hierarchical
- Less "native" to your system

**💡 Best for:**
- Additional benchmark (not your only evaluation)
- Proving generalization to standard datasets

**Paper wording:**
```
We additionally evaluate on SAMSum dialogue dataset (Gliwa et al., 
2019) to demonstrate generalization. We compare linear vs hierarchical 
context generation against existing human reference summaries.
```

---

### ✅ Option B: Small Human-Written Set (MOST COMMON - RECOMMENDED!)

**What it is:**
- YOU write 20-50 reference summaries
- This is what **most applied LLM papers actually do**, even in top venues

**Typical workflow:**
1. Extract 30 conversation branches
2. Write 3-5 sentence summaries for each
3. Takes ~2 hours total (~3-5 min per summary)
4. Call it "human-annotated evaluation set"

**✅ Pros:**
- **Strong and defensible**
- Reviewers accept it universally
- Fully aligned with ROUGE definition
- Custom to your hierarchical architecture

**❌ Cons:**
- Requires ~2 hours of manual work

**💡 Best for:**
- Main evaluation (PRIMARY RECOMMENDATION)
- Your core ROUGE table

**Paper wording (copy-paste ready):**
```
For evaluation, we construct a human-annotated dataset consisting 
of 30 conversation branches sampled from multiple hierarchical 
subchat trees. Each branch is paired with a reference summary 
written by the authors, capturing the user intent, key discussion 
points, and final outcome. We report ROUGE-1, ROUGE-2, and ROUGE-L 
F1 scores by comparing model-generated summaries against these 
references.
```

**How much is "enough"?**
- 20-30 examples → **acceptable**
- 50+ examples → **strong**
- 100+ → **excellent**

**Truth:** You can finish 30 summaries in ~2 hours. This is the gold standard.

---

### ⚠️ Option C: LLM-Generated Pseudo-Gold (WEAKER, use with caution)

**What it is:**
- Generate reference summaries using GPT-4/Claude/Gemini
- Freeze them as "pseudo-references" (also called "silver standard")
- Use for ROUGE calculation

**How to do it properly:**
1. Use a **stronger model** than what you're evaluating
2. Use very constrained, consistent prompts
3. **Manually inspect/edit** at least 10% of examples
4. **Clearly disclose** this in your paper

**✅ Pros:**
- No manual annotation time
- Can create large sets quickly

**❌ Cons:**
- Some reviewers will criticize it
- Not "true" gold standard
- Circular if you're evaluating LLM quality

**⚠️ Reviewer risk:**
- Acceptable for **workshops/early venues**
- **Not ideal for top-tier journals**
- Must be framed as "approximate evaluation"

**Paper wording (CRITICAL - must disclose!):**
```
Due to the absence of human reference summaries for our novel 
hierarchical architecture, we use high-quality LLM-generated 
summaries (GPT-4) as pseudo-references for ROUGE evaluation. 
We manually verified a random sample of 20% to ensure quality.
```

**💡 When to use:**
- Supplementary to human-written set
- Large-scale experiments
- Workshop papers / preprints

---

### ❌ Option D: No Reference Summaries

**❌ NOT VALID**

ROUGE without references is meaningless. Reviewers will reject immediately.

---

## 🎯 RECOMMENDED STRATEGY (Hybrid Approach)

For your hierarchical subchat trees paper, use **both Option A + Option B**:

### Primary Evaluation (Main Table):
- **30 human-written summaries** on your hierarchical data
- 2 hours of work
- Shows your architecture's native performance

### Secondary Evaluation (Generalization):
- **SAMSum or DialogSum dataset** (public)
- Zero annotation effort
- Proves method works on standard benchmarks

**Why this is powerful:**
1. Primary eval is custom → shows architecture strength
2. Secondary eval is standard → proves generalization
3. Reviewers see both rigor and broad applicability

**Paper structure:**
```latex
\subsection{Evaluation Setup}

\textbf{Primary Evaluation:} We construct a human-annotated dataset 
of 30 hierarchical conversation branches with reference summaries 
written by the authors (3-5 sentences each).

\textbf{Generalization Evaluation:} We additionally evaluate on 
SAMSum dialogue dataset (N=500 samples) to demonstrate performance 
on standard benchmarks.

[Table 1: ROUGE scores on hierarchical dataset]
[Table 2: ROUGE scores on SAMSum dataset]
```

---

## 📏 Quality Guidelines for Writing Summaries

When writing your 30 reference summaries:

**✅ DO:**
- Capture user intent / goal
- Include key discussion points
- State final outcome / conclusion
- Keep 3-5 sentences
- Use information ONLY from the branch
- Be consistent in style

**❌ DON'T:**
- Add information not in conversation
- Copy-paste from messages verbatim
- Write opinion/analysis
- Vary length dramatically
- Rush through (take 3-5 min each)

**Example template:**
```
User [goal]. Assistant [explains X and Y]. Discussion covers [key points]. 
User [final question/decision]. Conversation concludes with [outcome].
```

---

## ⚙️ Implementation in This Codebase

### Option B (Human-Written) - PRIMARY:
```bash
# Extract nodes
python -m evaluation.rouge_pipeline --nodes 30

# Manually edit summary_eval.jsonl
# Write 30 reference summaries (~2 hours)

# Continue with evaluation
python -m evaluation.rouge_pipeline --continue
```

### Option C (Pseudo-Gold) - OPTIONAL:
We can add a script that generates pseudo-references using GPT-4:

```bash
# Generate pseudo-gold summaries (if you choose this option)
python -m evaluation.generate_pseudo_references --model gpt-4 --nodes 30

# Then manually inspect 10% before using
```

**Note:** This is NOT currently implemented. Ask if you want this option.

---

## 🧠 Important Research Truth

### ROUGE is not mandatory for LLM papers

Your contribution is **context isolation architecture**, not summarization quality alone.

ROUGE supports your claim — it doesn't define it.

**What reviewers expect:**
- Qualitative analysis (main evidence)
- Architectural ablations (proof of design choices)
- ROUGE scores (quantitative support)
- Optional: User studies

ROUGE is **one piece of evidence**, not the whole evaluation.

---

## ✅ Final Recommendations

### For Your First Submission:

**Must Have:**
1. **30 human-written reference summaries** (2 hours)
   - Your main ROUGE table
   - Gold standard
   - Reviewers accept universally

**Nice to Have:**
2. **Public dataset evaluation** (SAMSum/DialogSum)
   - Proves generalization
   - Zero extra annotation
   - Strengthens paper

**Skip:**
3. LLM pseudo-gold (unless desperate for time)
   - Some reviewers criticize
   - Not worth the risk for first submission

---

## 📝 Time Investment Summary

| Option | Time Required | Reviewer Acceptance | Use Case |
|--------|---------------|---------------------|----------|
| Option A (Public dataset) | 0 hrs | ⭐⭐⭐⭐⭐ High | Secondary eval |
| Option B (Human-written) | 2 hrs | ⭐⭐⭐⭐⭐ High | **Primary eval** |
| Option C (Pseudo-gold) | 0.5 hrs | ⭐⭐⭐ Medium | Workshop only |
| Option D (None) | 0 hrs | ❌ Reject | Never |

---

## 🎯 Bottom Line

✅ **Yes, you need reference summaries for valid ROUGE**

✅ **Best option: Write 30 yourself (~2 hours)**

✅ **Boost with public dataset (SAMSum) for generalization**

✅ **Avoid pseudo-gold for first journal submission**

**Your 2-hour investment in writing summaries = publication-quality evaluation.**

Do it once, use it forever in your paper. Worth it.

---

## 🗓️ Practical Timeline for Complete Evaluation

### Option 1: Human-Written Only (~2.5 hours)
```
Hour 0-0.5: Extract 30 nodes, review conversations
Hour 0.5-2.5: Write 30 reference summaries (5 min each)
Hour 2.5-2.6: Run LLM prediction generation
Hour 2.6-2.7: Calculate ROUGE scores
Total: ~2.5 hours → Publication-ready results
```

### Option 2: Hybrid (Human + Public Dataset) (~3 hours)
```
Hour 0-0.5: Extract 30 nodes, review conversations  
Hour 0.5-2.5: Write 30 reference summaries (5 min each)
Hour 2.5-2.6: Run LLM prediction generation
Hour 2.6-3.0: Download & evaluate SAMSum dataset
Hour 3.0-3.1: Calculate all ROUGE scores
Total: ~3 hours → Strong paper with generalization
```

### Recommended Schedule:
**Day 1 (2 hours):**
- Morning: Write 15 reference summaries
- Afternoon: Write 15 reference summaries
- Total: 30 summaries done

**Day 2 (30 min):**
- Run evaluation scripts
- Get ROUGE results
- Generate paper-ready tables

**Result:** Complete ROUGE evaluation in 1.5 days of work.

---

## 💡 Tips for Efficient Summary Writing

1. **Batch by type:**
   - Write all main chat summaries first
   - Then all subchat summaries
   - Then nested summaries
   - Maintains consistency

2. **Use a template mentally:**
   - Sentence 1: User's goal
   - Sentence 2-3: Key discussion points
   - Sentence 4: Outcome/conclusion

3. **Set a timer:**
   - 5 minutes per summary
   - Don't overthink
   - Perfectionism slows you down

4. **Take breaks:**
   - After 10 summaries, take 5-min break
   - Prevents mental fatigue
   - Maintains quality

5. **Review sample first:**
   - Read 3-5 conversations
   - Understand common patterns
   - Then write summaries faster

---

## ✅ Quality Checklist (Before Finishing)

After writing all 30 summaries, verify:

- [ ] All are 3-5 sentences (consistent length)
- [ ] All include: user goal + key points + outcome
- [ ] No external information added
- [ ] No copy-paste from messages (paraphrase)
- [ ] Consistent style across all summaries
- [ ] No placeholders ("<<...>>") remaining
- [ ] Grammar/spelling checked
- [ ] File format is valid JSONL

**Spot check:** Read 5 random summaries. If they're good, rest are likely good.

---

## 🎯 When You're Done

You'll have:
- ✅ 30 high-quality reference summaries
- ✅ Valid ROUGE scores
- ✅ Publication-quality evaluation
- ✅ Copy-paste-ready tables for your paper
- ✅ Evidence of context isolation

**This is the foundation of your evaluation section.**

Worth every minute of the 2-hour investment.
