from pydantic import BaseModel, Field
from typing import List, Optional


class ResumeUploadRequest(BaseModel):
    job_description: str = Field(..., description="Job description text to match against")
    resume_text: str = Field(..., description="Extracted plain text from the uploaded resume")


class ResumeAnalysisResult(BaseModel):
    score: float = Field(..., description="Match score between resume and job description")
    skills: List[str] = Field(..., description="Skills extracted from the resume")
    missing_keywords: List[str] = Field(..., description="Keywords expected but missing in resume")
    suggestions: List[str] = Field(..., description="Suggestions to improve resume relevance")


class ResumeHistoryItem(BaseModel):
    id: int
    created_at: str
    score: float
    skills: Optional[str]
    missing_keywords: Optional[str]
    suggestions: Optional[str]


class PDFExportRequest(BaseModel):
    analysis: ResumeAnalysisResult