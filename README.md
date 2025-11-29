# BOT GPT - Conversational AI Backend

**Associate Engineer Case Study Solution**



Live API: http://localhost:8000/docs (Swagger UI)



## Features

- Full CRUD for multi-turn conversations

- Open Chat + Grounded (RAG) mode with document upload

- Real LLM via Groq (Llama 3.1 8B)

- TF-IDF retrieval from document chunks

- Context window management

- SQLite + SQLAlchemy

- Production-ready FastAPI



## Quick Start



```bash

# 1. Clone and enter

git clone https://github.com/yourname/botgpt-backend.git

cd botgpt-backend



# 2. Create virtual env

python -m venv venv

source venv/bin/activate    # Windows: venvScriptsactivate



# 3. Install

pip install -r requirements.txt



# 4. Set your Groq API key

export GROQ_API_KEY="gsk_..."    # Windows: set GROQ_API_KEY=gsk_...



# 5. Run

uvicorn app.main:app --reload

