"""
API documentation and OpenAPI schema configuration
"""
from fastapi.openapi.utils import get_openapi
from typing import Dict


def create_custom_openapi(app):
    """Return a callable that generates custom OpenAPI schema."""
    def custom_openapi() -> Dict:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="HR AI Platform API",
            version="1.0.0",
            description="AI-powered HR management platform API.",
            routes=app.routes,
        )

        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }

        openapi_schema["security"] = [{"bearerAuth": []}]

        openapi_schema["components"]["schemas"]["HTTPError"] = {
            "type": "object",
            "properties": {
                "detail": {"type": "string"},
                "code": {"type": "string"},
            },
        }

        openapi_schema["tags"] = [
            {"name": "Authentication", "description": "Authentication operations"},
            {"name": "Resume", "description": "Resume analysis and job matching"},
            {"name": "Interview Co-pilot", "description": "Interview management and feedback"},
            {"name": "Continuous Performance Feedback Writer", "description": "Performance reviews and feedback"},
            {"name": "AI Learning-Path Recommender", "description": "Learning paths and skill development"},
            {"name": "Attendance Anomaly Detector", "description": "Attendance tracking and analysis"},
            {"name": "Compensation Fairness Analyzer", "description": "Compensation analysis and benchmarking"},
            {"name": "Diversity & Inclusion Analytics", "description": "Diversity and inclusion metrics"},
            {"name": "Predictive Turnover & Retention Bot", "description": "Turnover prediction and retention"},
            {"name": "admin", "description": "Admin operations"},
        ]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi
