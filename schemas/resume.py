"""
Resume and job matching schemas
"""
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ResumeBase(BaseModel):
    """Base resume schema"""
    resume_text: str
    skills: List[str]

class ResumeCreate(ResumeBase):
    """Resume creation schema"""
    pass

class ResumeResponse(ResumeBase):
    """Resume response schema"""
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class JobBase(BaseModel):
    """Base job schema"""
    title: str
    description: str
    required_skills: List[str]
    department: Optional[str] = None

class JobCreate(JobBase):
    """Job creation schema"""
    pass

class JobResponse(JobBase):
    """Job response schema"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class JobMatchBase(BaseModel):
    """Base job match schema"""
    match_score: float
    skill_overlap_score: float
    matching_skills: List[str]
    missing_skills: List[str]

class JobMatchResponse(JobMatchBase):
    """Job match response schema"""
    job: JobResponse

    class Config:
        from_attributes = True
