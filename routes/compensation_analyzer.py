"""
Compensation Fairness Analyzer routes.

Provides endpoints for analyzing pay equity and detecting bias
across gender, ethnicity, and other attributes.
"""

from fastapi import APIRouter, Depends
import random
import datetime
from services.auth import allow_admin, get_current_user
from services import fairness_utils

router = APIRouter(prefix="/compensation", tags=["Compensation Fairness Analyzer"])


# -------------------------------
# Endpoints
# -------------------------------


@router.get('/fairness/metrics')
def fairness_metrics(current_user = Depends(allow_admin)):
    """
    Return stubbed fairness/bias metrics.
    Later: Replace with real analysis using AIF360 or Fairlearn.
    """
    # Stub: fake pay gap numbers
    return {
        "gender_pay_gap": round(random.uniform(0.05, 0.15), 3),  # 5-15%
        "ethnicity_pay_gap": round(random.uniform(0.08, 0.20), 3),
        "metrics_generated_at": datetime.datetime.utcnow().isoformat(),
        "recommendation": "Investigate compensation policies for equity."
    }


@router.get('/benchmarks')
def benchmarks(current_user = Depends(allow_admin)):
    """
    Return stubbed salary benchmarks by role/department.
    Later: Replace with real statistical analysis of your DB.
    """
    # Stub salary benchmarks
    salary_benchmarks = {
        "Software Engineer I": 70000,
        "Software Engineer II": 90000,
        "Data Scientist": 95000,
        "HR Specialist": 60000,
    }

    return {
        "benchmarks": salary_benchmarks,
        "benchmark_source": "Stub dataset",
        "generated_at": datetime.datetime.utcnow().isoformat()
    }

@router.post('/analyze')
def analyze_compensation(payload: dict, current_user = Depends(allow_admin)):
    result = fairness_utils.analyze_pay(payload.get("data", []))
    return result