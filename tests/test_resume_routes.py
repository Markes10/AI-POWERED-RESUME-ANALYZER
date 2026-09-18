"""
Tests for resume API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import json

def test_upload_resume(client: TestClient, test_user):
    """Test resume upload endpoint"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    resume_data = {
        "resume_text": "Python developer with 5 years experience in Django and React"
    }
    
    response = client.post("/api/v1/resume/upload", json=resume_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert data["user_id"] == test_user["id"]
    assert "skills" in data
    assert isinstance(data["skills"], list)

def test_get_my_resumes(client: TestClient, test_user):
    """Test getting user's resumes"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    
    # First upload a resume
    resume_data = {
        "resume_text": "Python developer with 5 years experience in Django and React"
    }
    client.post("/api/v1/resume/upload", json=resume_data, headers=headers)
    
    # Get resumes
    response = client.get("/api/v1/resume/my-resumes", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["user_id"] == test_user["id"]

def test_match_resume(client: TestClient, test_user):
    """Test resume-job matching"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    
    # Upload a resume
    resume_data = {
        "resume_text": "Python developer with experience in Django, FastAPI, and React"
    }
    resume_response = client.post("/api/v1/resume/upload", json=resume_data, headers=headers)
    resume_id = resume_response.json()["id"]
    
    # Test matching
    response = client.post(f"/api/v1/resume/{resume_id}/match?top_k=3", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    # Should return matches even if no jobs in DB (mock data)

def test_delete_resume(client: TestClient, test_user):
    """Test deleting a resume"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    
    # Upload a resume first
    resume_data = {
        "resume_text": "Python developer with 5 years experience"
    }
    resume_response = client.post("/api/v1/resume/upload", json=resume_data, headers=headers)
    resume_id = resume_response.json()["id"]
    
    # Delete the resume
    response = client.delete(f"/api/v1/resume/{resume_id}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "deleted successfully" in data["message"]

def test_upload_resume_unauthorized(client: TestClient):
    """Test resume upload without authorization"""
    resume_data = {
        "resume_text": "Python developer"
    }
    
    response = client.post("/api/v1/resume/upload", json=resume_data)
    assert response.status_code == 401

def test_get_resumes_unauthorized(client: TestClient):
    """Test getting resumes without authorization"""
    response = client.get("/api/v1/resume/my-resumes")
    assert response.status_code == 401

def test_match_resume_unauthorized(client: TestClient):
    """Test resume matching without authorization"""
    response = client.post("/api/v1/resume/1/match")
    assert response.status_code == 401

def test_delete_resume_unauthorized(client: TestClient):
    """Test deleting resume without authorization"""
    response = client.delete("/api/v1/resume/1")
    assert response.status_code == 401

def test_match_nonexistent_resume(client: TestClient, test_user):
    """Test matching a nonexistent resume"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    
    response = client.post("/api/v1/resume/999999/match", headers=headers)
    assert response.status_code == 404

def test_delete_nonexistent_resume(client: TestClient, test_user):
    """Test deleting a nonexistent resume"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    
    response = client.delete("/api/v1/resume/999999", headers=headers)
    assert response.status_code == 404

def test_upload_empty_resume(client: TestClient, test_user):
    """Test uploading an empty resume"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    resume_data = {
        "resume_text": ""
    }
    
    response = client.post("/api/v1/resume/upload", json=resume_data, headers=headers)
    # Should handle empty text gracefully
    assert response.status_code in [200, 400]

@pytest.mark.parametrize("top_k", [1, 3, 5])
def test_match_resume_top_k(client: TestClient, test_user, top_k):
    """Test resume matching with different top_k values"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    
    # Upload a resume
    resume_data = {
        "resume_text": "Python developer with experience in Django and React"
    }
    resume_response = client.post("/api/v1/resume/upload", json=resume_data, headers=headers)
    resume_id = resume_response.json()["id"]
    
    # Test matching with different top_k values
    response = client.post(f"/api/v1/resume/{resume_id}/match?top_k={top_k}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= top_k

def test_resume_upload_with_special_characters(client: TestClient, test_user):
    """Test resume upload with special characters"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    resume_data = {
        "resume_text": "Python/C++ developer with 5+ years of experience in AI & ML"
    }
    
    response = client.post("/api/v1/resume/upload", json=resume_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "skills" in data
    assert isinstance(data["skills"], list)