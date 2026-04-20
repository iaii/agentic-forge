# Quick Setup Guide

Welcome to Agentic Forge! This guide will get your local, multi-agent sandbox running smoothly in just a few minutes.

## Prerequisites
1. **Python 3.12+** installed on your system.
2. **LM Studio** (or Ollama/Oobabooga) downloaded and running locally. This prevents the platform from relying on expensive cloud proxies and keeps your data 100% private.

## Environment Setup

### 1. Launch Your Local Model
1. Open LM Studio.
2. Download a fast local model (we highly recommend `Mistral-7B-Instruct`, `Llama-3-8B`, or `Hermes-3`).
3. Turn on the **Local Server** (usually runs on `http://localhost:1234/v1`).

### 2. Configure the `.env` File
Ensure your `.env` file exists in the root of `Agentic-AI-Fun` and points to LM Studio:
```env
OPENAI_API_BASE="http://localhost:1234/v1"
OPENAI_API_KEY="lm-studio"
OPENAI_MODEL_NAME="openai/local-model"
```
*(Note for advanced users: The `openai/` prefix is mandatory for `OPENAI_MODEL_NAME` to ensure the backend LiteLLM router correctly interfaces with local models via CrewAI).*

### 3. Start the Server
Open your terminal in the `Agentic-AI-Fun` directory and run:
```bash
# Activate your virtual environment (if you use one)
source .venv/bin/activate

# Start the FastAPI server
uvicorn backend.main:app --reload --port 18564
```

### 4. Access the Dashboard
Open your favorite web browser and navigate to:
`http://localhost:18564`

You should be greeted by the Agentic Forge central hub! 

> [!TIP]
> **Stuck on Port 18564?**
> If you get an `Error: [Errno 48] Address already in use` error when starting Uvicorn, just run the built-in cleanup script: `./kill_uvicorn.sh`. This will hunt down any zombified Python workers holding the port hostage and terminate them so you can restart with a clean slate!
