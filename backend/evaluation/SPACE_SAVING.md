# 💾 Space-Saving ROUGE Setup

## Problem: Codespace Full

If you get "No space left on device" errors, follow these steps:

## Quick Fix (Free 8-10 GB)

```bash
# 1. Clear pip cache (frees ~8GB)
pip cache purge

# 2. Clear all Python caches
rm -rf ~/.cache/pip ~/.cache/huggingface

# 3. Check space
df -h /
```

## Optimized Installation (No rouge-score needed!)

The original plan used both `evaluate` and `rouge-score` libraries. **This is wasteful!**

### ✅ Minimal Installation

```bash
# Only install evaluate (includes ROUGE support)
pip install --no-cache-dir evaluate
```

This saves ~500MB and avoids build issues with `rouge-score`.

## How We Modified the Code

### Before (Required 2 libraries)
```python
import evaluate
from rouge_score import rouge_scorer  # ❌ Not needed!

self.rouge = evaluate.load("rouge")
self.scorer = rouge_scorer.RougeScorer(...)  # ❌ Redundant!
```

### After (Only evaluate)
```python
import evaluate  # ✅ Includes ROUGE support

self.rouge = evaluate.load("rouge")  # ✅ All you need!
```

## Additional Space-Saving Tips

### 1. Clean Docker Images (if applicable)
```bash
docker system prune -a --volumes
```

### 2. Remove Old Logs
```bash
# Check log sizes
du -sh backend/dataset/logs/*

# Remove old test logs if needed
rm -rf backend/dataset/logs/old_runs
```

### 3. Clear Chroma DB (if rebuilding)
```bash
# Backup if needed first!
du -sh backend/chroma_db
rm -rf backend/chroma_db/*
```

### 4. Clean Node Modules (if any)
```bash
cd front-end
rm -rf node_modules
npm install  # Reinstall only what's needed
```

## Monitoring Space

### Check Overall Usage
```bash
df -h /
```

### Find Large Directories
```bash
du -h --max-depth=2 /workspaces | sort -hr | head -20
```

### Find Large Files
```bash
find /workspaces -type f -size +100M -exec ls -lh {} \;
```

## If Still Out of Space

### Option 1: Use Smaller LLM Responses
```python
# In prediction_generator.py, limit response length
self.llm_client.generate_chat_response(
    user_message=prompt,
    max_tokens=200  # Add limit
)
```

### Option 2: Process Smaller Batches
```bash
# Instead of processing all at once
python -m evaluation.rouge_pipeline --num-scenarios 2
# Run multiple times with different scenarios
```

### Option 3: Clean Up Between Runs
```python
# In your evaluation script
import gc
import os

# After processing each batch
gc.collect()
os.system("pip cache purge")
```

## What Uses the Most Space?

Typical breakdown:
- **pip cache**: 8-10 GB (cleared with `pip cache purge`)
- **Docker layers**: 5-8 GB (cleared with `docker system prune`)
- **Python packages**: 2-4 GB (minimize with `--no-cache-dir`)
- **Hugging Face models**: 1-3 GB (cleared with `rm -rf ~/.cache/huggingface`)
- **Your logs**: Variable (check with `du -sh backend/dataset/logs`)

## Best Practices

1. **Always use `--no-cache-dir`** when installing in Codespaces
   ```bash
   pip install --no-cache-dir package_name
   ```

2. **Regularly clear caches**
   ```bash
   pip cache purge
   ```

3. **Monitor space before large operations**
   ```bash
   df -h / && echo "Proceeding with install..."
   ```

4. **Use streaming/batch processing** instead of loading everything into memory

---

**With these optimizations, you should have plenty of space for ROUGE evaluation!**
