from pydantic import BaseModel
from typing import List, Literal

class LearningPathSchema(BaseModel):
    id: str
    title: str
    description: str
    category: str
    difficulty: Literal["Beginner", "Intermediate", "Advanced"]
    duration: str
    modules: int
    progress: int
    completed_modules: int
    skills: List[str]
    format: List[str]
    rating: float
    enrollment: int

class SkillSchema(BaseModel):
    name: str
    current: int
    target: int
    importance: Literal["High", "Medium", "Low"]
    category: str

class RecommendationSchema(BaseModel):
    id: str
    title: str
    type: Literal["Course", "Certification", "Workshop", "Mentoring", "Conference"]
    provider: str
    duration: str
    difficulty: str
    relevance_score: int
    description: str
    skills: List[str]
    cost: str

class AchievementSchema(BaseModel):
    title: str
    date: str
    type: str
