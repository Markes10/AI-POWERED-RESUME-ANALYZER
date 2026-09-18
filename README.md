# ResumeMind AI - AI-Powered Resume Analyzer

AI-powered HR platform with a 9-agent AI Council for resume analysis, ATS scoring, skill gap analysis, market intelligence, and recruiter simulation. Uses Hugging Face Inference API for LLM and embeddings, Supabase PostgreSQL for storage.

## Features

- **AI Council** - 9 specialized AI agents (ATS Scanner, Role Matcher, Skill Analyst, Culture Fit, Career Coach, Resume Writer, Recruiter Sim, Market Intel, Debugger) + Consensus Engine
- **Resume Analysis** - Upload or paste resume text, get multi-dimensional scoring
- **ATS Compatibility** - Score resumes against job descriptions
- **Skill Gap Analysis** - Identify missing skills and get a 30/60/90 day learning roadmap
- **A/B Testing** - Compare two resumes side-by-side against a job description
- **Recruiter Simulation** - Simulate the full hiring decision process
- **Market Intelligence** - Analyze market demand for candidate skills
- **GitHub & Portfolio Analysis** - Enrich resume analysis with GitHub profile and portfolio review
- **Cover Letter Generation** - Generate job-specific cover letters
- **Resume Timeline** - Track resume versions and improvement over time
- **HR Analytics** - Turnover prediction, performance reviews, learning paths, compensation analysis, attendance tracking, diversity metrics

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + React Router 6 + TypeScript + Vite + TailwindCSS 3 |
| Backend | FastAPI (Python 3.11+) |
| Database | PostgreSQL via SQLAlchemy ORM |
| AI / LLM | Hugging Face Inference API / OpenAI / Gemini |
| Embeddings | sentence-transformers (BAAI/bge-large-en-v1.5) |
| Auth | JWT (python-jose) + bcrypt |
| NLP | spaCy + scikit-learn |
| Infrastructure | Docker Compose (PostgreSQL, Redis, Qdrant) |

## Project Structure

```
client/                   # React SPA frontend (Vite + React Router 6)
routes/                   # FastAPI route handlers
services/                 # Business logic and AI services
db/                       # SQLAlchemy database layer
schemas/                  # Pydantic request/response schemas
middleware/               # Error handling and rate limiting
main.py                   # FastAPI app entry point
requirements.txt          # Python dependencies
docker-compose.yml        # PostgreSQL, Redis, Qdrant, API and workers
Dockerfile                # API and frontend image
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop with the Linux engine running
- Tesseract OCR installed and available on PATH for scanned documents
- A PostgreSQL database (Docker Compose supplies one locally)

### Setup

1. **Set up environment variables**
   ```powershell
   copy .env.example .env
   ```
   Edit `.env` with your database URL, JWT secret, and optional AI provider keys.

2. **Install Python dependencies**
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m spacy download en_core_web_sm
   ```

3. **Install frontend dependencies**
   ```powershell
   corepack pnpm install
   ```

4. **Start infrastructure and the API**
   ```powershell
   docker compose up -d
   .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Start the frontend in a separate terminal**
   ```powershell
   corepack pnpm dev -- --host 0.0.0.0
   ```

6. Open `http://localhost:8080`.

### Docker Setup

```powershell
docker compose up -d --build
```

## API Documentation

Once running, visit:

- API Docs: `http://localhost:8000/api/docs`
- Health Check: `http://localhost:8000/health`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET` | Yes | Secret key for JWT tokens |
| `HF_TOKEN` | No | Hugging Face API token for LLM features |
| `OPENAI_API_KEY` | No | OpenAI API key |
| `GEMINI_API_KEY` | No | Gemini API key |
| `REDIS_URL` | No | Redis connection string |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token expiry, default 60 |

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
corepack pnpm test
```