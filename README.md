# 🧠 Review Analyzer

**Review Analyzer** is a fullstack AI-powered application that evaluates product reviews in real time. It uses sentiment analysis to detect tone and leverages a Large Language Model (LLM) to assess review quality and provide improvement suggestions when needed.

---

## 🚀 Features

- ✅ Sentiment classification using `distilbert-base-uncased-finetuned-sst-2-english`
- ✅ Review quality evaluation with `microsoft/phi-4`
- ✅ LLM-generated suggestions to help improve poor reviews
- ✅ Frontend built with Next.js and React Query
- ✅ Full backend powered by FastAPI
- ✅ Unit, integration and (soon) E2E testing with pytest and Playwright
- ✅ Secure API proxy to hide AI keys from frontend

---

## 🧰 Tech Stack

- **Frontend:** Next.js, TypeScript, React Query, TailwindCSS
- **Backend:** FastAPI, Hugging Face Transformers, Python
- **LLM:** Hugging Face Inference API (`phi-4`)
- **Sentiment Model:** `distilbert-base-uncased-finetuned-sst-2-english`
- **Testing:** pytest, Playwright
- **Infra:** Render, Vercel

---

## 📸 Demo

> Demo coming soon...

---

## 🛠️ Running Locally

### 1. Clone the project

```bash
git clone https://github.com/seu-usuario/review-analyzer.git
cd review-analyzer
```

### 2. Setup the backend

```bash
cd backend
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

> Set your Hugging Face token in `.env` as `HF_TOKEN=...`

### 3. Setup the frontend

```bash
cd frontend
npm install
npm run dev
```

> Ensure `.env.local` has:
> `BACKEND_API_URL=http://localhost:8000`

---

## 🧪 Running Tests

```bash
# Unit & Integration (backend)
cd backend
PYTHONPATH=. pytest

# E2E (frontend)
cd frontend
npx playwright test
```

---

## 📁 Project Structure

```
review-analyzer/
├── backend/
│   ├── app/
│   │   ├── core/                  # API clients (Hugging Face)
│   │   ├── services/              # Business logic: LLM + Sentiment
│   │   ├── utils/                 # Prompt formatters, extractors
│   │   ├── schemas.py             # Pydantic models
│   │   └── main.py                # FastAPI entrypoint
│   ├── tests/
│   │   ├── unit/                  # Unit tests (mocked services)
│   │   ├── integration/           # Integration tests (API endpoints)
│   │   └── conftest.py            # Test fixtures
│   └── requirements.txt
│
├── frontend/
│   ├── app/                       # Next.js pages (App Router)
│   │   └── api/                   # Proxy to backend
│   ├── components/                # ReviewForm, FeedbackCard, etc.
│   ├── lib/                       # reviewService (fetch wrapper)
│   ├── public/                    # Static assets (logo, etc.)
│   ├── styles/                    # Tailwind + custom styles
│   └── tests/
│       └── e2e/                   # Playwright tests
│
├── README.md
├── .env.example
└── .gitignore
```

---

## 🔮 Roadmap

- [ ] ✍️ Feedback loop for rejected reviews
- [ ] 🧪 End-to-end tests with Playwright
- [ ] 📊 Admin dashboard with filters and stats
- [ ] 🔐 User authentication + history
- [ ] 🌐 Multi-language support (i18n)

---

## 📄 License

MIT © Rafael Aquino — 2025