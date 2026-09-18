"""
Compensation Market Data API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from db.database import get_db
from db.models import User, CompensationRecord
from services.auth import get_current_user
from services.compensation_market_service import (
    compensation_market_service,
    MarketBenchmark,
    SalaryDataPoint
)

router = APIRouter(prefix="/compensation", tags=["Compensation Market"])


class MarketDataRequest(BaseModel):
    role: str
    location: str = "Remote"
    experience_level: str = "mid"


class MarketBenchmarkResponse(BaseModel):
    role: str
    location: str
    market_median: float
    market_p25: float
    market_p75: float
    internal_median: Optional[float] = None
    variance_pct: Optional[float] = None
    data_points: int
    sources: List[str]


class PayEquityAnalysisRequest(BaseModel):
    department: Optional[str] = None


class PayEquityAnalysisResponse(BaseModel):
    overall: Dict[str, Any]
    by_role: Dict[str, Any]
    by_demographic: Dict[str, Any]
    market_comparison: Dict[str, Any]
    recommendations: List[str]


@router.get("/market-data")
async def get_market_data(
    role: str = Query(...),
    location: str = Query("Remote"),
    experience_level: str = Query("mid"),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get market salary data for a role and location."""
    try:
        data = await compensation_market_service.get_market_data(
            role=role,
            location=location,
            experience_level=experience_level
        )
        
        return [
            {
                "title": d.title,
                "location": d.location,
                "min_salary": d.min_salary,
                "max_salary": d.max_salary,
                "median_salary": d.median_salary,
                "percentile_25": d.percentile_25,
                "percentile_75": d.percentile_75,
                "currency": d.currency,
                "source": d.source,
                "sample_size": d.sample_size,
                "date_collected": d.date_collected.isoformat()
            }
            for d in data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmark")
async def calculate_benchmark(
    request: MarketDataRequest,
    internal_salaries: List[float] = [],
    current_user: User = Depends(get_current_user)
) -> MarketBenchmarkResponse:
    """Calculate market benchmark against internal salaries."""
    try:
        benchmark = compensation_market_service.calculate_benchmark(
            role=request.role,
            location=request.location,
            internal_salaries=internal_salaries
        )
        
        return MarketBenchmarkResponse(
            role=benchmark.role,
            location=benchmark.location,
            market_median=benchmark.market_median,
            market_p25=benchmark.market_p25,
            market_p75=benchmark.market_p75,
            internal_median=benchmark.internal_median,
            variance_pct=benchmark.variance_pct,
            data_points=benchmark.data_points,
            sources=benchmark.sources or []
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pay-equity-analysis")
async def analyze_pay_equity(
    request: PayEquityAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PayEquityAnalysisResponse:
    """Analyze pay equity across the organization."""
    try:
        # Get compensation records
        query = db.query(CompensationRecord).join(User, CompensationRecord.user_id == User.id)
        
        if request.department:
            query = query.filter(CompensationRecord.department == request.department)
        
        records = query.all()
        
        if not records:
            raise HTTPException(status_code=404, detail="No compensation records found")
        
        # Prepare data for analysis
        compensation_data = []
        for record in records:
            user = db.query(User).filter(User.id == record.user_id).first()
            compensation_data.append({
                "role": record.position,
                "department": record.department,
                "salary": float(record.salary),
                "bonus": float(record.bonus or 0),
                "gender": getattr(user, "gender", None),
                "ethnicity": getattr(user, "ethnicity", None),
                "age_group": getattr(user, "age_group", None),
                "department": record.department
            })
        
        # Get market benchmarks for all roles
        roles = set(d["role"] for d in compensation_data)
        market_benchmarks = {}
        
        for role in roles:
            # Use first record's department as location proxy
            dept_record = next((d for d in compensation_data if d["role"] == role), None)
            location = dept_record.get("department", "Remote") if dept_record else "Remote"
            
            benchmark = compensation_market_service.calculate_benchmark(
                role=role,
                location=location,
                internal_salaries=[d["salary"] for d in compensation_data if d["role"] == role]
            )
            market_benchmarks[role] = benchmark
        
        # Run analysis
        from services.compensation_market_service import compensation_market_service
        analysis = compensation_market_service.analyze_pay_equity(
            compensation_data=compensation_data,
            market_benchmarks=market_benchmarks
        )
        
        return PayEquityAnalysisResponse(
            overall=analysis.get("overall", {}),
            by_role=analysis.get("by_role", {}),
            by_demographic=analysis.get("by_demographic", {}),
            market_comparison=analysis.get("market_comparison", {}),
            recommendations=analysis.get("recommendations", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-trends")
async def get_market_trends(
    role: str = Query(...),
    location: str = Query("Remote"),
    months: int = Query(12, ge=1, le=36),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get market salary trends over time (mock data for now)."""
    # In production, this would query historical market data
    import random
    from datetime import datetime, timedelta
    
    base_median = 150000
    data_points = []
    
    for i in range(months):
        date = datetime.utcnow() - timedelta(days=30 * (months - i))
        # Simulate market growth + noise
        growth_factor = 1 + (i * 0.003) + random.uniform(-0.02, 0.02)
        median = int(base_median * growth_factor)
        
        data_points.append({
            "date": date.strftime("%Y-%m"),
            "median": median,
            "p25": int(median * 0.85),
            "p75": int(median * 1.15),
            "sample_size": random.randint(100, 500)
        })
    
    return {
        "role": role,
        "location": location,
        "months": months,
        "trend": "increasing" if data_points[-1]["median"] > data_points[0]["median"] else "stable",
        "growth_rate": round((data_points[-1]["median"] / data_points[0]["median"] - 1) * 100, 1),
        "data": data_points
    }


@router.get("/roles")
async def get_available_roles(current_user: User = Depends(get_current_user)) -> List[str]:
    """Get list of roles with available market data."""
    return [
        "Software Engineer",
        "Senior Software Engineer",
        "Product Manager",
        "Data Scientist",
        "DevOps Engineer",
        "Engineering Manager",
        "QA Engineer",
        "UX Designer",
        "Sales Engineer",
        "Technical Program Manager"
    ]


@router.get("/locations")
async def get_available_locations(current_user: User = Depends(get_current_user)) -> List[str]:
    """Get list of locations with available market data."""
    return [
        "San Francisco, CA",
        "New York, NY",
        "Seattle, WA",
        "Austin, TX",
        "Boston, MA",
        "Los Angeles, CA",
        "Chicago, IL",
        "Denver, CO",
        "Atlanta, GA",
        "Remote",
        "National Average"
    ]