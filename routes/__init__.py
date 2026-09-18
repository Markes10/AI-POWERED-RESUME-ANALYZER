# Makes routes a package
"""
Routes package initializer.

This file collects all FastAPI routers for different modules
and makes them available for inclusion in main.py.
"""

from fastapi import APIRouter

# Import individual routers
from . import (
    auth,
    resume_fit,
    turnover_retention,
    interview_copilot,
    onboarding_journey,
    performance_feedback,
    compensation_analyzer,
    compensation_market,
    learning_paths,
    attendance_detector,
    diversity_inclusion,
    admin,
    ollama_routes,
)

# Create a parent router to group all sub-routers if desired
api_router = APIRouter()

# Include each module router
api_router.include_router(resume_fit.router)
api_router.include_router(resume_fit.api_router)
api_router.include_router(auth.router)
api_router.include_router(turnover_retention.router)
api_router.include_router(interview_copilot.router)
api_router.include_router(onboarding_journey.router)
api_router.include_router(performance_feedback.router)
api_router.include_router(compensation_analyzer.router)
api_router.include_router(compensation_market.router)
api_router.include_router(learning_paths.router)
api_router.include_router(attendance_detector.router)
api_router.include_router(diversity_inclusion.router)
api_router.include_router(admin.router)
api_router.include_router(ollama_routes.router)

# List of routers if you prefer to include them manually in main.py
ALL_ROUTERS = [
    auth.router,
    resume_fit.router,
    resume_fit.api_router,
    turnover_retention.router,
    interview_copilot.router,
    onboarding_journey.router,
    performance_feedback.router,
    compensation_analyzer.router,
    compensation_market.router,
    learning_paths.router,
    attendance_detector.router,
    diversity_inclusion.router,
    admin.router,
    ollama_routes.router,
]
