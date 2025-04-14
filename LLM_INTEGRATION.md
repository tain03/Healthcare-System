# LLM Integration for Healthcare Chat System

This document provides instructions for setting up and configuring the LLM (Large Language Model) integration for the AI-powered chat functionality in the healthcare system.

## 📋 Overview

The healthcare system includes an AI assistant that can answer health-related questions. This assistant uses a hybrid approach:

1. **Rule-based responses**: Pre-defined responses for common health questions
2. **LLM-powered responses**: For more complex or unique questions

The system is designed to be flexible, supporting both local models for privacy and cost-efficiency, as well as powerful cloud-based models like OpenAI's GPT for enhanced capabilities.

## 🔧 Configuration

The LLM integration can be configured in `settings.py` with the following options:

```python
# LLM Settings
# Set to True to use API, False to use local model
LLM_USE_API = True
# API provider ('openai', 'generic')
LLM_API_PROVIDER = 'openai'
# API key for external LLM service (if using API)
LLM_API_KEY = ''  # Add your OpenAI API key here
# API URL for external LLM service (if using generic API)
LLM_API_URL = 'http://localhost:8000/v1/completions'
# Model name (used for both API and local model)
# For OpenAI, use models like 'gpt-3.5-turbo' or 'gpt-4'
LLM_MODEL_NAME = 'gpt-3.5-turbo'
# Maximum tokens to generate
LLM_MAX_TOKENS = 256
# Temperature for generation (higher = more creative, lower = more deterministic)
LLM_TEMPERATURE = 0.7
# Probability threshold for rule-based vs LLM responses (0.0-1.0)
# Higher values will use rule-based responses more often
# Set to 0.0 to always use LLM responses
LLM_RULE_THRESHOLD = 0.0  # Always use LLM responses
```

## 📦 Installation Requirements

To use the LLM integration, you need to install the following dependencies:

```bash
pip install -r requirements.txt
```

The key dependencies for LLM functionality are:

For local models:
- transformers
- torch
- accelerate
- bitsandbytes
- sentencepiece

For OpenAI integration:
- openai

## 🚀 Deployment Options

### Local Model Deployment

By default, the system is configured to use a local model. This approach:
- Keeps all data on your server
- Eliminates API costs
- Reduces latency
- Works offline

Requirements for local deployment:
- At least 4GB of RAM (8GB recommended)
- GPU acceleration recommended but not required
- Approximately 2GB of disk space for model storage

### API Deployment

Alternatively, you can use an external LLM API:
1. Set `LLM_USE_API = True` in settings.py
2. Configure your API key and endpoint
3. Ensure your server can connect to the API endpoint

Recommended API providers:
- OpenAI API (GPT models)
- Hugging Face Inference API
- Self-hosted LLM API servers (like llama.cpp, text-generation-webui)

### OpenAI API Deployment

To use OpenAI's powerful models:

1. Set the following in settings.py:
   ```python
   LLM_USE_API = True
   LLM_API_PROVIDER = 'openai'
   LLM_API_KEY = 'your-openai-api-key'
   LLM_MODEL_NAME = 'gpt-4o-mini'  # Efficient and powerful model, or use 'gpt-3.5-turbo', 'gpt-4', etc.
   ```

2. Install the OpenAI Python package:
   ```bash
   pip install openai
   ```

3. Set `LLM_RULE_THRESHOLD = 0.0` to always use the OpenAI model instead of rule-based responses

## 🔄 Switching Models

To use a different model:

1. Change the `LLM_MODEL_NAME` setting to a different model identifier
2. Ensure the model is compatible with the transformers library
3. Consider the hardware requirements of the new model

Recommended models:

Local models:
- TinyLlama/TinyLlama-1.1B-Chat-v1.0 (~1.1B parameters)
- microsoft/phi-2 (~2.7B parameters)
- google/gemma-2b-it (~2B parameters)
- TheBloke/Llama-2-7B-Chat-GGUF (quantized versions)

OpenAI models:
- gpt-3.5-turbo (good balance of performance and cost)
- gpt-4 (more advanced capabilities, higher cost)
- gpt-4o (latest model with improved performance)
- gpt-4o-mini (efficient version of gpt-4o with lower cost, recommended for healthcare chat)

## ⚙️ Fine-tuning

For improved performance on healthcare-specific questions, you can fine-tune the model:

1. Collect healthcare Q&A pairs
2. Use the Hugging Face PEFT library for parameter-efficient fine-tuning
3. Update the `LLM_MODEL_NAME` to point to your fine-tuned model

## 🔍 Troubleshooting

Common issues:

1. **Out of memory errors**: Try a smaller model or enable quantization
2. **Slow responses**: Adjust `LLM_MAX_TOKENS` to a lower value
3. **Inappropriate responses**: Increase the `LLM_RULE_THRESHOLD` to rely more on rule-based responses

## 📊 Monitoring

The system logs LLM usage and performance metrics. Check the logs for:
- Response generation times
- Error rates
- Usage patterns

## 🔒 Privacy Considerations

When using LLM models:
- Ensure patient data is anonymized before processing
- Consider data retention policies
- Be transparent with users about AI usage
- Include appropriate disclaimers with AI-generated health information
