"""
Tests for resume service functionality
"""
import pytest
from services.resume_service import resume_service
from services.skill_extractor import extract_skills

def test_extract_skills(sample_resume_text):
    """Test skill extraction from resume text"""
    skills = extract_skills(sample_resume_text)
    assert isinstance(skills, list)
    assert "Python" in skills
    assert "React" in skills
    assert "FastAPI" in skills
    assert len(skills) > 0

def test_create_resume(test_db, test_user, test_tenant, sample_resume_text):
    """Test resume creation"""
    resume = resume_service.create_resume(
        user_id=test_user["id"],
        tenant_id=test_tenant.id,
        resume_text=sample_resume_text
    )
    assert resume["id"] is not None
    assert resume["user_id"] == test_user["id"]
    assert resume["tenant_id"] == test_tenant.id
    assert isinstance(resume["skills"], list)
    assert len(resume["skills"]) > 0

def test_get_user_resumes(test_db, test_user, test_tenant, sample_resume_text):
    """Test retrieving user resumes"""
    # Create a resume first
    resume_service.create_resume(
        user_id=test_user["id"],
        tenant_id=test_tenant.id,
        resume_text=sample_resume_text
    )
    
    # Get user resumes
    resumes = resume_service.get_user_resumes(test_user["id"], test_tenant.id)
    assert isinstance(resumes, list)
    assert len(resumes) > 0
    assert resumes[0]["user_id"] == test_user["id"]
    assert resumes[0]["tenant_id"] == test_tenant.id

def test_match_jobs(test_db, test_user, test_tenant, sample_resume_text, sample_job_posting):
    """Test job matching functionality"""
    # Create a resume
    resume = resume_service.create_resume(
        user_id=test_user["id"],
        tenant_id=test_tenant.id,
        resume_text=sample_resume_text
    )
    
    # Create a job in the database
    from db.database import DatabaseOperations
    job_ops = DatabaseOperations("jobs")
    job_posting = {**sample_job_posting, "tenant_id": test_tenant.id}
    job_id = job_ops.create(job_posting)
    
    # Test job matching
    matches = resume_service.match_jobs(resume["id"], top_k=1)
    assert isinstance(matches, list)
    assert len(matches) > 0
    assert matches[0]["job"]["id"] == job_id
    assert isinstance(matches[0]["match_score"], float)
    assert isinstance(matches[0]["matching_skills"], list)

@pytest.mark.parametrize("resume_text,expected_skills", [
    ("Python developer with React experience", ["Python", "React"]),
    ("AWS and Docker expert", ["AWS", "Docker"]),
    ("No technical skills mentioned", [])
])
def test_skill_extraction_variations(resume_text, expected_skills):
    """Test skill extraction with various inputs"""
    skills = extract_skills(resume_text)
    for skill in expected_skills:
        assert skill in skills

def test_resume_creation_validation():
    """Test resume creation with invalid inputs"""
    with pytest.raises(ValueError):
        resume_service.create_resume(user_id=None, tenant_id=1, resume_text="")
    
    with pytest.raises(ValueError):
        resume_service.create_resume(user_id=1, tenant_id=1, resume_text="")