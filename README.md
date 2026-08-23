# 🚀 AI-Powered Resume Analyzer - Next Generation

An **advanced, production-ready full-stack application** for intelligent resume analysis, ATS optimization, skill gap detection, and personalized learning recommendations. Built with modern technology and designed to run seamlessly on any user's system.

## 🎯 Core Features

### 📄 **Universal Resume Processing**
- **Multi-Format Support**: PDF, DOCX, TXT, Images (with OCR)
- **Design-Agnostic Analysis**: Works with any resume layout or design
- **Language Support**: 50+ languages (auto-detection + manual selection)
- **Encoding Detection**: Handles any character encoding automatically

### 🤖 **AI-Powered Analysis Suite**
- **Resume Score Analysis** — Multi-dimensional scoring (content, format, keywords)
- **ATS Compatibility Scoring** — Optimized recommendations for ATS systems
- **Skill Gap Analysis** — Identify missing skills for target roles
- **Resume Comparison** — A/B testing of multiple resume versions
- **Recruiter Simulation** — AI simulates hiring decision process
- **Market Intelligence** — Real-time demand analysis for skills
- **Smart Cover Letter Generation** — Job-specific, personalized content

### 📚 **Intelligent Learning Recommendations**
- **Skill Gap Detection** — Identifies missing competencies automatically
- **Curated Learning Paths** — Recommendations from Coursera, Udemy, LinkedIn Learning
- **Estimated Time to Competency** — How long to acquire missing skills
- **Cost Analysis** — Free vs. paid learning options
- **Progress Tracking** — Monitor your skill development journey

### 📊 **Advanced HR Analytics** (Optional)
- Turnover prediction models
- Performance review analytics
- Compensation analysis
- Market salary benchmarking

## 🏗️ Architecture

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + TypeScript + Vite | Modern, type-safe UI |
| **Routing** | React Router 6 (SPA) | Client-side navigation |
| **Styling** | TailwindCSS 3 + Radix UI | Design system & components |
| **Backend** | Express.js + Python FastAPI | Flexible API layer |
| **LLM** | Qwen2 (Hugging Face) | Advanced AI processing |
| **NLP** | spaCy, NLTK, scikit-learn | Text analysis & ML |
| **Database** | PostgreSQL + SQLAlchemy | Persistent data storage |
| **Auth** | JWT + bcrypt | Secure authentication |
| **OCR** | Tesseract + OpenCV | Image text extraction |
| **Vector DB** | Qdrant (optional) | Semantic search |
| **Testing** | Vitest + Pytest | Comprehensive test coverage |
| **Containerization** | Docker + Docker Compose | Consistent deployment |

### Project Structure

```
AI-POWERED-RESUME-ANALYZER/
├── client/                          # React Frontend (SPA)
│   ├── pages/
│   │   ├── Index.tsx               # Home page
│   │   ├── ResumeAnalysis.tsx       # Main analysis interface
│   │   ├── SkillGap.tsx             # Skill gap analysis
│   │   ├── LearningPaths.tsx        # Learning recommendations
│   │   ├── Comparison.tsx           # Resume A/B testing
│   │   └── Dashboard.tsx            # User dashboard
│   ├── components/
│   │   ├── ui/                      # Radix UI components
│   │   ├── ResumeUploader.tsx       # File upload handler
│   │   ├── ScoreCard.tsx            # Results display
│   │   └── LearningCard.tsx         # Learning recommendations
│   ├── hooks/                       # Custom React hooks
│   ├── services/                    # API client services
│   ├── types/                       # TypeScript types
│   ├── App.tsx                      # Router & layout
│   ├── global.css                   # TailwindCSS theming
│   └── vite.config.ts               # Vite configuration
│
├── server/                          # Express Backend
│   ├── index.ts                     # Express app setup
│   ├── routes/
│   │   ├── resume.ts                # Resume analysis endpoints
│   │   ├── skills.ts                # Skill endpoints
│   │   └── health.ts                # Health check
│   ├── middleware/
│   │   ├── auth.ts                  # JWT verification
│   │   └── errorHandler.ts          # Error handling
│   └── services/                    # Business logic
│
├── app/                             # FastAPI Backend (Python)
│   ├── db/
│   │   ├── database.py              # SQLAlchemy setup
│   │   └── models.py                # DB models
│   ├── routes/
│   │   ├── resume_analysis.py       # Analysis endpoints
│   │   ├── skill_gap.py             # Skill gap endpoints
│   │   ├── learning.py              # Learning recommendations
│   │   └── auth.py                  # Authentication
│   ├── services/
│   │   ├── llm.py                   # LLM service (Qwen2)
│   │   ├── nlp.py                   # NLP processing
│   │   ├── ocr.py                   # OCR processing
│   │   ├── learning.py              # Learning path logic
│   │   └── environment_checks.py    # Startup validation
│   ├── schemas/
│   │   ├── resume.py                # Pydantic schemas
│   │   └── learning.py
│   └── middleware/
│       └── error_handling.py        # Error handling
│
├── shared/                          # Shared Types
│   └── api.ts                       # API interfaces
│
├── tests/                           # Test Suite
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── e2e/                         # E2E tests
│
├── docs/                            # Documentation
│   ├── API.md                       # API documentation
│   ├── ARCHITECTURE.md              # Detailed architecture
│   └── DEPLOYMENT.md                # Deployment guide
│
├── docker-compose.yml               # Development environment
├── docker-compose.prod.yml          # Production environment
├── Dockerfile                       # Container image
├── package.json                     # Node.js dependencies
├── requirements.txt                 # Python dependencies
├── tsconfig.json                    # TypeScript config
├── vite.config.ts                   # Frontend build config
└── main.py                          # FastAPI entry point
```

