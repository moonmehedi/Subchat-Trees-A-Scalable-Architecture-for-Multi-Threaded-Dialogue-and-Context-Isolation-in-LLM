# vLLM Backend Integration for Kaggle GPU Inference

## Overview

This document describes the integration of vLLM (fast LLM inference engine) with the hierarchical subchat backend, enabling GPU-accelerated inference on Kaggle notebooks with dual GPUs.

## Architecture

### Multi-Backend Support

The backend now supports **3 LLM backends** via the `LLM_BACKEND` environment variable:

1. **`groq`** (default) - Cloud API (Groq)
2. **`ollama`** - Local inference (Ollama)  
3. **`vllm`** - Kaggle GPU inference (vLLM)

### Component Flow

```
┌─────────────────────────────────────────────────────┐
│ Kaggle Notebook                                     │
│  ┌────────────────────────────────────────────────┐ │
│  │ Cell 9: Load vLLM Model                        │ │
│  │ llm = vllm.LLM(model_path, ...)               │ │
│  └────────────────────────────────────────────────┘ │
│                        │                            │
│                        ▼                            │
│  ┌────────────────────────────────────────────────┐ │
│  │ Cell 21: Register Model Globally               │ │
│  │ VLLMClient.set_model(llm)                     │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                         │
                         │ (Shared singleton)
                         ▼
┌─────────────────────────────────────────────────────┐
│ Backend Services                                    │
│  ┌────────────────────────────────────────────────┐ │
│  │ VLLMClient (Singleton)                         │ │
│  │ - _llm: Globally loaded vLLM model             │ │
│  │ - generate(messages) → str                     │ │
│  │ - generate_stream(messages) → generator        │ │
│  │ - _messages_to_prompt(messages) → str          │ │
│  └────────────────────────────────────────────────┘ │
│                        │                            │
│                        ▼                            │
│  ┌────────────────────────────────────────────────┐ │
│  │ SimpleLLMClient                                │ │
│  │ Priority: vLLM → Ollama → Groq → Echo          │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## File Structure

### New Files

- **`backend/src/services/vllm_client.py`** (162 lines)
  - `VLLMClient` singleton class
  - `set_model()` class method for registration
  - `generate()` and `generate_stream()` methods
  - Message format conversion (OpenAI → Qwen template)

### Modified Files

- **`backend/src/cores/config.py`**
  - Added `vllm` to `llm_backend` options
  - Added `vllm_model_path` config field
  - Added vLLM backend initialization in `__init__`

- **`backend/src/services/simple_llm.py`**
  - Added vLLM client initialization in `__init__`
  - Integrated vLLM as **highest priority** in `generate_response()`
  - Integrated vLLM streaming in `generate_response_stream()`

- **`hirachical-subchat.ipynb`**
  - Cell 8: Sets `LLM_BACKEND=vllm` in environment
  - Cell 9: Loads vLLM model (Qwen-3 14B AWQ)
  - Cell 21: Registers model with `VLLMClient.set_model(llm)`
  - Cell 23: Tests integration end-to-end

## Usage

### On Kaggle (GPU Inference)

1. **Run notebook cells 1-9** to load vLLM model on GPUs
2. **Run cell 21** to register model with backend:
   ```python
   from src.services.vllm_client import VLLMClient
   VLLMClient.set_model(llm)
   ```
3. **Backend automatically uses vLLM** when `LLM_BACKEND=vllm` is set
4. **Test integration** with cell 23:
   ```python
   llm_client = SimpleLLMClient()
   response = llm_client.generate_response(root_node, "Your prompt")
   ```

### Local Development (Groq/Ollama)

Set `LLM_BACKEND=groq` or `LLM_BACKEND=ollama` in `.env`:
```bash
LLM_BACKEND=groq  # Use Groq cloud API
GROQ_API_KEY=your_key_here
```

The same code works seamlessly - no changes needed.

## vLLM Configuration

### Model Specifications

- **Model**: Qwen-3 14B AWQ (quantized)
- **Path**: `/kaggle/input/qwen-3/transformers/14b-awq/1`
- **Quantization**: AWQ (4-bit)
- **Tensor Parallelism**: 2 GPUs (T4 x2)
- **GPU Memory**: 91% utilization
- **Max Tokens**: 5120 context length
- **Prefix Caching**: Enabled

### Load Parameters

```python
llm = vllm.LLM(
    model_path,
    quantization='awq',
    tensor_parallel_size=torch.cuda.device_count(),
    gpu_memory_utilization=0.91,
    trust_remote_code=True,
    dtype="half",
    enforce_eager=True,
    max_model_len=5120,
    disable_log_stats=True,
    enable_prefix_caching=True
)
```

### Inference Parameters

```python
sampling_params = SamplingParams(
    temperature=0.0,  # Deterministic
    top_p=0.9,
    max_tokens=1000
)
```

## Message Format Conversion

### Input (OpenAI Format)
```python
[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"},
    {"role": "assistant", "content": "4."},
    {"role": "user", "content": "And 3+3?"}
]
```

### Converted (Qwen Chat Template)
```
System: You are a helpful assistant.

User: What is 2+2?