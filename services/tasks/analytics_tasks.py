"""
Celery tasks for analytics and ML model training.
"""
import logging
from celery import shared_task
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="services.tasks.analytics_tasks.retrain_role_predictor"
)
def retrain_role_predictor(self, csv_path: str = "data/training_dataset.csv") -> Dict[str, Any]:
    """
    Retrain the role predictor model with latest data.
    
    Args:
        csv_path: Path to training data CSV
    
    Returns:
        Dict with training results
    """
    import os
    from ai_engine.role_predictor import role_predictor
    
    if not os.path.exists(csv_path):
        logger.warning(f"Training data not found at {csv_path}")
        return {"status": "skipped", "reason": "Training data not found"}
    
    try:
        logger.info("Starting role predictor retraining")
        success = role_predictor.train_from_csv(csv_path)
        
        if success:
            role_predictor.save_model()
            logger.info("Role predictor retrained and saved successfully")
            return {"status": "success", "model_saved": True}
        else:
            logger.error("Role predictor training failed")
            return {"status": "failed", "reason": "Training failed"}
            
    except Exception as e:
        logger.error(f"Role predictor retraining error: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(
    bind=True,
    name="services.tasks.analytics_tasks.generate_daily_analytics"
)
def generate_daily_analytics(self) -> Dict[str, Any]:
    """
    Generate daily analytics aggregates.
    
    Returns:
        Dict with analytics summary
    """
    from db.database import get_db
    from db.models import Resume, User, Job, JobMatch
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    db = next(get_db())
    
    # Last 24 hours
    since = datetime.utcnow() - timedelta(days=1)
    
    # Resume uploads
    resume_count = db.query(func.count(Resume.id)).filter(Resume.created_at >= since).scalar()
    
    # New users
    user_count = db.query(func.count(User.id)).filter(User.created_at >= since).scalar()
    
    # Job matches created
    match_count = db.query(func.count(JobMatch.id)).filter(JobMatch.created_at >= since).scalar()
    
    # Average match score
    avg_match = db.query(func.avg(JobMatch.match_score)).filter(JobMatch.created_at >= since).scalar()
    
    # Top skills
    from sqlalchemy import text
    skills_result = db.execute(text("""
        SELECT jsonb_array_elements_text(skills) as skill, count(*) as count
        FROM resumes
        WHERE created_at >= :since
        GROUP BY skill
        ORDER BY count DESC
        LIMIT 20
    """), {"since": since}).fetchall()
    
    top_skills = [{"skill": row[0], "count": row[1]} for row in skills_result]
    
    analytics = {
        "date": datetime.utcnow().date().isoformat(),
        "resumes_uploaded": resume_count or 0,
        "new_users": user_count or 0,
        "job_matches": match_count or 0,
        "avg_match_score": float(avg_match) if avg_match else 0.0,
        "top_skills": top_skills,
    }
    
    logger.info(f"Daily analytics generated: {analytics}")
    
    # Store in database (could create an Analytics table)
    return {"status": "success", "analytics": analytics}


@shared_task(
    name="services.tasks.analytics_tasks.calculate_turnover_risk"
)
def calculate_turnover_risk(employee_ids: List[int] = None) -> Dict[str, Any]:
    """
    Calculate turnover risk scores for employees.
    
    Args:
        employee_ids: Optional list of employee IDs to analyze
    
    Returns:
        Dict with risk assessments
    """
    from db.database import get_db
    from db.models import User, PerformanceReview, AttendanceRecord
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    db = next(get_db())
    
    query = db.query(User).filter(User.role == "employee")
    if employee_ids:
        query = query.filter(User.id.in_(employee_ids))
    
    employees = query.all()
    results = []
    
    for emp in employees:
        # Get recent performance reviews
        reviews = db.query(PerformanceReview).filter(
            PerformanceReview.user_id == emp.id,
            PerformanceReview.created_at >= datetime.utcnow() - timedelta(days=180)
        ).all()
        
        # Get attendance records
        attendance = db.query(AttendanceRecord).filter(
            AttendanceRecord.user_id == emp.id,
            AttendanceRecord.check_in >= datetime.utcnow() - timedelta(days=90)
        ).all()
        
        # Simple risk calculation (would use ML model in production)
        risk_factors = []
        risk_score = 0
        
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            if avg_rating < 3:
                risk_factors.append("Low performance ratings")
                risk_score += 30
        
        if attendance:
            anomaly_scores = [a.anomaly_score for a in attendance if a.anomaly_score]
            if anomaly_scores:
                avg_anomaly = sum(anomaly_scores) / len(anomaly_scores)
                if avg_anomaly > 0.7:
                    risk_factors.append("Attendance anomalies")
                    risk_score += 25
        
        # Tenure risk
        tenure_days = (datetime.utcnow() - emp.created_at).days
        if tenure_days < 90:
            risk_factors.append("New hire (< 3 months)")
            risk_score += 20
        elif tenure_days > 1095:  # 3 years
            risk_factors.append("Long tenure - potential stagnation")
            risk_score += 10
        
        risk_level = "Low"
        if risk_score >= 60:
            risk_level = "Critical"
        elif risk_score >= 40:
            risk_level = "High"
        elif risk_score >= 20:
            risk_level = "Medium"
        
        results.append({
            "employee_id": emp.id,
            "name": emp.username,
            "risk_score": min(risk_score, 100),
            "risk_level": risk_level,
            "factors": risk_factors
        })
    
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return {"assessments": results, "generated_at": datetime.utcnow().isoformat()}


@shared_task(
    name="services.tasks.analytics_tasks.generate_compensation_report"
)
def generate_compensation_report(department: str = None) -> Dict[str, Any]:
    """
    Generate compensation fairness report.
    
    Args:
        department: Optional department filter
    
    Returns:
        Dict with compensation analysis
    """
    from db.database import get_db
    from db.models import CompensationRecord, User
    from sqlalchemy import func
    
    db = next(get_db())
    
    query = db.query(
        CompensationRecord,
        User.username,
        User.email,
        User.department
    ).join(User, CompensationRecord.user_id == User.id)
    
    if department:
        query = query.filter(CompensationRecord.department == department)
    
    records = query.all()
    
    if not records:
        return {"error": "No compensation records found"}
    
    # Analyze by department
    dept_stats = {}
    for record, username, email, dept in records:
        if dept not in dept_stats:
            dept_stats[dept] = {"salaries": [], "employees": []}
        dept_stats[dept]["salaries"].append(float(record.salary))
        dept_stats[dept]["employees"].append({
            "username": username,
            "email": email,
            "salary": float(record.salary),
            "bonus": float(record.bonus or 0)
        })
    
    analysis = {}
    for dept, data in dept_stats.items():
        salaries = data["salaries"]
        analysis[dept] = {
            "count": len(salaries),
            "mean": sum(salaries) / len(salaries),
            "median": sorted(salaries)[len(salaries) // 2],
            "min": min(salaries),
            "max": max(salaries),
            "employees": data["employees"]
        }
    
    return {
        "department": department or "all",
        "analysis": analysis,
        "generated_at": datetime.utcnow().isoformat()
    }


@shared_task(
    name="services.tasks.analytics_tasks.analyze_diversity_metrics"
)
def analyze_diversity_metrics(department: str = None) -> Dict[str, Any]:
    """
    Analyze diversity and inclusion metrics.
    
    Returns:
        Dict with diversity analysis
    """
    # Placeholder - would integrate with HRIS demographic data
    return {
        "status": "not_implemented",
        "note": "Requires demographic data integration"
    }


from datetime import datetime