## 🚀 Quick Start Guide

### Prerequisites

#### System Requirements
- **OS**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Disk**: 5GB free space

#### Required Software
- **Python**: 3.11+ ([Download](https://www.python.org/downloads/))
- **Node.js**: 18+ ([Download](https://nodejs.org/))
- **PostgreSQL**: 12+ ([Download](https://www.postgresql.org/download/))
- **Git**: Latest version ([Download](https://git-scm.com/))

#### Optional (for enhanced features)
- **Tesseract OCR** (for image-based resumes)
- **Docker & Docker Compose** (for containerized deployment)

### 1️⃣ Clone & Setup

```bash
# Clone repository
git clone https://github.com/Dweepangain11dec99/AI-POWERED-RESUME-ANALYZER.git
cd AI-POWERED-RESUME-ANALYZER

# Run setup script (auto-installs dependencies)
npm run setup:dev
```

### 2️⃣ Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# IMPORTANT: Set these values:
# - DATABASE_URL=postgresql://user:password@localhost:5432/resume_analyzer
# - HF_TOKEN=your_huggingface_api_token (get from https://huggingface.co/settings/tokens)
# - JWT_SECRET=your_random_secret_key_min_32_chars
# - CORS_ORIGINS=http://localhost:5173,http://localhost:8000
```

### 3️⃣ Database Setup

```bash
# Create PostgreSQL database (Linux/macOS)
createdb resume_analyzer

# Or use PostgreSQL shell
psql -c "CREATE DATABASE resume_analyzer;"

# Initialize database schema
python init_db.py
```

### 4️⃣ Install Dependencies

```bash
# Frontend dependencies
pnpm install

# Python backend dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
```

### 5️⃣ Run Application

```bash
# Start all services (frontend + backend)
pnpm dev

# Or start separately:
# Terminal 1: Frontend
pnpm dev:client

# Terminal 2: Python backend
uvicorn main:app --reload --port 8000

# Terminal 3: Express server (optional)
pnpm dev:server
```

Access the application:
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

## 📦 Docker Deployment

### Quickstart with Docker

```bash
# Development environment
docker-compose up -d

# Production environment
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Build Custom Image

```bash
# Build Docker image
docker build -t resume-analyzer:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/analyzer \
  -e HF_TOKEN=your_token \
  resume-analyzer:latest
```

## 🔧 Configuration Guide

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | - | PostgreSQL connection string |
| `HF_TOKEN` | ✅ | - | Hugging Face API token |
| `JWT_SECRET` | ✅ | - | Secret for JWT (min 32 chars) |
| `APP_ENV` | ❌ | development | `development` or `production` |
| `DEBUG` | ❌ | false | Enable debug logging |
| `CORS_ORIGINS` | ❌ | `*` | Comma-separated allowed origins |
| `LOG_LEVEL` | ❌ | info | `debug`, `info`, `warn`, `error` |
| `MAX_FILE_SIZE` | ❌ | 10485760 | Max upload size in bytes (10MB) |
| `SUPPORTED_LANGUAGES` | ❌ | en,es,fr,de,zh,ja | Supported resume languages |

### Database Configuration

```python
# PostgreSQL connection formats
# Standard: postgresql://user:password@localhost:5432/dbname
# SSL: postgresql://user:password@localhost:5432/dbname?sslmode=require
# Socket: postgresql://user@/dbname?unix_socket_dir=/tmp
```

### LLM Configuration

```python
# main.py - Customize LLM settings
LLM_CONFIG = {
    "model": "Qwen/Qwen2-7B-Instruct",  # Model name
    "temperature": 0.3,                  # Creativity (0-1)
    "max_tokens": 2048,                  # Response length
    "top_p": 0.9,                        # Nucleus sampling
}
```

## 🎨 Usage Guide

### Uploading a Resume

1. Navigate to **Resume Analysis** page
2. Click **"Upload Resume"** or drag-and-drop file
3. Select resume language (auto-detected)
4. Click **"Analyze"** to begin processing

**Supported Formats:**
- PDF, DOCX, TXT (text-based)
- JPG, PNG, BMP, TIFF (image-based with OCR)

### Analyzing Results

#### Resume Score Breakdown
- **Content Score** (40%): Relevance, completeness, quantification
- **Format Score** (30%): Structure, readability, ATS compatibility
- **Keyword Score** (30%): Industry match, skill presence

#### ATS Compatibility
- Shows estimated ATS software results (iCIMS, Workday, etc.)
- Highlights formatting issues that may confuse parsers
- Provides specific fix recommendations

#### Skill Gap Analysis
1. View missing skills for target role
2. See skill importance ranking
3. Access curated learning paths
4. Track estimated learning time

### Learning Path Recommendations

After skill gap analysis, view:
- **Free Resources**: YouTube, blogs, documentation
- **Paid Courses**: Coursera, Udemy, LinkedIn Learning (with pricing)
- **Projects**: Hands-on projects to build skills
- **Communities**: Forums, Discord, Reddit communities

## 🧪 Testing

### Run All Tests

```bash
# Frontend tests (React/Vitest)
pnpm test

# Frontend tests with coverage
pnpm test:coverage

# Backend tests (Python/pytest)
pip install pytest pytest-cov
pytest --cov=app

# E2E tests (Playwright)
pnpm test:e2e
```

### Test Coverage

```bash
# Generate coverage reports
pnpm test:coverage              # Frontend
pytest --cov=app --cov-report=html  # Backend
```

## 📊 API Documentation

### Resume Analysis Endpoint

```bash
POST /api/analyze-resume

# Request
{
  "file": <binary>,
  "language": "en",
  "jobDescription": "Optional job description for ATS comparison"
}

# Response
{
  "resumeId": "uuid",
  "scores": {
    "overall": 85,
    "content": 90,
    "format": 75,
    "keywords": 85
  },
  "atsCompatibility": 88,
  "sections": {
    "summary": {...},
    "experience": [...],
    "skills": [...],
    "education": [...]
  }
}
```

### Skill Gap Analysis

```bash
POST /api/skill-gap

# Request
{
  "resumeId": "uuid",
  "targetRole": "Senior Software Engineer",
  "targetCompany": "Google",
  "targetIndustry": "Technology"
}

# Response
{
  "skillGaps": [
    {
      "skill": "Machine Learning",
      "importance": 0.95,
      "currentLevel": 0.3,
      "targetLevel": 0.9,
      "estimatedHours": 200
    }
  ],
  "learningPaths": [...]
}
```

### Learning Recommendations

```bash
GET /api/learning-paths?skill=machine-learning&budget=free

# Response
{
  "skill": "machine-learning",
  "learningPaths": [
    {
      "source": "Coursera",
      "title": "Machine Learning by Andrew Ng",
      "duration": "11 weeks",
      "price": 39.99,
      "difficulty": "Intermediate",
      "rating": 4.8,
      "url": "..."
    }
  ]
}
```

Full API docs available at `/api/docs` (Swagger UI)

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres -d postgres -c "SELECT 1;"

# Verify connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

#### 2. Hugging Face Token Invalid
```bash
# Generate new token at https://huggingface.co/settings/tokens
# Create "Fine-grained" token with read access
# Update .env with new token
HF_TOKEN=hf_your_new_token

# Restart application
```

#### 3. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess  # Windows

# Kill process or use different port
export PORT=8001
```

#### 4. Tesseract OCR Not Found
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

#### 5. Python Module Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

#### 6. Node Module Issues
```bash
# Clear and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Or use npm
npm ci
```

## 📈 Performance Optimization

### Frontend Optimization
- Code splitting with React Router
- Lazy loading of heavy components
- Image optimization with WebP
- Caching strategy with React Query

### Backend Optimization
- Database query optimization with SQLAlchemy
- Connection pooling (10-20 connections)
- Redis caching for LLM responses (optional)
- Async processing for large files

### Database Optimization
```sql
-- Create indexes for common queries
CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_analyses_resume_id ON analyses(resume_id);
CREATE INDEX idx_skills_name ON skills(name);

-- Monitor query performance
EXPLAIN ANALYZE SELECT ...;
```

## 🔒 Security Considerations

### Authentication
- JWT tokens expire after 24 hours
- Refresh tokens stored securely
- Password hashing with bcrypt (12 rounds)

### Data Protection
- Files encrypted at rest
- HTTPS enforced in production
- CORS properly configured
- Rate limiting on API endpoints
- Input validation with Zod/Pydantic

### Best Practices
```bash
# Never commit .env to version control
echo ".env" >> .gitignore

# Use environment-specific configs
NODE_ENV=production pnpm build

# Enable HTTPS in production
# Use nginx/reverse proxy with SSL cert
```

## 🌍 Deployment Options

### 1. Self-Hosted (VPS)
```bash
# Ubuntu/Debian VPS
ssh user@your-vps.com

# Install dependencies
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Deploy with Docker
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Cloud Platforms

#### AWS EC2
```bash
# Launch Ubuntu instance
# Security group: Open ports 80, 443, 5432

docker-compose -f docker-compose.prod.yml up -d
```

#### Heroku
```bash
heroku create your-app-name
git push heroku main
```

#### Railway/Render
- Connect GitHub repository
- Set environment variables
- Auto-deploy on push

### 3. Containerization (Production)
```bash
# Build optimized image
docker build -t resume-analyzer:1.0.0 .

# Push to registry
docker tag resume-analyzer:1.0.0 your-registry/resume-analyzer:1.0.0
docker push your-registry/resume-analyzer:1.0.0

# Deploy with Kubernetes
kubectl apply -f k8s/deployment.yaml
```

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Development Workflow
```bash
# Install dev dependencies
pnpm install --dev

# Run linter and formatter
pnpm format:fix
pnpm lint

# Type checking
pnpm typecheck

# Run tests before commit
pnpm test
```

## 📚 Documentation

- **[API Documentation](docs/API.md)** - Detailed endpoint reference
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design & patterns
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🆘 Support & Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/Dweepangain11dec99/AI-POWERED-RESUME-ANALYZER/issues)
- **Discussions**: [Ask questions and discuss ideas](https://github.com/Dweepangain11dec99/AI-POWERED-RESUME-ANALYZER/discussions)
- **Email**: [Create an issue for support request](https://github.com/Dweepangain11dec99/AI-POWERED-RESUME-ANALYZER/issues)

## 🎓 Learning Resources

- [React Documentation](https://react.dev)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)

## 🚀 Roadmap

### Version 1.1 (Q4 2026)
- [ ] Video resume analysis
- [ ] LinkedIn profile integration
- [ ] Real-time collaboration on resumes
- [ ] Mobile app (React Native)

### Version 1.2 (Q1 2027)
- [ ] Interview preparation module
- [ ] Salary negotiation guidance
- [ ] Company culture matching
- [ ] Blockchain credentials

### Version 2.0 (Q2 2027)
- [ ] Multi-language support (20+ languages)
- [ ] Custom AI model training
- [ ] Enterprise API
- [ ] White-label solution

## ⭐ Show Your Support

If this project helped you, please consider:
- ⭐ Starring the repository
- 🔗 Sharing with your network
- 💬 Leaving feedback in Discussions
- 🐛 Reporting issues
- 🔧 Contributing code

---

**Made with ❤️ by the community**

**Last Updated**: August 2026  
**Status**: 🟢 Active Development
