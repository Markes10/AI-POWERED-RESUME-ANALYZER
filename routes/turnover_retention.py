"""
Predictive Turnover & Retention Bot routes.

Provides endpoints for:
- Predicting employee turnover risk
- Suggesting retention strategies
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
import datetime
import random
from services import churn_model

router = APIRouter(prefix="/turnover", tags=["Predictive Turnover & Retention Bot"])


# -------------------------------
# Request Models
# -------------------------------
class EmployeeFeatures(BaseModel):
    employee_id: str
    engagement_score: float
    performance_score: float
    tenure_months: int
    compensation_ratio: float


class BatchPredictRequest(BaseModel):
    employees: List[EmployeeFeatures]


# -------------------------------
# Endpoints
# -------------------------------

@router.post("/predict")
def predict_turnover(payload: Dict[str, Any]):
    # Features: engagement, performance, tenure, compensation ratio
    prediction = churn_model.predict(payload)
    return prediction

@router.post("/predict/batch")
async def predict_batch(req: BatchPredictRequest) -> Dict[str, Any]:
    """
    Predict turnover risk for a batch of employees (stub).
    """
    results = []
    for emp in req.employees:
        risk_score = round(random.uniform(0.0, 1.0), 3)
        risk_label = "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
        results.append({
            "employee_id": emp.employee_id,
            "risk_score": risk_score,
            "risk_label": risk_label
        })

    return {
        "total_employees": len(req.employees),
        "predictions": results,
        "predicted_at": datetime.datetime.utcnow().isoformat()
    }


@router.get("/recommendations/{employee_id}")
async def retention_recommendations(employee_id: str) -> Dict[str, Any]:
    """
    Recommend retention strategies for an employee (stub).
    Later: Replace with rules-based + ML-driven strategies.
    """
    strategies = [
        "Offer career development opportunities",
        "Review compensation package",
        "Assign a mentor",
        "Improve work-life balance policies",
        "Conduct regular check-ins"
    ]
    selected = random.sample(strategies, k=2)

    return {
        "employee_id": employee_id,
        "recommendations": selected,
        "generated_at": datetime.datetime.utcnow().isoformat()
    }
