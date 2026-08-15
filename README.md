# Portfolio RAG Assistant

A recruiter-facing AI assistant that answers questions about **Vinay Kumar Mandalapu** using a **Retrieval-Augmented Generation (RAG)** pipeline.

Built with **ChromaDB** (vector store), **Sentence Transformers** (embeddings), **Gemini 3.7 Flash** (LLM), and clean modular architecture.

---

## Directory Structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py           # Centralised configuration
│   ├── rag_pipeline.py     # Single interface ask_question() & service pipeline
│   ├── retriever.py        # Vector store retriever (ChromaDB + sentence-transformers)
│   ├── generator.py        # LLM answer generator (Gemini)
│   └── cache.py            # File-backed answer cache
│
├── ingestion/
│   ├── __init__.py
│   ├── ingest.py           # Ingestion script
│   └── rebuild_db.py       # DB purge & rebuild script
│
├── knowledge/              # Markdown knowledge base
│   ├── about_me.md
│   ├── achievements.md
│   ├── certifications.md
│   ├── contact.md
│   ├── education.md
│   ├── experience.md
│   ├── skills.md
│   └── projects/
│       ├── bank_customer_churn_prediction.md
│       ├── bitcoin_price_prediction.md
│       ├── credit_risk_scoring_engine.md
│       ├── customer_segmentation.md
│       ├── enterprise_ecommerce_ai_retention_engine.md
│       ├── fruit_freshness_classifier.md
│       └── resume_builder_system.md
│
├── database/
│   └── chroma_db/          # Persistent ChromaDB storage
│
├── tests/
│   ├── __init__.py
│   ├── test_retriever.py   # Retriever test battery
│   ├── test_generator.py   # Generator test suite
│   ├── test_cache.py       # Answer cache unit tests
│   └── test_pipeline.py    # Pipeline service unit tests
│
├── scripts/
│   ├── __init__.py
│   └── ask.py              # CLI entry point
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create `.env` in the root directory:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.7-flash
TOP_K=5
SIMILARITY_THRESHOLD=1.6
MAX_CONTEXT_CHUNKS=5
MAX_OUTPUT_TOKENS=1024
TEMPERATURE=0.2
CACHE_ENABLED=true
CACHE_TTL_HOURS=168
LOG_LEVEL=INFO
```

### 3. Run Ingestion

```bash
python ingestion/ingest.py
```

Or rebuild the database from scratch:

```bash
python ingestion/rebuild_db.py
```

### 4. Query via CLI

```bash
python scripts/ask.py "Tell me about Vinay"
```

Bypass cache:

```bash
python scripts/ask.py --no-cache "What deep learning projects has Vinay built?"
```

cache management:

```bash
python scripts/ask.py --cache-stats
python scripts/ask.py --clear-cache
```

### 5. Run API Server

```bash
python run.py
```

The server starts on `http://0.0.0.0:8000`. 

- **Interactive API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### API Endpoints

