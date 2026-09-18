"""
Learning paths service module
"""
import json
from typing import List, Dict, Any, Optional
from db.database import get_db_connection, close_db_connection
from schemas.learning import (
    LearningPathSchema,
    SkillSchema,
    RecommendationSchema,
    AchievementSchema
)


class LearningService:
    """Service class for learning path operations used by AI feedback service."""

    def get_all_paths(self) -> List[Dict[str, Any]]:
        return [
            {"id": "1", "title": "Python for Data Science", "category": "Technical"},
            {"id": "2", "title": "Machine Learning Basics", "category": "Technical"},
            {"id": "3", "title": "Effective Communication", "category": "Soft Skills"},
            {"id": "4", "title": "Leadership 101", "category": "Management"},
            {"id": "5", "title": "Advanced SQL", "category": "Technical"},
            {"id": "6", "title": "Project Management Essentials", "category": "Management"},
        ]

    def get_role_skills(self, role: str) -> List[str]:
        role_skill_map = {
            "software engineer": ["python", "javascript", "git", "sql", "api design"],
            "data scientist": ["python", "machine learning", "statistics", "sql", "data visualization"],
            "product manager": ["agile", "user research", "data analysis", "roadmapping", "communication"],
            "hr specialist": ["recruiting", "employee relations", "compliance", "training", "compensation"],
        }
        return role_skill_map.get(role.lower(), ["communication", "problem solving", "teamwork"])

    def find_courses(self, skill: str) -> List[Dict[str, Any]]:
        courses = {
            "python": [{"title": "Python Mastery", "provider": "Coursera", "duration": "6 weeks"}],
            "machine learning": [{"title": "ML Specialization", "provider": "Coursera", "duration": "12 weeks"}],
            "sql": [{"title": "SQL Fundamentals", "provider": "Udemy", "duration": "4 weeks"}],
        }
        return courses.get(skill.lower(), [{"title": f"{skill.title()} Fundamentals", "provider": "Online", "duration": "4 weeks"}])


async def get_all_learning_paths() -> List[LearningPathSchema]:
    """Get all learning paths from database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM learning_paths")
        paths = cursor.fetchall()
        return [LearningPathSchema(
            id=path['id'],
            title=path['title'],
            description=path['description'],
            category=path['category'],
            difficulty=path['difficulty'],
            duration=path['duration'],
            modules=path['modules'],
            progress=path['progress'],
            completed_modules=path['completed_modules'],
            skills=json.loads(path['skills']),
            format=json.loads(path['format']),
            rating=path['rating'],
            enrollment=path['enrollment']
        ) for path in paths]
    finally:
        cursor.close()
        close_db_connection(conn)

async def get_all_skills() -> List[SkillSchema]:
    """Get all skills from .database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM skills")
        skills = cursor.fetchall()
        return [SkillSchema(
            name=skill['name'],
            current=skill['current'],
            target=skill['target'],
            importance=skill['importance'],
            category=skill['category']
        ) for skill in skills]
    finally:
        cursor.close()
        close_db_connection(conn)

async def get_all_recommendations() -> List[RecommendationSchema]:
    """Get all recommendations from .database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM recommendations")
        recommendations = cursor.fetchall()
        return [RecommendationSchema(
            id=rec['id'],
            title=rec['title'],
            type=rec['type'],
            provider=rec['provider'],
            duration=rec['duration'],
            difficulty=rec['difficulty'],
            relevance_score=rec['relevance_score'],
            description=rec['description'],
            skills=json.loads(rec['skills']),
            cost=rec['cost']
        ) for rec in recommendations]
    finally:
        cursor.close()
        close_db_connection(conn)

async def get_all_achievements() -> List[AchievementSchema]:
    """Get all achievements from .database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM achievements")
        achievements = cursor.fetchall()
        return [AchievementSchema(
            title=ach['title'],
            date=ach['date'].strftime('%Y-%m-%d'),
            type=ach['type']
        ) for ach in achievements]
    finally:
        cursor.close()
        close_db_connection(conn)
