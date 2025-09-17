from fastapi import APIRouter
from app.models.schemas import ResumeUploadRequest, ResumeAnalysisResult
from app.services.analyzer import analyze_resume

router = APIRouter()


@router.post("/analyze", response_model=ResumeAnalysisResult)
async def analyze_resume_endpoint(payload: ResumeUploadRequest):
    """
    Analyze resume text against job description and return match score, skills, and suggestions.
    """
    result = analyze_resume(payload.resume_text, payload.job_description)
    return result 