- **GET /** — Service Status
  ```bash
  curl http://localhost:8000/
  ```
  Response:
  ```json
  {
      "service": "Vinay Portfolio AI",
      "status": "running"
  }
  ```

- **GET /health** — Component Health Check
  ```bash
  curl http://localhost:8000/health
  ```
  Response:
  ```json
  {
      "status": "healthy",
      "components": {
          "config": "ok",
          "database": "ok",
          "llm": "ok"
      }
  }
  ```

- **GET /sample-questions** — Recruiter Sample Questions
  ```bash
  curl http://localhost:8000/sample-questions
  ```
  Response:
  ```json
  [
      "What projects has Vinay built?",
      "What deep learning projects has Vinay worked on?",
      "What technologies does Vinay know?",
      "Why should someone hire Vinay?",
      "What is Vinay's education background?"
  ]
  ```

- **POST /ask** — Ask RAG Assistant
  ```bash
  curl -X POST http://localhost:8000/ask \
       -H "Content-Type: application/json" \
       -d '{"question": "What projects has Vinay built?"}'
  ```
  Response:
  ```json
  {
      "answer": "...",
      "sources": [
          "projects/fruit_freshness_classifier.md",
          "projects/bank_customer_churn_prediction.md"
      ],
      "cached": false,
      "response_time_ms": 1200
  }
  ```

---

## Testing

Run all unit and component tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Run individual test files:

```bash
python tests/test_retriever.py
python tests/test_generator.py --offline
python tests/test_cache.py
python tests/test_pipeline.py
python tests/test_api.py
```

---

---

## Production Deployment & Configuration

### Architecture Overview

```
User Query / Client Request
        │
        ▼
   FastAPI Layer (app/main.py)
   ├── Rate Limiter (slowapi 10 req/min/IP)
   ├── Security Headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
   └── IP-Aware Request Logger
        │
        ▼
   RAG Pipeline Service (app/rag_pipeline.py)
   ├── Answer Cache (app/cache.py — answer_cache.json)
   ├── Retriever (app/retriever.py — ChromaDB vector store + sentence-transformers)
   └── Generator (app/generator.py — Gemini 3.7 Flash with retry logic)
```

### Environment Variables Reference

Copy `.env.example` to `.env` for local setup. In production (Docker / Render), supply environment variables directly at runtime:

| Variable | Description | Default / Required |
| --- | --- | --- |
| `GEMINI_API_KEY` | Google Gemini API Key | **Required** |
| `GEMINI_MODEL` | Gemini LLM Model | `gemini-3.7-flash` |
| `EMBEDDING_MODEL` | SentenceTransformer model | `sentence-transformers/all-MiniLM-L6-v2` |
| `CHROMA_DB_PATH` | Path to persistent vector database | `database/chroma_db` |
| `CACHE_ENABLED` | Enable answer caching | `true` |
| `CACHE_TTL_HOURS` | Cache TTL in hours | `168` |
| `TOP_K` | Number of chunks retrieved | `5` |
| `SCORE_THRESHOLD` | L2 distance threshold | `1.6` |
| `LOG_LEVEL` | Application logging verbosity | `INFO` |

---

### Render Deployment Steps

#### Option A: Deploy via Render Blueprint (`render.yaml`)
1. Push your repository to GitHub.
2. Log in to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** $\rightarrow$ **Blueprint**.
4. Connect your GitHub repository. Render will automatically detect `render.yaml`.
5. Under **Environment Variables**, set `GEMINI_API_KEY` to your Gemini API key.
6. Click **Apply**. Render will build the Docker container and deploy the web service.

#### Option B: Deploy via Render Web Service UI
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** $\rightarrow$ **Web Service**.
3. Connect your GitHub repository.
4. Select **Docker** as the Runtime.
5. Set the Health Check Path to `/health`.
6. Add environment variable `GEMINI_API_KEY` under **Environment**.
7. Click **Create Web Service**.

---

### Local Docker Deployment

#### Build Docker Image
```bash
docker build -t vinay-portfolio-rag .
```

#### Run Docker Container
```bash
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY="your_gemini_api_key_here" \
  --name vinay-portfolio-rag-app \
  vinay-portfolio-rag
```

#### Test Running Container
```bash
curl http://localhost:8000/health
```

---

### Updating Knowledge Base Workflow

When updating portfolio information or adding new projects:

1. **Add / Edit Markdown Files**:
   Edit files in `knowledge/` or `knowledge/projects/`. Ensure YAML frontmatter specifies `category`, `domain`, and `project_name`.

2. **Rebuild Vector Database**:
   ```bash
   python ingestion/rebuild_db.py
   ```
   This clears and re-populates the persistent vector index in `database/chroma_db/`.

3. **Verify Retrieval**:
   ```bash
   python tests/test_retriever.py
   ```

4. **Commit & Push**:
   Commit the updated markdown files and `database/chroma_db/` folder to git:
   ```bash
   git add knowledge/ database/chroma_db/
   git commit -m "Update portfolio knowledge base"
   git push origin main
   ```
   *Render will automatically trigger a build and deploy the updated application!*
