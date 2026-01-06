# Quick Reference: Multi-Metric Evaluation Decision Tree

## ❓ What should I do for summary evaluation?

### START HERE: How much time do you have?

---

## Path A: I have 2.5-3 hours (RECOMMENDED ⭐)

**Do this:**
1. Write 30 human reference summaries (2 hours)
2. Run comprehensive evaluation: ROUGE + METEOR + BERTScore (15 min)
3. Get publication-quality results with all metrics

**Why:**
- ✅ Gold standard - reviewers accept universally
- ✅ Multi-metric approach shows rigor (ROUGE + METEOR + BERTScore)
- ✅ Custom to your hierarchical architecture
- ✅ One-time investment, use forever in paper

**Commands:**
```bash
cd backend
python -m evaluation.rouge_pipeline --nodes 30
# Edit summary_eval.jsonl - write 30 summaries
python -m evaluation.rouge_pipeline --continue --use-all-metrics
```

**Result:** Complete evaluation table with ROUGE, METEOR, and BERTScore ready for your paper

**See:** `REFERENCE_SUMMARY_OPTIONS.md` → Option B

---

## Path B: I have 3-4 hours (STRONGEST PAPER ⭐⭐⭐)

**Do this:**
1. Write 30 human reference summaries (2 hours)
2. Evaluate on SAMSum public dataset (1 hour)
3. Get two ROUGE tables

**Why:**
- ✅ Custom data shows architecture strength
- ✅ Public dataset proves generalization
- ✅ Reviewers love dual evaluation
- ✅ Zero annotation for second dataset

**Commands:**
```bash
# Part 1: Custom data
python -m evaluation.rouge_pipeline --nodes 30
# Edit summary_eval.jsonl
python -m evaluation.rouge_pipeline --continue

# Part 2: SAMSum (public dataset)
# Download SAMSum: https://huggingface.co/datasets/samsum
# Evaluate your system on it
```

**Result:** Two tables in paper (hierarchical + generalization)

**See:** `PAPER_WRITING_GUIDE.md` → Hybrid Evaluation Strategy

---

## Path C: I have < 1 hour (WORKSHOP ONLY ⚠️)

**Do this:**
1. Use GPT-4 to generate pseudo-references (30 min)
2. Manually inspect 10% (15 min)
3. Run evaluation (5 min)

**Why:**
- ✅ Fast
- ❌ Some reviewers criticize
- ❌ Not ideal for journal submission
- ⚠️ Must clearly disclose in paper

**Commands:**
```bash
# Generate pseudo-gold (NOT YET IMPLEMENTED - ask if needed)
python -m evaluation.generate_pseudo_references --model gpt-4
# Manually review 3-4 examples
python -m evaluation.rouge_pipeline --continue
```

**Result:** Pseudo-reference ROUGE (clearly disclosed)

**See:** `REFERENCE_SUMMARY_OPTIONS.md` → Option C

---

## Path D: I have NO time (❌ DON'T DO THIS)

**Don't:**
- Skip ROUGE entirely
- Use ROUGE without references
- Rush through low-quality summaries

**Instead:**
- Do Path A properly (just 2 hours!)
- Or postpone ROUGE to revision stage
- Focus on qualitative analysis first

**Why:**
- ❌ Invalid ROUGE = paper rejection
- ❌ Poor summaries = bad scores = wasted time
- ✅ 2 hours invested now saves months of revision

---

## Decision Matrix

| Time Available | What to Do | Paper Strength | Reviewer Acceptance |
|----------------|------------|----------------|---------------------|
| 3-4 hours | **Path B** (Hybrid) | ⭐⭐⭐ Excellent | 100% |
| 2-3 hours | **Path A** (Human) | ⭐⭐ Strong | 100% |
| 1 hour | Path C (Pseudo) | ⭐ Acceptable | 70% |
| 0 hours | ❌ Skip | ❌ Incomplete | 0% |

