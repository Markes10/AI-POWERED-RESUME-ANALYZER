"""
Tests for error handling middleware
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from middleware.error_handling import (
    AuthError,
    PermissionError,
    NotFoundError,
    ValidationError
)

client = TestClient(app)

def test_auth_error():
    """Test authentication error handling"""
    @app.get("/test-auth-error")
    def test_endpoint():
        raise AuthError("Invalid credentials")
    
    response = client.get("/test-auth-error")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

def test_permission_error():
    """Test permission error handling"""
    @app.get("/test-permission-error")
    def test_endpoint():
        raise PermissionError("Insufficient permissions")
    
    response = client.get("/test-permission-error")
    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}

def test_not_found_error():
    """Test not found error handling"""
    @app.get("/test-not-found")
    def test_endpoint():
        raise NotFoundError("Resource not found")
    
    response = client.get("/test-not-found")
    assert response.status_code == 404
    assert response.json() == {"detail": "Resource not found"}

def test_validation_error():
    """Test validation error handling"""
    @app.get("/test-validation")
    def test_endpoint():
        raise ValidationError("Invalid data")
    
    response = client.get("/test-validation")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid data"}

def test_unexpected_error():
    """Test unexpected error handling"""
    @app.get("/test-unexpected")
    def test_endpoint():
        raise Exception("Unexpected error")
    
    response = client.get("/test-unexpected")
    assert response.status_code == 500
    assert response.json() == {"detail": "An unexpected error occurred"}
