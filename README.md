# 🧠 Review Analyzer

![Backend CI](https://github.com/rafael-acerqueira/review-analyzer/actions/workflows/backend-ci.yml/badge.svg)
![Frontend CI](https://github.com/rafael-acerqueira/review-analyzer/actions/workflows/frontend-ci.yml/badge.svg)


**Review Analyzer** is a fullstack AI-powered application that evaluates product reviews in real time. It uses sentiment analysis to detect tone and leverages a Large Language Model (LLM) to assess review quality and provide improvement suggestions when needed.

---

## 🚀 Features

- ✅ Sentiment classification using `distilbert-base-uncased-finetuned-sst-2-english`
- ✅ Review quality evaluation with a configurable Hugging Face chat model
- ✅ LLM-generated suggestions to help improve poor reviews
- ✅ Frontend built with Next.js and React Query
- ✅ Full backend powered by FastAPI
- ✅ Unit, integration and (soon) E2E testing with pytest and Playwright
- ✅ Secure API proxy to hide AI keys from frontend
- ✅ Retrieval-Augmented Generation (RAG) com `pgvector` para buscar reviews similares e enriquecer as respostas da LLM


---

## 🧰 Tech Stack

- **Frontend:** Next.js, TypeScript, React Query, TailwindCSS
- **Backend:** FastAPI, Hugging Face Transformers, Python, pgvector (Postgres)
- **LLM:** Hugging Face Inference API (default: `Qwen/Qwen2.5-7B-Instruct`)
- **Sentiment Model:** `distilbert-base-uncased-finetuned-sst-2-english`
- **Testing:** pytest, Playwright
- **Infra:** Render, Vercel

---

## 🧩 Retrieval-Augmented Generation (RAG)

The Review Analyzer now supports RAG (Retrieval-Augmented Generation) to enhance the review analysis process.

1. Converts the new review into an embedding vector
2. Searches in the database (Postgres + pgvector) for semantically similar reviews.
3. Provides these reviews as additional context to the LLM.

This approach increases relevance, consistency, and accuracy of the responses, avoiding generic answers.

---

## 📸 Demo

![Login](assets/login.png)
<p align="center"><em>Login page</em></p>

![Home](assets/review_analyzer.png)
<p align="center"><em>Review Analyzer</em></p>

![Home Submit](assets/review_analyzer_submit.png)
<p align="center"><em>Review Analyzer Submit button</em></p>

![My Reviews](assets/my_reviews.png)
<p align="center"><em>My Reviews</em></p>

![Dashboard](assets/dashboard.png)
<p align="center"><em>Dashboard</em></p>

![ReviewList](assets/review_list.png)
<p align="center"><em>Review List (Admin)</em></p>

![ReviewDetails](assets/review_details.png)
<p align="center"><em>Review Details</em></p>

---

## 🛠️ Running Locally

### Required Software
- **Python**: 3.10.x
- **uv** (Python package manager): ≥ 0.4
- **PostgreSQL**: 16 with **pgvector** extension
- **Node.js**: 20 LTS
- **npm** (or pnpm/yarn)

### 1. Clone the project

```bash
git clone https://github.com/seu-usuario/review-analyzer.git
cd review-analyzer
```

### 2. Setup the backend

#### Use uv to install dependencies from pyproject.toml
```bash
cd backend
uv sync --locked --extra dev
```

#### Create backend/.env
```bash
# --- Core ---
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/review_analyzer
SECRET_KEY=dev-secret
INTERNAL_AUTH_SECRET=dev-internal-secret

# --- Hugging Face / LLM (optional, if using HF Inference) ---
HF_TOKEN=<your_hf_token>
HF_PROVIDER=together
HF_MODEL=Qwen/Qwen2.5-7B-Instruct
LLM_CACHE_ENABLED=false
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=150
LLM_TIMEOUT_SECONDS=30
LLM_RETRY_ATTEMPTS=2
LLM_RETRY_BACKOFF_SECONDS=0.5

# --- Sentiment model ---
SENTIMENT_MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english

# --- Embeddings / RAG ---
EMBEDDINGS_MODEL_NAME=intfloat/multilingual-e5-small
RAG_ENABLED=true

# RAG tuning (optional)
RAG_TOPN=50
RAG_MIN_SCORE=0.70
RAG_MMR_LAMBDA=0.7
RAG_MMR_K=8
RAG_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
RAG_RERANKER_TOPK=3

# Hardware / E5 prefix
RAG_EMBEDDING_DEVICE=cpu
RAG_E5_QUERY_PREFIX="query: "


```

#### Run migrations

> uv run alembic upgrade head


#### Start the API
> uv run uvicorn app.main:app --reload


#### Verify the backend is running
> Open http://localhost:8000/docs

Or ping the RAG endpoint (it may return empty results until you save embedded reviews):

```bash
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H 'Content-Type: application/json' \
  -d '{"text":"battery life", "k":3}'
```


### 3. Setup the frontend

```bash
cd frontend
npm install
```

#### Create frontend/.env.local (example values)

```bash
# Backend URL your Next.js code calls
API_URL=http://localhost:8000

# Where your Next app is reachable
NEXTAUTH_URL=http://localhost:3000

# NextAuth secret (any strong random string for local)
NEXTAUTH_SECRET=dev-secret

# Shared secret used by Next.js server routes to call protected FastAPI auth endpoints
INTERNAL_AUTH_SECRET=dev-internal-secret

# Google OAuth (optional for local testing)
GOOGLE_CLIENT_ID=<google_client_id>
GOOGLE_CLIENT_SECRET=<google_client_secret>

```

#### Run the dev server
> npm run dev

#### Verify the frontend is running
> Open http://localhost:3000
> If the frontend can’t reach the API, check that the backend is up (see the verification step).
---

## 🧪 Running Tests

### Backend (unit + integration)
#### Use a dedicated test databse

```bash
cd backend
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/review_analyzer_test

# Ensure the extension exists in the test DB once:
psql postgresql://postgres:postgres@localhost:5432/review_analyzer_test -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run tests
uv run pytest

```

> Test fixtures create/drop schema and use the pgvector extension. A separate DB avoids clobbering dev data.

### Frontend (Playwright e2e)
```bash
cd frontend
npx playwright install
npx playwright test

```

---

## 📁 Project Structure

```
review-analyzer/
├── backend/
│   ├── alembic/                         # Alembic migrations
│   │   ├── env.py                       # Alembic runtime config (SQLModel/SQLAlchemy)
│   │   ├── script.py.mako               # Migration template
│   │   └── versions/                    # Migration files (e.g., *_init.py)
│   ├── alembic.ini                      # Alembic config (points to DB URL/env.py)
│   ├── app/
│   │   ├── main.py                      # FastAPI app + routers include
│   │   ├── database.py                  # Engine/Session factory + get_session
│   │   ├── security.py                  # JWT helpers (create/verify), password hashing
│   │   ├── dependencies.py              # Auth guard: get_current_user
│   │   ├── schemas.py                   # Pydantic DTOs (Review*, Auth*, Rag*)
│   │   ├── models/                      # SQLModel tables
│   │   │   ├── user.py
│   │   │   └── review.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── deps.py              # DI factories (use cases, repos, embedders)
│   │   │       └── endpoints/
│   │   │           ├── auth.py          # Thin endpoints → delegate to Auth UCs
│   │   │           ├── review.py        # /analyze_review, /reviews, /mine
│   │   │           ├── admin.py         # /admin/reviews, /admin/stats, delete
│   │   │           └── rag.py           # /rag/search
│   │   ├── domain/                      # Business/Application core (Hexagonal)
│   │   │   ├── auth/
│   │   │   │   ├── entities.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── use_cases.py         # RegisterUser, LoginUser, GoogleLogin, TokenExchange, RefreshTokens
│   │   │   ├── reviews/
│   │   │   │   ├── entities.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── interfaces.py        # ReviewRepository, Sentiment, Suggestion, Embedder
│   │   │   │   └── use_cases.py         # EvaluateText, ListMyReviews, SaveApprovedReview (embeds & saves)
│   │   │   ├── rag/
│   │   │   │   ├── entities.py          # RagHit
│   │   │   │   ├── interfaces.py        # RagRepository, Embedder
│   │   │   │   └── use_cases.py         # SearchRag
│   │   │   └── admin/
│   │   │       ├── entities.py          # AdminStats, Period, RejectionReason
│   │   │       ├── interfaces.py        # AdminReviewsRepository (ports)
│   │   │       └── use_cases.py         # ListReviews, DeleteReview, GetStats
│   │   ├── infra/                       # Adapters (Hexagonal)
│   │   │   ├── db/
│   │   │   │   ├── repositories.py      # User repository (SQLModel)
│   │   │   │   ├── reviews_repository.py# Reviews CRUD (+ embedding save)
│   │   │   │   ├── rag_repository.py    # Vector search (pgvector) for RAG
│   │   │   │   └── admin_repository.py  # Admin filters/aggregations (list/delete/stats)
│   │   │   ├── embeddings/
│   │   │   │   └── local_sentence_transformer.py  # E5 embedder (query/doc) with cache/device
│   │   │   └── tokens/
│   │   │       └── token_provider.py    # Token provider for Auth UCs
│   │   ├── services/
│   │   │   ├── retriever.py
│   │   │   ├── sentiment_analysis_service.py
│   │   │   └── suggestion_service.py
│   ├── tests/
│   │   ├── unit/                        # Unit tests (use cases, services)
│   │   ├── integration/                 # Integration tests (API endpoints/repos)
│   │   └── conftest.py                  # Test fixtures (DB, DI overrides, fake embedders)
│   ├── pyproject.toml                   # uv/packaging config (deps, extras)
│   └── uv.lock                          # lockfile
│
├── frontend/
|   |── src/app                    # Next.js pages (App Router)
│   │   |── admin                  # Admin Page
|   |   |── api                    # Proxy to backend
|   │   ├── review/components/     # ReviewForm, ReviewFilter, etc.
|   │   ├── lib/                   # reviewService (fetch wrapper)
|   │   ├── public/                # Static assets (logo, etc.)
|   |   |── login/                 # Login Page
│   |── tests/
|   |   └── e2e/                   # Playwright tests
├── README.md
├── .env.example
└── .gitignore
```
---
## 📝 Notes & Tips
- NEXTAUTH_URL must match the actual URL users hit. Locally: http://localhost:3000. In containers/tunnels: use the public/local URL.
- Verify backend first (OpenAPI UI or cURL) before npm run dev to avoid confusing frontend errors.
- Embeddings on save: approved reviews are embedded on creation, so /rag/search immediately has data.
- pgvector errors like type "vector" does not exist mean the extension isn’t created in the DB used by DATABASE_URL.
- Switching models/devices: adjust EMBEDDINGS_MODEL_NAME and RAG_EMBEDDING_DEVICE (e.g., cpu vs. cuda) in .env.


---

## 🔮 Roadmap

- [x] ⚙️ Continuous Integration (CI) with Github Actions
- [x] 🧪 End-to-end tests with Playwright
- [x] ✍️ Feedback loop for rejected reviews
- [x] 📊 Admin dashboard with filters and stats
- [x] 🔐 User authentication (credentials & Google OAuth)
- [x] 📝 Review linked to user (user-specific review history)
- [x] 📊 Admin statistics by sentiment, status, etc.
- [x] 🗃️ User “My Reviews” page (/my-reviews)
- [x] 🧩 RAG integration (pgvector + LLM)
- [x] 🚀 Public demo deployment


---

## 📄 License

MIT © Rafael Aquino — 2025
