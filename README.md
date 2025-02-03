## 1. What is this?
REST API created with FastAPI, OpenAI API and LangChain (for RAG). Ask questions concerning David Hume's *A Treatise of Human Nature*.

App performs semantic search on the book and using retrieved context pieces generates answers to your questions.

## 2. How to run
Clone/download this repository and create .env file in project directory. It should look like this
```
ENVIRONMENT = "production" (or "development")
OPENAI_API_KEY="your_key"
MODEL_TEMPERATURE = 0.3
AUTH_SECRET_KEY = "auth_secret_key" (use 'openssl rand -hex 32' to generate)
LANGCHAIN_API_KEY="your_key"
LANGCHAIN_TRACING_V2="true"
```

### 2.1 Without Docker [on Linux]
Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

Open terminal in your project directory and run the following command

```uv run -- fastapi run src/main.py```
