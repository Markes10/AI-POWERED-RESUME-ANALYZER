# ResumeMind AI — AI-Powered Resume Analyzer

AI-powered HR platform with a 9-agent AI Council for resume analysis, ATS scoring, skill gap analysis, market intelligence, and recruiter simulation. Uses Hugging Face Inference API for LLM and embeddings, Supabase PostgreSQL for storage.

## Features

- **AI Council** — 9 specialized AI agents (ATS Scanner, Role Matcher, Skill Analyst, Culture Fit, Career Coach, Resume Writer, Recruiter Sim, Market Intel, Debugger) + Consensus Engine
- **Resume Analysis** — Upload or paste resume text, get multi-dimensional scoring
- **ATS Compatibility** — Score resumes against job descriptions
- **Skill Gap Analysis** — Identify missing skills and get a 30/60/90 day learning roadmap
- **A/B Testing** — Compare two resumes side-by-side against a job description
- **Recruiter Simulation** — Simulate the full hiring decision process
- **Market Intelligence** — Analyze market demand for candidate skills
- **GitHub & Portfolio Analysis** — Enrich resume analysis with GitHub profile and portfolio review
- **Cover Letter Generation** — Generate job-specific cover letters
- **Resume Timeline** — Track resume versions and improvement over time
- **HR Analytics** — Turnover prediction, performance reviews, learning paths, compensation analysis, attendance tracking, diversity metrics

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
| Infrastructure | Docker Compose (PostgreSQL, Qdrant) |

## Project Structure

```
├── client/                 # React SPA frontend (Vite + React Router 6)
│   ├── pages/              # Route components
│   └── components/         # UI components
├── routes/                 # FastAPI route handlers
│   ├── auth.py             # JWT authentication (login, register)
│   ├── resume_fit.py       # Resume-job matching
│   ├── interview_copilot.py
│   ├── turnover_retention.py
│   └── ...                 # Other HR modules
├── services/               # Business logic & AI services
│   ├── llm.py              # LLM client (OpenAI/Gemini)
│   ├── auth.py             # JWT & password utilities
│   ├── embedding_service.py
│   ├── skill_extractor.py  # spaCy + ML skill extraction
│   └── ...                 # Other services
├── db/                     # Database layer
│   ├── config.py           # SQLAlchemy engine + session
│   ├── database.py         # Base database operations
│   └── models.py           # All ORM models
├── schemas/                # Pydantic request/response schemas
├── middleware/              # Error handling, rate limiting
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker setup (PostgreSQL, Qdrant)
└── Dockerfile              # Container build
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- A PostgreSQL database (local or Supabase)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd ResumeMind-AI
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and JWT secret
   ```

3. **Install Python dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt  # Windows
   # or: source .venv/bin/activate && pip install -r requirements.txt  # Linux/Mac
   ```

4. **Start the backend**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Start the frontend (separate terminal)**
   ```bash
   npm install
   npm run dev
   ```

6. **Open** `http://localhost:8080`

### Docker Setup

```bash
docker-compose up -d
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
| `HF_TOKEN` | No | Hugging Face API token (for LLM features) |
| `SUPABASE_URL` | No | Supabase project URL (optional) |
| `SUPABASE_KEY` | No | Supabase anon/public key (optional) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token expiry (default: 60) |

## Tests

```bash
pytest -q           # Python tests
npm test            # Frontend tests
```
