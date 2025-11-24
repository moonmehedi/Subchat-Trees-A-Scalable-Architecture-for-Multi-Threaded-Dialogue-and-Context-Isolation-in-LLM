## Introduction

We release sharded instructions that are used to simulate single-turn and multi-turn conversations in the paper "LLMs Get Lost in Multi-Turn Conversation".
This dataset is released in conjunction with the code repository which can conduct the simulation, located at: https://github.com/microsoft/lost_in_conversation
More information in the Github repository is provided on how to use the dataset.

## Dataset Contents

Each sample has the following schema:

```
{
    "task_id": "sharded-{original-task-id}",
    "task": "code|database|actions|math|data2text|summary|translation",
    "shards: [{"shard_id": 1, "shard_text": "[...]"}, {"shard_id": 2, "shard_text": "[...]"}, ...],
    "<task_specific_keys>": <task_specific_values>
}
```

The task-specific keys and values depend on the task, and are used for bookkeeping and evaluation (e.g., the reference answer, tests, etc.).
## Downloading the Dataset

The main dataset file `lost_in_conversation.json` is tracked with Git LFS and can be obtained in one of two ways:
1. Using Git LFS (recommended):
  ```bash
  # Install git lfs if not present (Debian/Ubuntu)
  sudo apt update && sudo apt install -y git-lfs
  git lfs install
  git clone https://huggingface.co/datasets/microsoft/lost_in_conversation
  cd lost_in_conversation
  git lfs pull  # ensures large files are fetched
  ```
2. Direct download (fallback if Git LFS is unavailable):
  ```bash
  curl -L -o lost_in_conversation.json \
    https://huggingface.co/datasets/microsoft/lost_in_conversation/resolve/main/lost_in_conversation.json
  ```
Expected file metadata:
* Filename: `lost_in_conversation.json`
* Size: 30,521,543 bytes
* SHA256: `692d588c17c878dce1593c816e0d755582b6e73ae0f6c2fb5148defab2082b9f`
Verify after download:
```bash
wc -c lost_in_conversation.json    # should print: 30521543 lost_in_conversation.json
sha256sum lost_in_conversation.json | grep 692d588c17c878dce1593c816e0d755582b6e73ae0f6c2fb5148defab2082b9f
```
## Quick Usage Example

You can stream and iterate over records (each line is a JSON object) in Python:
```python
import json, itertools

with open('lost_in_conversation.json', 'r', encoding='utf-8') as f:
   for i, line in enumerate(f):
      obj = json.loads(line)
      # Access top-level keys
      task_id = obj.get('task_id')
      task = obj.get('task')
      shards = obj.get('shards', [])  # list of {shard_id, shard_text}
      # Example: reconstruct full instruction
      full_text = '\n'.join(s['shard_text'] for s in sorted(shards, key=lambda s: s['shard_id']))
      # Do something with the reconstructed text
      if i < 3:
        print(task_id, task, len(shards))
      # Break early for demo
      if i == 9:
        break
```
Memory tip: Process line-by-line instead of loading the entire file at once since it is ~30MB.

## Dataset Creation & Processing

The data was created through automatic generation followed by manual curation by the authors of the work, between January and April 2025. The exact process is described in the "Sharding Process" Appendix section of the paper.

Creating datasets involved transforming existing data (fully-specified single-turn instructions) from seven datasets, as listed in the paper. All datasets correspond to datasets released to evaluate LLM performance on generation tasks.

## License

The dataset is licensed under CDLA Permissive 2.0.

## Privacy Statement

[Microsoft Privacy Statement](https://go.microsoft.com/fwlink/?LinkId=521839)

## Citation

If you use this dataset in your work, please cite the following paper:
```
@inproceedings{laban2025lost_in_conv,
  title={LLMs Get Lost In Multi-Turn Conversation},
  author={Laban, Philippe and Hayashi, Hiroaki and Zhou, Yingbo and Neville, Jennifer},
  year={2025},
}
```

### Dataset Card Contact

Contact Philippe Laban (plaban@microsoft.com) or Jennifer Neville (jenneville@microsoft.com) if you have any questions.