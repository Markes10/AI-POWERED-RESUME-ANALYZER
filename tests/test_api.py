"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_resume_upload_endpoint(client: TestClient, test_user, sample_resume_text):
    """Test resume upload endpoint"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.post(
        "/api/v1/resume/upload",
        json={"resume_text": sample_resume_text},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "skills" in data
    assert len(data["skills"]) > 0

def test_job_matching_endpoint(client: TestClient, test_user, sample_resume_text, sample_job_posting):
    """Test job matching endpoint"""
    # First upload a resume
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    resume_response = client.post(
        "/api/v1/resume/upload",
        json={"resume_text": sample_resume_text},
        headers=headers
    )
    resume_id = resume_response.json()["id"]
    
    # Create a job (POST only endpoint on /api/jobs/create)
    job_response = client.post(
        "/api/jobs/create",
        json=sample_job_posting,
        headers=headers
    )
    assert job_response.status_code == 200
    
    # Test job matching (POST only)
    response = client.post(
        f"/api/v1/resume/{resume_id}/match",
        headers=headers
    )
    assert response.status_code == 200
    matches = response.json()
    assert isinstance(matches, list)

def test_unauthorized_access(client: TestClient, sample_resume_text):
    """Test unauthorized access to protected endpoints"""
    # Try without auth token
    response = client.post(
        "/api/v1/resume/upload",
        json={"resume_text": sample_resume_text}
    )
    assert response.status_code == 401

def test_invalid_resume_upload(client: TestClient, test_user):
    """Test resume upload with invalid data"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.post(
        "/api/v1/resume/upload",
        json={"resume_text": ""},  # Empty resume text
        headers=headers
    )
    assert response.status_code == 400

@pytest.mark.parametrize("endpoint,method", [
    ("/api/v1/resume/upload", "post"),
    ("/api/jobs/create", "post"),
    ("/api/v1/resume/1/match", "post"),
])
def test_protected_endpoints(client: TestClient, endpoint, method):
    """Test that protected endpoints require authentication"""
    response = getattr(client, method.lower())(endpoint)
    assert response.status_code in (401, 405)  # 401 for auth required, 405 if method not allowed but endpoint exists
    assert "detail" in response.json()

def test_resume_list_endpoint(client: TestClient, test_user):
    """Test getting list of user's resumes"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.get("/api/v1/resume/my-resumes", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)