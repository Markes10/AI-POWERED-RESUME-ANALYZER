"""Structured logging configuration using structlog"""
import logging
import sys
import os
from typing import Any, Dict
import structlog
from structlog.stdlib import LoggerFactory


def configure_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "json")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format == "json":
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        shared_processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=shared_processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level),
    )

    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "sqlalchemy"]:
        logging.getLogger(logger_name).handlers = []
        logging.getLogger(logger_name).propagate = True

    return structlog.get_logger()


def get_logger(name: str = None):
    return structlog.get_logger(name)


from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import uuid


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("request")

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        request_id = request.headers.get("x-request-id", "")
        if not request_id:
            request_id = str(uuid.uuid4())[:8]

        structlog.contextvars.bind_contextvars(request_id=request_id)

        method = request.method
        path = request.url.path
        query_string = str(request.query_params)
        client = request.client.host if request.client else "unknown"

        self.logger.info(
            "request_started",
            method=method,
            path=path,
            query=query_string,
            client_ip=client,
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            self.logger.info(
                "request_completed",
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )
            return response
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                "request_failed",
                method=method,
                path=path,
                error=str(e),
                duration_ms=round(duration * 1000, 2),
            )
            raise
        finally:
            structlog.contextvars.clear_contextvars()


def log_startup_info():
    logger = get_logger("startup")
    logger.info(
        "application_starting",
        environment=os.getenv("ENVIRONMENT", "development"),
        version=os.getenv("APP_VERSION", "1.0.0"),
        python_version=sys.version,
    )


def log_shutdown_info():
    logger = get_logger("shutdown")
    logger.info("application_shutting_down")