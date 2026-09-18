"""
Celery tasks for resume processing.
Handles async resume parsing, analysis, and matching.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="services.tasks.resume_tasks.process_resume"
)
def process_resume(self, file_path: str, user_id: int, filename: str, job_description: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a resume file asynchronously.
    
    Args:
        file_path: Path to the uploaded resume file
        user_id: ID of the user who uploaded the resume
        filename: Original filename
        job_description: Optional job description for matching
    
    Returns:
        Dict with processing results
    """
    try:
        logger.info(f"Processing resume {filename} for user {user_id}")
        
        # Import services locally to avoid circular imports
        from services.resume_service import ResumeService
        from services.embedding_service import embedding_service
        from services.skill_extractor import extract_skills
        from ai_engine.role_predictor import role_predictor
        from db.database import get_db
        from db.models import Resume, User
        
        db = next(get_db())
        
        # Extract text from file
        from routes.resume_fit import extract_text_from_path
        resume_text = extract_text_from_path(file_path, filename)
        
        if not resume_text or not resume_text.strip():
            raise ValueError("Could not extract text from resume")
        
        # Extract skills
        skills = extract_skills(resume_text)
        
        # Get role predictions
        role_predictions = role_predictor.predict(resume_text, top_k=3)
        
        # Generate embedding
        embedding = embedding_service.embed_text(resume_text)
        
        # Convert embedding to hex for storage
        import numpy as np
        import json
        try:
            vec_np = np.asarray(embedding, dtype=np.float32)
            vector_hex = vec_np.tobytes().hex()
        except Exception:
            vector_hex = json.dumps(embedding.tolist() if hasattr(embedding, "tolist") else embedding)
        
        # Calculate match score if job description provided
        match_score = None
        if job_description:
            job_embedding = embedding_service.embed_text(job_description)
            match_score = embedding_service.calculate_similarity(embedding, job_embedding)
        
        # Store in database
        resume_record = Resume(
            user_id=user_id,
            resume_text=resume_text,
            skills=skills,
            vector_embedding=vector_hex,
        )
        db.add(resume_record)
        db.commit()
        db.refresh(resume_record)
        
        result = {
            "resume_id": resume_record.id,
            "skills": skills,
            "role_predictions": role_predictions,
            "match_score": match_score,
            "status": "completed"
        }
        
        logger.info(f"Resume {resume_record.id} processed successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Failed to process resume: {exc}")
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for resume processing")
            return {"status": "failed", "error": str(exc)}


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="services.tasks.resume_tasks.batch_process_resumes"
)
def batch_process_resumes(self, file_paths: List[Dict[str, Any]], user_id: int) -> Dict[str, Any]:
    """
    Process multiple resumes in batch.
    
    Args:
        file_paths: List of dicts with file_path, filename, job_description
        user_id: ID of the user
    
    Returns:
        Dict with batch processing results
    """
    results = []
    failed = 0
    
    for item in file_paths:
        try:
            result = process_resume.delay(
                item["file_path"],
                user_id,
                item["filename"],
                item.get("job_description")
            ).get(timeout=300)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to process {item['filename']}: {e}")
            failed += 1
            results.append({"filename": item["filename"], "status": "failed", "error": str(e)})
    
    return {
        "total": len(file_paths),
        "successful": len(results) - failed,
        "failed": failed,
        "results": results
    }


@shared_task(
    bind=True,
    name="services.tasks.resume_tasks.match_resume_to_jobs"
)
def match_resume_to_jobs(self, resume_id: int, top_k: int = 10) -> Dict[str, Any]:
    """
    Match a resume against all jobs in the database.
    
    Args:
        resume_id: ID of the resume to match
        top_k: Number of top matches to return
    
    Returns:
        Dict with job matches
    """
    from db.database import get_db
    from db.models import Resume, Job
    from services.embedding_service import embedding_service
    
    db = next(get_db())
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return {"error": "Resume not found", "matches": []}
    
    jobs = db.query(Job).all()
    matches = []
    
    for job in jobs:
        resume_embedding = embedding_service.embed_text(resume.resume_text or "")
        job_embedding = embedding_service.embed_text(job.description or "")
        similarity = embedding_service.calculate_similarity(resume_embedding, job_embedding)
        
        resume_skills = set(resume.skills or [])
        job_skills = set(job.required_skills or [])
        skill_overlap = len(resume_skills.intersection(job_skills))
        skill_overlap_score = skill_overlap / len(job_skills) if job_skills else 0
        
        matches.append({
            "job_id": job.id,
            "job_title": job.title,
            "department": job.department,
            "match_score": float(similarity),
            "skill_overlap_score": float(skill_overlap_score),
            "matching_skills": list(resume_skills.intersection(job_skills)),
            "missing_skills": list(job_skills - resume_skills)
        })
    
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {"resume_id": resume_id, "matches": matches[:top_k]}


@shared_task(
    name="services.tasks.resume_tasks.generate_resume_report"
)
def generate_resume_report(resume_id: int, format: str = "pdf") -> Dict[str, Any]:
    """
    Generate a detailed report for a resume.
    
    Args:
        resume_id: ID of the resume
        format: Output format (pdf, json, docx)
    
    Returns:
        Dict with report path or data
    """
    from db.database import get_db
    from db.models import Resume
    from services.resume_advisor import suggest_improvements
    
    db = next(get_db())
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return {"error": "Resume not found"}
    
    # Get suggestions
    suggestions = suggest_improvements(resume.resume_text or "", None)
    
    report_data = {
        "resume_id": resume_id,
        "skills": resume.skills,
        "suggestions": suggestions,
        "generated_at": str(datetime.utcnow()),
    }
    
    if format == "json":
        return {"format": "json", "data": report_data}
    
    # For PDF, would use the pdfExport utility
    return {"format": format, "data": report_data, "note": "PDF generation via frontend"}


from datetime import datetime