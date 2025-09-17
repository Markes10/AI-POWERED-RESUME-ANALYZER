from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.services.matcher import compute_match_score

router = APIRouter()


class MatchRequest(BaseModel):
    resume_text: str = Field(..., description="Plain text extracted from the resume")
    job_description: str = Field(..., description="Text of the job description")


class MatchResponse(BaseModel):
    score: float = Field(..., description="Semantic similarity score between resume and job description")


@router.post("/match", response_model=MatchResponse)
async def match_resume(payload: MatchRequest):
    """
    Compute semantic match score between resume and job description.
    """
    score = compute_match_score(payload.resume_text, payload.job_description)
    return MatchResponse(score=score) 
