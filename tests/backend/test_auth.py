"""
Authentication Routes Tests (Block 2 - FR-1)
Tests for /api/v1/auth/* endpoints
Matches your existing test pattern
"""
import pytest
import json
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app import create_app
from database.db import db
from models.user import User

# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture
def test_db():
    """Create test database with schema"""
    test_db_path = 'test_auth.db'
    
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass
    
    db.connect(test_db_path)
    
    # Load schema
    schema_path = backend_path / 'database' / 'schema.sql'
    with open(schema_path, 'r') as f:
        db.connection.executescript(f.read())
    
    yield db
    
    db.close()
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass


@pytest.fixture
def app(test_db):
    """Create Flask app for testing"""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret-key-for-auth-tests"
    })
    
    yield app


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


# ================================================================
# TEST 1: REGISTER - Success & Validation
# ================================================================

def test_register_success(client):
    """
    TEST 1.1: Register new user successfully
    Expected: 201, user object, JWT token, streak auto-created
    """
    response = client.post('/api/v1/auth/register',
        json={
            "email": "john.doe@example.com",
            "password": "SecurePass123!",
            "name": "John Doe"
        },
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    # Check response structure
    assert "user" in data
    assert "token" in data
    
    # Check user data
    assert data["user"]["email"] == "john.doe@example.com"
    assert data["user"]["name"] == "John Doe"
    assert "id" in data["user"]
    assert "created_at" in data["user"]
    
    # Verify token is non-empty
    assert len(data["token"]) > 20
    
    # Verify user exists in database
    user = User.find_by_email("john.doe@example.com")
    assert user is not None
    assert user.name == "John Doe"
    
    print(f"✅ TEST 1.1: User registered successfully - ID={user.id}, Email={user.email}")


def test_register_missing_fields(client):
    """
    TEST 1.2: Register with missing required fields
    Expected: 400 error
    """
    test_cases = [
        ({"password": "Pass123!", "name": "Test"}, "Missing email"),
        ({"email": "test@example.com", "name": "Test"}, "Missing password"),
        ({"email": "test@example.com", "password": "Pass123!"}, "Missing name"),
        ({}, "Missing all fields")
    ]
    
    for payload, description in test_cases:
        response = client.post('/api/v1/auth/register', json=payload)
        assert response.status_code == 400, f"Failed for: {description}"
        data = json.loads(response.data)
        assert "error" in data
    
    print(f"✅ TEST 1.2: Missing fields validation - All {len(test_cases)} cases rejected")


def test_register_invalid_email(client):
    """
    TEST 1.3: Register with invalid email format
    Expected: 400 error
    """
    invalid_emails = [
        "not-an-email",
        "missing@domain",
        "@domain.com",
        "user@"
    ]
    
    for email in invalid_emails:
        response = client.post('/api/v1/auth/register',
            json={
                "email": email,
                "password": "ValidPass123!",
                "name": "Test User"
            }
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "email" in data["error"].lower()
    
    print(f"✅ TEST 1.3: Invalid email validation - {len(invalid_emails)} formats rejected")


def test_register_weak_password(client):
    """
    TEST 1.4: Register with weak passwords
    Expected: 400 error with specific messages
    """
    test_cases = [
        ("short", "Too short"),
        ("alllowercase123!", "No uppercase"),
        ("ALLUPPERCASE123!", "No lowercase"),
        ("NoNumbers!", "No number"),
        ("Password123", "No special char")
    ]
    
    for password, description in test_cases:
        response = client.post('/api/v1/auth/register',
            json={
                "email": f"test_{description.replace(' ', '_')}@example.com",
                "password": password,
                "name": "Test User"
            }
        )
        assert response.status_code == 400, f"Failed for: {description}"
        data = json.loads(response.data)
        assert "error" in data
    
    print(f"✅ TEST 1.4: Weak password validation - All {len(test_cases)} cases rejected")


def test_register_duplicate_email(client):
    """
    TEST 1.5: Register with duplicate email
    Expected: 409 conflict error
    """
    # Register first user
    client.post('/api/v1/auth/register',
        json={
            "email": "duplicate@example.com",
            "password": "Password123!",
            "name": "First User"
        }
    )
    
    # Try to register with same email
    response = client.post('/api/v1/auth/register',
        json={
            "email": "duplicate@example.com",
            "password": "DifferentPass123!",
            "name": "Second User"
        }
    )
    
    assert response.status_code == 400  # Your User.create raises ValueError
    data = json.loads(response.data)
    assert "error" in data
    assert "already" in data["error"].lower()
    
    print(f"✅ TEST 1.5: Duplicate email blocked")


# ================================================================
# TEST 2: LOGIN - Success & Validation
# ================================================================

def test_login_success(client):
    """
    TEST 2.1: Login with valid credentials
    Expected: 200, user object, token, has_completed_onboarding flag
    """
    # First register
    client.post('/api/v1/auth/register',
        json={
            "email": "login@example.com",
            "password": "LoginPass123!",
            "name": "Login User"
        }
    )
    
    # Now login
    response = client.post('/api/v1/auth/login',
        json={
            "email": "login@example.com",
            "password": "LoginPass123!"
        }
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check response structure
    assert "user" in data
    assert "token" in data
    assert "has_completed_onboarding" in data
    
    # Check user data
    assert data["user"]["email"] == "login@example.com"
    assert data["user"]["name"] == "Login User"
    assert "last_login" in data["user"]
    
    # Check onboarding status (should be False for new user)
    assert data["has_completed_onboarding"] == False
    
    # Verify last_login was updated
    user = User.find_by_email("login@example.com")
    assert user.last_login is not None
    
    print(f"✅ TEST 2.1: Login successful - Token length={len(data['token'])}, Last login updated")


def test_login_missing_credentials(client):
    """
    TEST 2.2: Login with missing credentials
    Expected: 400 error
    """
    test_cases = [
        ({"password": "Pass123!"}, "Missing email"),
        ({"email": "test@example.com"}, "Missing password"),
        ({}, "Missing both")
    ]
    
    for payload, description in test_cases:
        response = client.post('/api/v1/auth/login', json=payload)
        assert response.status_code == 400, f"Failed for: {description}"
        data = json.loads(response.data)
        assert "error" in data
    
    print(f"✅ TEST 2.2: Missing credentials validation - All {len(test_cases)} cases rejected")


def test_login_wrong_password(client):
    """
    TEST 2.3: Login with wrong password
    Expected: 401 unauthorized
    """
    # Register user
    client.post('/api/v1/auth/register',
        json={
            "email": "wrongpass@example.com",
            "password": "CorrectPass123!",
            "name": "Test User"
        }
    )
    
    # Try login with wrong password
    response = client.post('/api/v1/auth/login',
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPassword123!"
        }
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    
    print(f"✅ TEST 2.3: Wrong password rejected")


def test_login_nonexistent_user(client):
    """
    TEST 2.4: Login with non-existent email
    Expected: 401 unauthorized
    """
    response = client.post('/api/v1/auth/login',
        json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    
    print(f"✅ TEST 2.4: Non-existent user rejected")


# ================================================================
# TEST 3: GET PROFILE - Protected Route
# ================================================================

def test_get_profile_success(client):
    """
    TEST 3.1: Get profile with valid token
    Expected: 200, complete user profile
    """
    # Register and login
    reg_response = client.post('/api/v1/auth/register',
        json={
            "email": "profile@example.com",
            "password": "ProfilePass123!",
            "name": "Profile User"
        }
    )
    reg_data = json.loads(reg_response.data)
    token = reg_data["token"]
    
    # Get profile
    response = client.get('/api/v1/auth/profile',
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data["email"] == "profile@example.com"
    assert data["name"] == "Profile User"
    assert "id" in data
    assert "created_at" in data
    assert "is_active" in data
    assert "email_notifications_enabled" in data
    
    print(f"✅ TEST 3.1: Profile retrieved - ID={data['id']}, Name={data['name']}")


def test_get_profile_no_token(client):
    """
    TEST 3.2: Get profile without token
    Expected: 401 unauthorized
    """
    response = client.get('/api/v1/auth/profile')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    
    print(f"✅ TEST 3.2: No token rejected")


def test_get_profile_invalid_token(client):
    """
    TEST 3.3: Get profile with invalid token
    Expected: 401 unauthorized
    """
    response = client.get('/api/v1/auth/profile',
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    
    print(f"✅ TEST 3.3: Invalid token rejected")


# ================================================================
# TEST 4: UPDATE PROFILE - Protected Route
# ================================================================

def test_update_profile_success(client):
    """
    TEST 4.1: Update profile successfully
    Expected: 200, updated user data
    """
    # Register
    reg_response = client.post('/api/v1/auth/register',
        json={
            "email": "update@example.com",
            "password": "UpdatePass123!",
            "name": "Original Name"
        }
    )
    reg_data = json.loads(reg_response.data)
    token = reg_data["token"]
    
    # Update profile
    response = client.put('/api/v1/auth/profile',
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Name",
            "email": "updated@example.com"
        }
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data["name"] == "Updated Name"
    assert data["email"] == "updated@example.com"
    
    # Verify in database
    user = User.find_by_email("updated@example.com")
    assert user is not None
    assert user.name == "Updated Name"
    
    print(f"✅ TEST 4.1: Profile updated - Name='{data['name']}', Email='{data['email']}'")


def test_update_profile_invalid_email(client):
    """
    TEST 4.2: Update with invalid email
    Expected: 400 error
    """
    # Register
    reg_response = client.post('/api/v1/auth/register',
        json={
            "email": "validemail@example.com",
            "password": "Pass123!",
            "name": "Test"
        }
    )
    token = json.loads(reg_response.data)["token"]
    
    # Try to update with invalid email
    response = client.put('/api/v1/auth/profile',
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "invalid-email"}
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    
    print(f"✅ TEST 4.2: Invalid email update rejected")


def test_update_profile_duplicate_email(client):
    """
    TEST 4.3: Update to email that's already taken
    Expected: 400 error
    """
    # Register first user
    client.post('/api/v1/auth/register',
        json={
            "email": "taken@example.com",
            "password": "Pass123!",
            "name": "First"
        }
    )
    
    # Register second user
    reg_response = client.post('/api/v1/auth/register',
        json={
            "email": "second@example.com",
            "password": "Pass123!",
            "name": "Second"
        }
    )
    token = json.loads(reg_response.data)["token"]
    
    # Try to update second user's email to first user's email
    response = client.put('/api/v1/auth/profile',
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "taken@example.com"}
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    
    print(f"✅ TEST 4.3: Duplicate email update rejected")


# ================================================================
# TEST 5: DELETE PROFILE - Protected Route & CASCADE
# ================================================================

def test_delete_profile_success(client):
    """
    TEST 5.1: Delete profile successfully
    Expected: 200, user removed from database
    """
    # Register
    reg_response = client.post('/api/v1/auth/register',
        json={
            "email": "delete@example.com",
            "password": "DeletePass123!",
            "name": "Delete User"
        }
    )
    reg_data = json.loads(reg_response.data)
    token = reg_data["token"]
    user_id = reg_data["user"]["id"]
    
    # Delete profile
    response = client.delete('/api/v1/auth/profile',
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    
    # Verify user is deleted
    user = User.find_by_id(user_id)
    assert user is None
    
    print(f"✅ TEST 5.1: Profile deleted - User ID={user_id} removed from database")


def test_delete_profile_cascade(client):
    """
    TEST 5.2: Verify CASCADE delete removes related data
    Expected: All user's data deleted
    """
    from models.company import Company
    from models.application import Application
    
    # Register
    reg_response = client.post('/api/v1/auth/register',
        json={
            "email": "cascade@example.com",
            "password": "CascadePass123!",
            "name": "Cascade User"
        }
    )
    reg_data = json.loads(reg_response.data)
    token = reg_data["token"]
    user_id = reg_data["user"]["id"]
    
    # Create related data
    company = Company.create(user_id, "Test Company")
    app = Application.create(user_id, company.id, "Test Job", status="Planned")
    
    company_id = company.id
    app_id = app.id
    
    # Delete user
    client.delete('/api/v1/auth/profile',
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify CASCADE delete
    assert Company.find_by_id(company_id) is None
    assert Application.find_by_id(app_id) is None
    
    print(f"✅ TEST 5.2: CASCADE DELETE verified - Company and Application deleted")


# ================================================================
# SUMMARY
# ================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 BLOCK 2 - FR-1 AUTHENTICATION TESTS")
    print("="*70 + "\n")
    
    pytest.main([__file__, '-v', '--tb=short', '--color=yes'])
    
    print("\n" + "="*70)
    print("✅ ALL AUTH TESTS COMPLETED!")
    print("="*70)