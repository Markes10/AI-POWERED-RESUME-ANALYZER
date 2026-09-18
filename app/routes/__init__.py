"""
Routes initialization
Import and collect all route handlers from the top-level routes package
"""
from fastapi import APIRouter

from routes import ALL_ROUTERS

__all__ = ["ALL_ROUTERS"]
