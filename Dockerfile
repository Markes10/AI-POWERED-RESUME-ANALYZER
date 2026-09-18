# Multi-stage Dockerfile for HR AI Platform
# Build stage for Python dependencies
FROM python:3.11-slim AS python-builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Build stage for Node.js frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app

RUN npm install -g pnpm@10

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY index.html vite.config.ts tsconfig.json tailwind.config.ts postcss.config.js ./
COPY client/ ./client/
COPY shared/ ./shared/

RUN pnpm install --frozen-lockfile
RUN pnpm run build:client

# Runtime stage
FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-builder /root/.local /root/.local

COPY --from=frontend-builder /app/dist ./static

COPY . .

RUN mkdir -p uploads/resumes

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]