---

## My Recommendation

### For Journal Submission (First Time):
→ **Path A** (30 human summaries)
- 2 hours = publication-ready
- Safe, accepted everywhere
- Do it once, done forever

### For Strong Conference Paper:
→ **Path B** (Hybrid: 30 human + SAMSum)
- 3 hours = dual evaluation
- Shows both custom + generalization
- Impresses reviewers

### For Workshop / Preprint:
→ **Path C** (Pseudo-gold)
- 1 hour = quick results
- Must disclose clearly
- Plan to upgrade for journal

---

## What 30 Summaries Looks Like

**Format (JSONL):**
```json
{"id":"node_001","messages":[...],"reference_summary":"User asks about Python basics. Assistant explains..."}
{"id":"node_002","messages":[...],"reference_summary":"User inquires about..."}
```

**Each summary:**
- 3-5 sentences
- ~50-80 words
- 3-5 minutes to write

**Total:**
- 30 summaries × 4 min = 120 min = 2 hours
- Achievable in one sitting

**Template:**
1. User's goal/question
2. Key points discussed
3. Assistant's main explanations
4. Conversation outcome

---

## Quality Checks Before Running Evaluation

✅ **Before hitting "run":**
- [ ] All 30 summaries written (no placeholders)
- [ ] Each is 3-5 sentences
- [ ] Consistent style
- [ ] No copy-paste from messages
- [ ] Only info from conversation (no external)
- [ ] Grammar checked
- [ ] JSONL format valid

**One bad summary = whole average affected**

---

## After Evaluation: What You Get

### Path A (Human-Written):
- `FINAL_ROUGE_REPORT.md`
- `PAPER_READY_FORMAT.md` with:
  - LaTeX table
  - Markdown table
  - Methods section text
  - Results section text

### Path B (Hybrid):
- Same as Path A, plus:
  - Second table for SAMSum
  - Generalization discussion points
  - Stronger paper narrative

---

## Common Questions

### Q: Can I use fewer than 30 summaries?
**A:** Yes, but:
- 20-30 = acceptable
- 10-20 = weak (reviewers may question)
- <10 = not credible

30 is the sweet spot.

### Q: Can I hire someone to write summaries?
**A:** Yes, if:
- They understand your architecture
- You review all summaries
- You disclose in paper ("by domain expert")

Better: do it yourself (you understand context best)

### Q: What if my scores are low?
**A:** Low ROUGE ≠ bad paper:
- Your contribution is architecture, not summarization
- ROUGE is supporting evidence only
- Discuss why (context isolation trade-offs)
- Focus on qualitative analysis

### Q: Can I change summaries after seeing scores?
**A:** ❌ NO - that's "teaching to the test"
- Write summaries blind to model output
- Don't iterate to optimize scores
- That's academic misconduct

---

## Bottom Line

### ✅ Recommended Path for You:

1. **Spend 2 hours writing 30 summaries** (Path A)
2. **Run evaluation pipeline** (10 min)
3. **Get paper-ready ROUGE tables**
4. **Optional:** Add SAMSum if time allows (+1 hour)

### Your 2-hour investment gets you:
- ✅ Publication-quality ROUGE evaluation
- ✅ Reviewer-proof methodology
- ✅ Ready-to-use LaTeX tables
- ✅ Evidence for context isolation
- ✅ Reusable for all paper versions

**Do it once. Use it forever.**

---

## Next Steps

1. **Read:** `REFERENCE_SUMMARY_OPTIONS.md` (detailed options)
2. **Follow:** `HOW_TO_CALCULATE_ROUGE.md` (step-by-step)
3. **Write:** 30 reference summaries (2 hours)
4. **Run:** Evaluation pipeline (10 min)
5. **Copy-paste:** From `PAPER_READY_FORMAT.md` to your paper

**You're 2 hours away from complete ROUGE evaluation.**

Start now! 🚀
