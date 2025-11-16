# LM Studio Integration Guide

This guide explains how to use **real LLM models** with FunSearch instead of the mock LLM.

---

## 📋 Prerequisites

- **LM Studio** installed (download from [https://lmstudio.ai/](https://lmstudio.ai/))
- **8GB+ RAM** recommended (16GB+ for larger models)
- **GPU optional** but recommended for faster generation

---

## 🚀 Quick Start

### 1. Install and Start LM Studio

```bash
# Download from https://lmstudio.ai/
# Install and launch the application
```

### 2. Download a Code Model

Recommended models for FunSearch:

| Model | Size | Quality | Speed | Use Case |
|-------|------|---------|-------|----------|
| **CodeLlama-7B-Instruct** | 7B | Good | Fast | Quick testing |
| **DeepSeek-Coder-6.7B-Instruct** | 6.7B | Excellent | Fast | Best balance |
| **Mistral-7B-Instruct** | 7B | Good | Fast | General purpose |
| **CodeLlama-13B-Instruct** | 13B | Better | Slower | Better quality |
| **WizardCoder-15B** | 15B | Best | Slowest | Maximum quality |

**Recommendation**: Start with `deepseek-coder-6.7b-instruct-q4_k_m` (good quality, small size)

### 3. Start the LM Studio Server

In LM Studio:
1. Load your downloaded model
2. Go to **Local Server** tab
3. Click **Start Server**
4. Verify it's running at `http://localhost:1234`

### 4. Verify Connection

```bash
# Check health endpoint
curl http://localhost:7351/health | jq '.services.lm_studio'

# Should show:
# {
#   "lm_studio": "connected",
#   "lm_studio_model": "deepseek-coder-6.7b-instruct",
#   "lm_studio_models": ["deepseek-coder-6.7b-instruct"]
# }
```

### 5. Run an Experiment with LM Studio

```bash
# Create a project
curl -X POST http://localhost:7351/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Knapsack with Real LLM",
    "description": "Test with LM Studio",
    "problem_type": "optimization",
    "specification": {
      "file_path": "examples/knapsack/specification.py",
      "evolve_function": "priority",
      "evaluate_function": "evaluate"
    }
  }' | jq

# Start experiment (replace PROJECT_ID)
curl -X POST http://localhost:7351/api/v1/projects/{PROJECT_ID}/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LM Studio Test",
    "config": {
      "llm": {
        "provider": "lm_studio",
        "model": "auto",
        "base_url": "http://localhost:1234/v1",
        "temperature": 0.8,
        "max_tokens": 512,
        "timeout": 30
      },
      "sandbox": {
        "provider": "subprocess"
      },
      "funsearch": {
        "samples_per_prompt": 4,
        "num_islands": 10,
        "reset_period": 1800
      },
      "execution": {
        "max_iterations": 1000
      }
    }
  }' | jq
```

---

## ⚙️ Configuration Options

### LLM Config Parameters

```python
{
  "llm": {
    "provider": "lm_studio",  # Use LM Studio
    "model": "auto",          # Auto-detect loaded model (or specify exact name)
    "base_url": "http://localhost:1234/v1",  # LM Studio API URL
    "temperature": 0.8,       # 0.0 = deterministic, 2.0 = very creative
    "max_tokens": 512,        # Max tokens to generate per sample
    "timeout": 30             # Request timeout in seconds
  }
}
```

### Temperature Guide

| Temperature | Behavior | Best For |
|-------------|----------|----------|
| 0.0 - 0.3 | Deterministic, focused | Reproducing known algorithms |
| 0.4 - 0.7 | Balanced | General optimization |
| 0.8 - 1.2 | Creative, diverse | Exploration, novel solutions |
| 1.3 - 2.0 | Very random | Maximum diversity (may be incoherent) |

**Recommended**: Start with 0.8 for good balance

---

## 📊 Expected Performance

### Mock LLM vs Real LLM Comparison

| Aspect | Mock LLM | Real LLM (DeepSeek-Coder-6.7B) |
|--------|----------|-------------------------------|
| Code Quality | Template-based, limited | Creative, novel solutions |
| Speed | Very fast (~1ms) | Moderate (~500ms-2s per sample) |
| Diversity | Low (10-12 templates) | High (infinite variations) |
| Memory Usage | Minimal | 4-8GB |
| GPU Required | No | Optional (10x faster) |
| Discovery Potential | Low | High |

### Iteration Time Estimates

With DeepSeek-Coder-6.7B on CPU:
- **Mock LLM**: 100 iterations ~ 2-3 minutes
- **Real LLM**: 100 iterations ~ 15-30 minutes

With GPU (CUDA):
- **Real LLM**: 100 iterations ~ 3-5 minutes

### Quality Improvements

Expected score improvements with real LLM:

| Example | Mock LLM Best | Real LLM Best | Improvement |
|---------|---------------|---------------|-------------|
| Number Sequence | -5,000 | -500 | 10x better |
| Knapsack | 520 | 580 | 12% better |

---

## 🐛 Troubleshooting

### "LM Studio: disconnected"

**Problem**: Health check shows LM Studio disconnected

**Solutions**:
1. Check LM Studio is running: Open the app
2. Verify model is loaded: See "Local Server" tab
3. Ensure server is started: Click "Start Server"
4. Test manually: `curl http://localhost:1234/v1/models`

### "Connection timeout"

**Problem**: Requests timing out

**Solutions**:
1. Increase timeout in config: `"timeout": 60`
2. Use smaller model (e.g., 6.7B instead of 13B)
3. Reduce `max_tokens`: Try `256` instead of `512`
4. Check system resources: Close other applications

### "Model not loaded"

**Problem**: LM Studio running but no model active

**Solutions**:
1. Download a model in LM Studio
2. Load the model (click on it)
3. Wait for it to fully load (watch memory usage)

### "Out of memory"

**Problem**: System runs out of RAM

**Solutions**:
1. Use quantized models (Q4_K_M instead of FP16)
2. Close other applications
3. Use smaller model (7B → 3B)
4. Enable GPU offloading if you have NVIDIA GPU

### Experiments are slow

**Problem**: Takes too long to complete

**Solutions**:
1. Reduce iterations: `"max_iterations": 500`
2. Reduce islands: `"num_islands": 5`
3. Reduce samples: `"samples_per_prompt": 2`
4. Use faster model (prefer 6.7B over 13B+)
5. Enable GPU if available

---

## 🔬 Advanced Usage

### Custom Prompt Templates

You can customize prompts per problem type:

```python
# In backend/core/llm/prompts.py
CUSTOM_TEMPLATE = PromptTemplate(
    name="my_custom_template",
    description="For my specific problem",
    instruction="Your custom instruction here",
    examples=[
        "Example hint 1",
        "Example hint 2",
    ],
)
```

### Multiple Models

Compare different models on the same problem:

```bash
# Experiment 1: DeepSeek-Coder-6.7B
{
  "name": "DeepSeek Test",
  "config": {
    "llm": {
      "provider": "lm_studio",
      "model": "deepseek-coder-6.7b-instruct"
    }
  }
}

# Experiment 2: CodeLlama-7B
{
  "name": "CodeLlama Test",
  "config": {
    "llm": {
      "provider": "lm_studio",
      "model": "codellama-7b-instruct"
    }
  }
}
```

Use MLflow to compare results across models.

### GPU Acceleration

If you have an NVIDIA GPU:

1. Install CUDA drivers
2. LM Studio will automatically use GPU
3. Check GPU usage in Task Manager / nvidia-smi
4. Expect 5-10x speedup

### Chat vs Completion API

The framework supports both:

- **Completion API** (default): Direct code completion
- **Chat API**: Uses conversational format

To use chat API, modify experiment runner to use `LMStudioChatSampler`.

---

## 📈 Monitoring

### Watch Logs

```bash
# Backend logs show LLM activity
tail -f backend.log | grep "LM Studio"

# You'll see:
# ✓ Connected to LM Studio, using model: deepseek-coder-6.7b-instruct
# ✓ Using LM Studio: deepseek-coder-6.7b-instruct
# LLM call completed in 1.23s
# Tokens: 245 prompt + 87 completion = 332 total
```

### WebSocket Monitoring

```javascript
// Subscribe to experiment logs
{
  "type": "subscribe",
  "channels": ["logs", "metrics", "best_program"]
}

// You'll receive:
{
  "type": "log",
  "level": "info",
  "message": "Using LM Studio for code generation",
  "timestamp": "..."
}
```

### MLflow Tracking

If MLflow is running:

```bash
# View in browser
http://localhost:7352

# Compare experiments
# - Filter by llm_provider = "lm_studio"
# - Compare metrics across different models
# - View generated code artifacts
```

---

## 🎯 Best Practices

### For Quick Testing
- Use **mock LLM** first to verify setup
- Then switch to **small real model** (6.7B)
- Run **short experiments** (100-500 iterations)

### For Research
- Use **larger models** (13B+) for better quality
- Run **longer experiments** (5K-10K iterations)
- Enable **MLflow tracking**
- Compare **multiple models**

### For Production
- Use **GPU acceleration**
- Set **appropriate timeouts**
- Monitor **token usage**
- Implement **retry logic**

---

## 📚 Additional Resources

- [LM Studio Documentation](https://lmstudio.ai/docs)
- [DeepSeek-Coder Paper](https://arxiv.org/abs/2401.14196)
- [CodeLlama Paper](https://arxiv.org/abs/2308.12950)
- [FunSearch Paper (Nature)](https://www.nature.com/articles/s41586-023-06924-6)

---

## ✅ Verification Checklist

Before running a real experiment:

- [ ] LM Studio installed and running
- [ ] Model downloaded and loaded
- [ ] Server started on port 1234
- [ ] Health check shows "connected"
- [ ] Test API manually with curl
- [ ] Backend can detect the model
- [ ] Mock experiment works (baseline test)
- [ ] Ready to run with real LLM!

---

**Next Steps**: Once you've verified LM Studio works, try the knapsack example with a real LLM. You should see significantly better heuristics evolved compared to the mock LLM!
