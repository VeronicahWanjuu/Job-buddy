"""
Test Block 1: Backend Foundation
Tests config, utilities, services, and app initialization
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from backend.config import config_by_name
from backend.utils.validators import validate_date, validate_email
from backend.utils.helpers import hash_password, verify_password, generate_token
from backend.services.streak_service import update_user_streak
from backend.services.notification_service import create_follow_up_notification
from backend.database.db import db


class TestBlock1Foundation:
    """Test all Block 1 components"""
    
    def test_config_loaded(self):
        """Test config classes"""
        dev_config = config_by_name['development']
        assert dev_config.DEBUG is True
        assert hasattr(dev_config, 'SECRET_KEY')
        print("✅ Config loaded successfully")
    
    def test_validators(self):
        """Test validation functions"""
        # Email validation
        assert validate_email('test@example.com') is True
        assert validate_email('invalid-email') is False
        
        # Date validation
        assert validate_date('2025-01-15') is True
        assert validate_date('2025/01/15') is False
        assert validate_date('invalid') is False
        print("✅ Validators working correctly")
    
    def test_password_hashing(self):
        """Test password utilities"""
        password = "SecurePass123!"
        hashed = hash_password(password)
        
        assert len(hashed) > 0
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False
        print("✅ Password hashing/verification working")
    
    def test_jwt_generation(self):
        """Test JWT token generation"""
        from flask import Flask
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        
        with app.app_context():
            token = generate_token(1)
            assert isinstance(token, str)
            assert len(token) > 50
        print("✅ JWT token generation working")
    
    def test_database_connection(self, app):
        """Test database connection - FIXED"""
        with app.app_context():
            # Database should already be connected by the app fixture
            result = db.execute_one("SELECT 1 as test")
            assert result is not None
            assert result['test'] == 1
        print("✅ Database connection successful")
    
    def test_app_initialization(self):
        """Test Flask app creation"""
        from backend.app import create_app
        app = create_app()
        
        assert app is not None
        assert app.config['DEBUG'] is True
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            assert response.json == {"status": "healthy"}
        print("✅ App initialization successful")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])