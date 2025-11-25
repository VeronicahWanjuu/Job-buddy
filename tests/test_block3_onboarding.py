"""
Test Block 3: Onboarding Endpoints
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))


class TestBlock3Onboarding:
    """Test all onboarding endpoints"""
    
    def test_create_onboarding_valid(self, client, auth_headers):
        """Test POST /api/v1/onboarding with valid data"""
        response = client.post('/api/v1/onboarding',
            headers=auth_headers,
            json={
                "current_feeling": "Excited and ready",
                "dream_milestone": "Become a Senior Developer at FAANG",
                "weekly_application_goal": 7,
                "weekly_outreach_goal": 5,
                "companies": [
                    {"name": "Google", "website": "https://google.com"},
                    {"name": "Meta", "website": "https://meta.com"}
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'onboarding' in data
        assert 'goal' in data
        assert 'companies_created' in data
        assert data['onboarding']['current_feeling'] == "Excited and ready"
        assert data['goal']['applications_goal'] == 7
        assert data['companies_created'] == 2
        print(f"✅ Onboarding created: {data['onboarding']['dream_milestone']}")
    
    def test_create_onboarding_invalid_feeling(self, client, auth_headers):
        """Test with invalid feeling"""
        response = client.post('/api/v1/onboarding',
            headers=auth_headers,
            json={
                "current_feeling": "Invalid Feeling",
                "dream_milestone": "My career goal here",
                "weekly_application_goal": 5,
                "weekly_outreach_goal": 3
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid feeling' in data['error']
        print(f"✅ Invalid feeling rejected")
    
    def test_create_onboarding_short_milestone(self, client, auth_headers):
        """Test with too short dream milestone"""
        response = client.post('/api/v1/onboarding',
            headers=auth_headers,
            json={
                "current_feeling": "Excited and ready",
                "dream_milestone": "Short",
                "weekly_application_goal": 5,
                "weekly_outreach_goal": 3
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert '10 characters' in data['error']
        print(f"✅ Short milestone rejected")
    
    def test_create_onboarding_invalid_goals(self, client, auth_headers):
        """Test with invalid goal values"""
        response = client.post('/api/v1/onboarding',
            headers=auth_headers,
            json={
                "current_feeling": "Excited and ready",
                "dream_milestone": "My career milestone here",
                "weekly_application_goal": 0,
                "weekly_outreach_goal": -1
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        print(f"✅ Invalid goals rejected")
    
    def test_get_onboarding_completed(self, client, auth_headers):
        """Test GET /api/v1/onboarding after completion"""
        # First create onboarding
        client.post('/api/v1/onboarding',
            headers=auth_headers,
            json={
                "current_feeling": "Overwhelmed but motivated",
                "dream_milestone": "Land my dream tech job",
                "weekly_application_goal": 5,
                "weekly_outreach_goal": 3
            }
        )
        
        # Then get it
        response = client.get('/api/v1/onboarding',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['completed'] is True
        assert 'current_feeling' in data
        assert 'dream_milestone' in data
        print(f"✅ Onboarding retrieved: Completed={data['completed']}")
    
    def test_get_onboarding_not_completed(self, client):
        """Test GET when onboarding not done"""
        # Register new user
        reg_response = client.post('/api/v1/auth/register', json={
            "email": "no.onboarding@example.com",
            "password": "SecurePass123!",
            "name": "No Onboarding User"
        })
        token = reg_response.get_json()['token']
        
        # Get onboarding
        response = client.get('/api/v1/onboarding',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['completed'] is False
        print(f"✅ Not completed status returned")
    
    def test_duplicate_onboarding_blocked(self, client, auth_headers):
        """Test that duplicate onboarding is prevented"""
        # Create first onboarding
        client.post('/api/v1/onboarding',
            headers=auth_headers,
            json={
                "current_feeling": "Excited and ready",
                "dream_milestone": "First milestone here",
                "weekly_application_goal": 5,
                "weekly_outreach_goal": 3
            }
        )
        
        # Try to create second
        response = client.post('/api/v1/onboarding',
            headers=auth_headers,
            json={
                "current_feeling": "Frustrated and stuck",
                "dream_milestone": "Second milestone here",
                "weekly_application_goal": 3,
                "weekly_outreach_goal": 2
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'already completed' in data['error']
        print(f"✅ Duplicate onboarding blocked")
    
    def test_onboarding_creates_goal(self, client, auth_headers):
        """Test that onboarding creates weekly goal"""
        response = client.post('/api/v1/onboarding',
            headers=auth_headers,
            json={
                "current_feeling": "Just getting started",
                "dream_milestone": "My career goal here",
                "weekly_application_goal": 10,
                "weekly_outreach_goal": 8,
                "companies": []
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Check goal created
        assert 'goal' in data
        assert data['goal']['applications_goal'] == 10
        assert data['goal']['outreach_goal'] == 8
        assert data['goal']['applications_current'] == 0
        assert data['goal']['outreach_current'] == 0
        print(f"✅ Goal created: {data['goal']['applications_goal']} apps, {data['goal']['outreach_goal']} outreach")
    
    def test_onboarding_creates_companies(self, client, auth_headers):
        """Test that onboarding creates companies"""
        response = client.post('/api/v1/onboarding',
            headers=auth_headers,
            json={
                "current_feeling": "Excited and ready",
                "dream_milestone": "Career milestone here",
                "weekly_application_goal": 5,
                "weekly_outreach_goal": 3,
                "companies": [
                    {"name": "Apple", "website": "https://apple.com"},
                    {"name": "Netflix", "website": "https://netflix.com"},
                    {"name": "Tesla", "website": "https://tesla.com"}
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['companies_created'] == 3
        print(f"✅ Companies created: {data['companies_created']}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])