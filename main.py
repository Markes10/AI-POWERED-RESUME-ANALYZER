"""
Main application entry point
FastAPI web application with PostgreSQL database
"""
import os
import sys
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import uvicorn

from db.config import init_db_pool, get_db_connection, close_db_connection
from routes import ALL_ROUTERS
from routes import resume_fit
from middleware.error_handling import error_handler
from middleware.rate_limiting import RateLimitMiddleware
from services.logging_config import configure_logging, log_startup_info, log_shutdown_info, RequestLoggingMiddleware
from services.environment_checks import run_startup_checks
from app.api_docs import create_custom_openapi

configure_logging()
logger = __import__("structlog").get_logger("main")

REQUIRED_ENV_VARS = ["JWT_SECRET", "DATABASE_URL"]
OPTIONAL_ENV_VARS = ["HF_TOKEN", "REDIS_URL", "QDRANT_HOST", "QDRANT_PORT", "ACCESS_TOKEN_EXPIRE_MINUTES"]


def validate_environment():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        logger.error("missing_required_env_vars", missing_vars=missing)
        if os.getenv("ENVIRONMENT", "development") == "production":
            sys.exit(1)
        else:
            logger.warning("running_in_dev_mode_with_missing_env_vars", missing_vars=missing)

    jwt_secret = os.getenv("JWT_SECRET", "")
    if jwt_secret in ("dev-secret-change-me", "change_this_to_a_secure_random_string", ""):
        logger.warning("weak_jwt_secret_detected", secret_length=len(jwt_secret))
        if os.getenv("ENVIRONMENT") == "production":
            sys.exit(1)


@asynccontextmanager
async def lifespan(app):
    validate_environment()
    log_startup_info()

    try:
        ok = init_db_pool()
        if not ok:
            logger.warning("database_init_failed_continuing_without_db")
    except Exception as e:
        logger.warning("database_init_exception", error=str(e))

    try:
        run_startup_checks()
    except Exception as e:
        logger.warning("environment_checks_failed", error=str(e))

    yield

    log_shutdown_info()


app = FastAPI(
    title="HR AI Platform",
    description="AI-powered HR management platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Currently active HTTP requests",
    ["method", "endpoint"]
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    ACTIVE_REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(duration)
        return response
    finally:
        ACTIVE_REQUESTS.labels(method=request.method, endpoint=request.url.path).dec()


app.middleware("http")(error_handler)

if os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true":
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")),
    )

app.add_middleware(RequestLoggingMiddleware)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if allowed_origins == ["*"] and os.getenv("ENVIRONMENT") == "production":
    logger.warning("cors_allow_all_origins_in_production")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit-Minute", "X-RateLimit-Remaining-Minute", "X-RateLimit-Limit-Hour", "X-RateLimit-Remaining-Hour"],
)


@app.get("/")
async def root():
    return {"message": "HR AI Platform API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    try:
        conn = get_db_connection()
        close_db_connection(conn)
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return {"status": "unhealthy", "database": "disconnected", "detail": str(e)}


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    if os.getenv("PROMETHEUS_METRICS_ENABLED", "true").lower() == "true":
        return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    return PlainTextResponse("Metrics disabled", status_code=404)


# Include routers with version prefix
# Note: resume_fit.api_router already has /api prefix, so include it without version prefix
for r in ALL_ROUTERS:
    if r == resume_fit.api_router:
        app.include_router(r)  # Already has /api prefix
    else:
        app.include_router(r, prefix="/api/v1")

app.openapi = create_custom_openapi(app)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=False,
    )