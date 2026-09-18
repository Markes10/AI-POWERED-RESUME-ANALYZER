from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from services.ai_feedback_service import AIFeedbackService
from services.hr_analytics_service import HRAnalyticsService
from services.nlp_service import NLPService

router = APIRouter(prefix="/ai", tags=["AI Services"])


# Initialize services
ai_feedback_service = AIFeedbackService()
hr_analytics_service = HRAnalyticsService()
nlp_service = NLPService()

@router.post("/analyze-review")
async def analyze_review(review_text: str) -> Dict[str, Any]:
    """Analyze performance review text"""
    try:
        return ai_feedback_service.analyze_performance_review(review_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend-learning")
async def recommend_learning(user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get personalized learning recommendations"""
    try:
        return ai_feedback_service.recommend_learning_path(user_profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/skill-gaps")
async def analyze_skill_gaps(
    current_skills: List[str],
    target_role: str
) -> Dict[str, Any]:
    """Identify skill gaps"""
    try:
        return ai_feedback_service.identify_skill_gaps(current_skills, target_role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/development-plan")
async def generate_development_plan(
    user_profile: Dict[str, Any],
    skill_gaps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate personalized development plan"""
    try:
        return ai_feedback_service.generate_development_plan(
            user_profile,
            skill_gaps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/turnover-risk")
async def predict_turnover_risk(employee_data: Dict[str, Any]) -> Dict[str, Any]:
    """Predict employee turnover risk"""
    try:
        import pandas as pd
        df = pd.DataFrame([employee_data])
        return hr_analytics_service.predict_turnover_risk(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-sentiment")
async def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze text sentiment"""
    try:
        return nlp_service.analyze_sentiment(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-entities")
async def extract_entities(text: str) -> List[Dict[str, Any]]:
    """Extract named entities from text"""
    try:
        return nlp_service.extract_entities(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer-question")
async def answer_question(
    context: str,
    question: str
) -> Dict[str, Any]:
    """Answer questions based on context"""
    try:
        return nlp_service.answer_question(context, question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
