"""
AI Learning-Path Recommender routes.

Provides endpoints for:
- Hybrid recommendations (collaborative + content-based filtering)
- Graph-based queries (skills to learning paths)
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
import datetime
import random

from services import graph_utils, recommender_utils

router = APIRouter(prefix="/learning", tags=["AI Learning-Path Recommender"])


# -------------------------------
# Request Models
# -------------------------------
class RecsRequest(BaseModel):
    user_id: str
    skills: List[str] = []


class GraphQueryRequest(BaseModel):
    query: str


# -------------------------------
# Endpoints
# -------------------------------

@router.post("/recs/hybrid")
async def recs_hybrid(req: RecsRequest) -> Dict[str, Any]:
    """
    Hybrid recommender (stub).
    Later: Replace with LightFM/implicit for CF + embeddings for content.
    """
    # Stub: pick random courses
    all_courses = [
        "Python for Data Science",
        "Machine Learning Basics",
        "Effective Communication",
        "Leadership 101",
        "Advanced SQL",
        "Project Management Essentials"
    ]
    recommended = random.sample(all_courses, k=min(3, len(all_courses)))

    return {
        "user_id": req.user_id,
        "input_skills": req.skills,
        "recommended_courses": recommended,
        "generated_at": datetime.datetime.utcnow().isoformat()
    }


@router.get("/graph/query")
def query_graph(node: str, depth: int = 1):
    graph = graph_utils.get_graph()
    return graph.query_related(node, depth)


@router.get("/graph/export")
def export_graph():
    graph = graph_utils.get_graph()
    return graph.export_graph()


@router.get("/recs/hybrid")
def hybrid_recs(user_id: str, top_k: int = 5):
    recommender = recommender_utils.get_recommender()
    return {"recommendations": recommender.recommend(user_id, top_k)}