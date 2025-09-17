from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

router = APIRouter()


# Feedback schema
class FeedbackRequest(BaseModel):
    analysis_id: int = Field(..., description="ID of the resume analysis result")
    user_id: Optional[int] = Field(None, description="Optional user ID if available")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    comments: Optional[str] = Field(None, description="Optional user comments")


# In-memory store (replace with DB in production)
feedback_store = []


@router.post("/feedback")
async def submit_feedback(payload: FeedbackRequest):
    """
    Submit feedback for a resume analysis result.
    """
    feedback_entry = {
        "analysis_id": payload.analysis_id,
        "user_id": payload.user_id,
        "rating": payload.rating,
        "comments": payload.comments,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Simulate DB insert
    feedback_store.append(feedback_entry)

    return {"message": "Feedback submitted successfully", "data": feedback_entry}