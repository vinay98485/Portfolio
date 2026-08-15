# Portfolio AI Assistant & Web Application

A production-quality AI Engineer portfolio website and recruiter-facing RAG assistant for **Vinay kumar Mandalapu**.

Built with **Next.js 14+ (App Router)**, **Tailwind CSS**, **Framer Motion**, **FastAPI**, **ChromaDB** (vector store), **Gemini Embedding API**, and **Gemini 3.1 Flash Lite** (LLM).

---

## 📁 Directory Structure

```
Portfolio/
│
├── app/                         # FastAPI RAG Backend
│   ├── config.py                # Centralised configuration
│   ├── rag_pipeline.py          # Single interface ask_question() & service pipeline
│   ├── retriever.py             # Vector store retriever (ChromaDB + Gemini API)
│   ├── generator.py             # LLM answer generator (Gemini 3.1 Flash Lite)
│   ├── cache.py                 # File-backed answer cache
│   └── main.py                  # FastAPI application & API endpoints
│
├── frontend/                    # Next.js Recruiter Portfolio Frontend
│   ├── app/                     # Next.js App Router pages & layout
│   ├── components/              # Glassmorphic UI components & floating RAG widget
│   │   ├── Navbar.tsx
│   │   ├── Hero.tsx
│   │   ├── About.tsx
│   │   ├── Skills.tsx
│   │   ├── Projects.tsx
│   │   ├── ProjectCard.tsx
│   │   ├── Timeline.tsx
│   │   ├── Education.tsx
│   │   ├── Certifications.tsx
│   │   ├── Contact.tsx
│   │   ├── AIChatButton.tsx     # Floating circular bottom-right trigger
│   │   ├── AIChatWindow.tsx     # RAG AI assistant modal
│   │   ├── QuestionMenu.tsx     # Predefined recruiter questions selector
│   │   └── ChatMessage.tsx      # Clean markdown answer bubble
│   ├── data/
│   │   ├── questions.json       # Predefined recruiter questions
│   │   ├── projects.json        # 7 verified AI/ML project specifications
│   │   └── profile.json         # Verified bio, skills, education & certs
│   ├── public/
│   │   ├── profile.jpg          # Vinay's formal profile portrait
│   │   ├── resume.pdf           # Downloadable resume
│   │   ├── LinkedIn.pdf         # Downloadable LinkedIn export
│   │   └── projects/            # 3D project thumbnail cards
│   ├── package.json
│   ├── .env.example
│   └── .env.local               # NEXT_PUBLIC_RAG_API_URL
│
├── ingestion/
│   ├── ingest.py                # Knowledge ingestion script
│   └── rebuild_db.py            # DB purge & rebuild script
│
├── knowledge/                   # Markdown knowledge base
│   ├── about_me.md
│   ├── achievements.md
│   ├── certifications.md
│   ├── contact.md
│   ├── education.md
│   ├── experience.md
│   ├── skills.md
│   └── projects/                # 7 detailed project markdown documents
│
├── database/
│   └── chroma_db/               # Persistent ChromaDB vector storage
│
├── tests/                       # Python unit & API integration test battery
│   ├── test_retriever.py
│   ├── test_generator.py
│   ├── test_cache.py
│   ├── test_pipeline.py
│   └── test_api.py
│
├── scripts/
│   └── ask.py                   # CLI entry point
│
├── Dockerfile                   # Backend Docker image configuration
├── requirements.txt             # Backend Python dependencies
├── render.yaml                  # Render deployment blueprint
└── README.md
```

---

## ⚡ Quick Start

### 1. RAG Backend Setup (FastAPI)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_gemini_api_key_here

# Run backend API server
python run.py
```

The FastAPI backend starts on `http://localhost:8000`.
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### 2. Portfolio Frontend Setup (Next.js)

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Configure environment variable
cp .env.example .env.local
# Set NEXT_PUBLIC_RAG_API_URL=http://localhost:8000 (or your deployed Render URL)

# Start Next.js dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🤖 RAG API Endpoints

- **GET /health** — Health check for database, config & LLM connectivity.
- **POST /ask** — Submit question to RAG Assistant.
  ```json
  // POST /ask
  {
    "question": "What deep learning projects has Vinay worked on?"
  }
  ```
  Response:
  ```json
  {
    "answer": "Vinay has developed several deep learning systems...",
    "sources": ["projects/fruit_freshness_classifier.md"],
    "cached": false,
    "response_time_ms": 450
  }
  ```

---

## 🧪 Testing

Run backend test suite (26/26 tests):

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Verify Next.js frontend build:

```bash
cd frontend
npm run build
```

---

## 🌐 Production Deployment

### Frontend (Vercel)
1. Push your repository to GitHub.
2. Log into [Vercel](https://vercel.com/) and click **Add New Project**.
3. Import the `Portfolio` repository.
4. Set **Root Directory** to `frontend`.
5. Add Environment Variable:
   - `NEXT_PUBLIC_RAG_API_URL` = `https://your-rag-backend.onrender.com`
6. Click **Deploy**.

### Backend (Render / Docker)
1. Log into [Render Dashboard](https://dashboard.render.com/).
2. Deploy via Render Blueprint (`render.yaml`) or Web Service using **Docker** runtime.
3. Set environment variable `GEMINI_API_KEY`.
4. Render automatically builds and hosts the FastAPI container.
