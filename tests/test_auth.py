"""
Test authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from main import app
from db.models import User, Tenant
import routes.auth as auth_routes
from services.auth import get_password_hash, create_access_token

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Mock password hash for testing to avoid bcrypt issues
def mock_get_password_hash(password: str) -> str:
    return f"mocked_hash_{password}"

def mock_verify_password(plain: str, hashed: str) -> bool:
    return hashed == f"mocked_hash_{plain}"

# Patch the functions in the routes.auth module
auth_routes.get_password_hash = mock_get_password_hash
auth_routes.verify_password = mock_verify_password

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_tenant(test_db):
    """Create a test tenant"""
    tenant = Tenant(
        name="Test Company",
        slug="test-company",
        tier="free",
        status="active",
        settings={},
        custom_limits={}
    )
    db = TestingSessionLocal()
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    db.close()
    return tenant

@pytest.fixture
def test_user(test_db, test_tenant):
    """Create a test user"""
    from services.auth import get_password_hash, create_access_token
    
    # Create a user
    hashed_password = get_password_hash("test123")
    user = User(
        tenant_id=test_tenant.id,
        username="testuser",
        email="test@example.com",
        password_hash=hashed_password
    )
    
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Add access token
    access_token = create_access_token(data={"sub": user.username})
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "access_token": access_token
    }
    
    return user_dict

@pytest.fixture
def client(test_db, test_tenant):
    """Create test client"""
    # Override the application's get_db dependency to use the test DB
    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()

def test_create_user(client, test_tenant):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123",
            "role": "employee"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "password" not in data

def test_login(client, test_tenant):
    # Create a test user
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123",
            "role": "employee"
        }
    )

    # Try to login
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "test123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "testuser"

def test_get_current_user(client, test_tenant, test_user):
    # Create and login a test user
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123",
            "role": "employee"
        }
    )

    login_response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "test123"
        }
    )
    token = login_response.json()["access_token"]

    # Get current user info
    response = client.get(
        "/api/v1/auth/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_update_user(client, test_tenant, test_user):
    # Create and login a test user
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123",
            "role": "employee"
        }
    )

    login_response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "test123"
        }
    )
    token = login_response.json()["access_token"]

    # Update user info
    response = client.put(
        "/api/v1/auth/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "newusername",
            "email": "newemail@example.com"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newusername"
    assert data["email"] == "newemail@example.com"