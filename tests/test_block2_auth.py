"""
Test Block 2: Authentication Endpoints
"""

import pytest


class TestBlock2Authentication:
    """Test all authentication endpoints"""
    
    def test_register_valid_user(self, client):
        """Test POST /api/v1/auth/register with valid data"""
        response = client.post('/api/v1/auth/register', json={
            "email": "pytest.user@example.com",
            "password": "SecurePass123!",
            "name": "Pytest User"
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'user' in data
        assert 'token' in data
        assert data['user']['email'] == 'pytest.user@example.com'
        print(f"✅ User registered: {data['user']['email']}")
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/api/v1/auth/register', json={
            "email": "invalid-email",
            "password": "SecurePass123!",
            "name": "Test"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        print(f"✅ Invalid email rejected: {data['error']}")
    
    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        response = client.post('/api/v1/auth/register', json={
            "email": "test2@example.com",
            "password": "weak",
            "name": "Test"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Password' in data['error']
        print(f"✅ Weak password rejected: {data['error']}")
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # Register first user
        client.post('/api/v1/auth/register', json={
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "name": "First User"
        })
        
        # Try to register with same email
        response = client.post('/api/v1/auth/register', json={
            "email": "duplicate@example.com",
            "password": "AnotherPass123!",
            "name": "Second User"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'already exists' in data['error'].lower()
        print(f"✅ Duplicate email rejected: {data['error']}")
    
    def test_login_valid(self, client):
        """Test POST /api/v1/auth/login with valid credentials"""
        # First register
        client.post('/api/v1/auth/register', json={
            "email": "login.test@example.com",
            "password": "SecurePass123!",
            "name": "Login Test"
        })
        
        # Then login
        response = client.post('/api/v1/auth/login', json={
            "email": "login.test@example.com",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert 'token' in data
        assert 'has_completed_onboarding' in data
        print(f"✅ Login successful, token received")
    
    def test_login_invalid_password(self, client):
        """Test login with wrong password"""
        # Register user
        client.post('/api/v1/auth/register', json={
            "email": "wrong.pass@example.com",
            "password": "SecurePass123!",
            "name": "Test"
        })
        
        # Try wrong password
        response = client.post('/api/v1/auth/login', json={
            "email": "wrong.pass@example.com",
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        print(f"✅ Wrong password rejected")
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        response = client.post('/api/v1/auth/login', json={
            "email": "notfound@example.com",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        print(f"✅ Non-existent user rejected")
    
    def test_get_profile_protected(self, client):
        """Test GET /api/v1/auth/profile (requires token)"""
        # Register and login
        reg_response = client.post('/api/v1/auth/register', json={
            "email": "profile.test@example.com",
            "password": "SecurePass123!",
            "name": "Profile Test"
        })
        token = reg_response.get_json()['token']
        
        # Get profile with token
        response = client.get('/api/v1/auth/profile', headers={
            'Authorization': f'Bearer {token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == 'profile.test@example.com'
        assert data['name'] == 'Profile Test'
        print(f"✅ Profile retrieved: {data['name']}")
    
    def test_get_profile_no_token(self, client):
        """Test profile access without token"""
        response = client.get('/api/v1/auth/profile')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        print(f"✅ Unauthorized access blocked")
    
    def test_get_profile_invalid_token(self, client):
        """Test profile access with invalid token"""
        response = client.get('/api/v1/auth/profile', headers={
            'Authorization': 'Bearer invalid_token_here'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        print(f"✅ Invalid token rejected")
    
    def test_update_profile(self, client):
        """Test PUT /api/v1/auth/profile"""
        # Register
        reg_response = client.post('/api/v1/auth/register', json={
            "email": "update.test@example.com",
            "password": "SecurePass123!",
            "name": "Original Name"
        })
        token = reg_response.get_json()['token']
        
        # Update name
        response = client.put('/api/v1/auth/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={"name": "Updated Name"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Name'
        print(f"✅ Profile updated: {data['name']}")
    
    def test_update_profile_email(self, client):
        """Test updating email"""
        # Register
        reg_response = client.post('/api/v1/auth/register', json={
            "email": "oldemail@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        })
        token = reg_response.get_json()['token']
        
        # Update email
        response = client.put('/api/v1/auth/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={"email": "newemail@example.com"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == 'newemail@example.com'
        print(f"✅ Email updated to: {data['email']}")
    
    def test_update_profile_duplicate_email(self, client):
        """Test updating to an email that already exists"""
        # Register first user
        client.post('/api/v1/auth/register', json={
            "email": "existing@example.com",
            "password": "SecurePass123!",
            "name": "Existing User"
        })
        
        # Register second user
        reg_response = client.post('/api/v1/auth/register', json={
            "email": "second@example.com",
            "password": "SecurePass123!",
            "name": "Second User"
        })
        token = reg_response.get_json()['token']
        
        # Try to update to existing email
        response = client.put('/api/v1/auth/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={"email": "existing@example.com"}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'already in use' in data['error'].lower()
        print(f"✅ Duplicate email update blocked")
    
    def test_update_profile_no_data(self, client):
        """Test update with no data"""
        # Register
        reg_response = client.post('/api/v1/auth/register', json={
            "email": "nodata@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        })
        token = reg_response.get_json()['token']
        
        # Try to update with empty data
        response = client.put('/api/v1/auth/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        print(f"✅ Empty update rejected")
    
    def test_delete_profile(self, client):
        """Test DELETE /api/v1/auth/profile"""
        # Register
        reg_response = client.post('/api/v1/auth/register', json={
            "email": "delete.test@example.com",
            "password": "SecurePass123!",
            "name": "Delete Test"
        })
        token = reg_response.get_json()['token']
        
        # Delete
        response = client.delete('/api/v1/auth/profile',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'deleted' in data['message'].lower()
        print(f"✅ Profile deleted: {data['message']}")
    
    def test_delete_profile_then_login(self, client):
        """Test that deleted user cannot login"""
        # Register
        reg_response = client.post('/api/v1/auth/register', json={
            "email": "deleteme@example.com",
            "password": "SecurePass123!",
            "name": "Delete Me"
        })
        token = reg_response.get_json()['token']
        
        # Delete account
        client.delete('/api/v1/auth/profile',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Try to login
        response = client.post('/api/v1/auth/login', json={
            "email": "deleteme@example.com",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 401
        print(f"✅ Deleted user cannot login")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
