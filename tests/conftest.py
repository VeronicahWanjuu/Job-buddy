import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app import create_app
from backend.database.db import db


@pytest.fixture()
def app():
    """Create Flask test app with fresh in-memory DB."""
    
    os.environ["FLASK_ENV"] = "testing"
    app = create_app()
    app.config["TESTING"] = True
    app.config["DATABASE_URL"] = ":memory:"
    
    with app.app_context():
        # Close any existing connection
        db.close()
        
        # Connect to in-memory database
        db.connect(":memory:")
        
        # Load schema (this will create the trigger that auto-creates streaks)
        schema_path = Path(__file__).parent.parent / "backend" / "database" / "schema.sql"
        db.run_schema(str(schema_path))
    
    yield app
    
    # Cleanup
    with app.app_context():
        db.close()


@pytest.fixture()
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture()
def auth_headers(client):
    """Register a user and return Authorization headers."""
    register_data = {
        "email": "test@example.com",
        "password": "Test123!@#",
        "name": "Test User"
    }
    response = client.post(
        "/api/v1/auth/register",
        json=register_data
    )
    
    assert response.status_code == 201, f"Registration failed: {response.get_json()}"
    
    token = response.get_json()["token"]
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@pytest.fixture()
def registered_user(client):
    """Register and return user info with token"""
    register_data = {
        "email": "user@test.com",
        "password": "Pass123!@#",
        "name": "Registered User"
    }
    response = client.post(
        "/api/v1/auth/register",
        json=register_data
    )
    
    assert response.status_code == 201
    data = response.get_json()
    
    return {
        "user": data["user"],
        "token": data["token"],
        "password": register_data["password"]
    }