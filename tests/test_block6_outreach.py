"""Test Block 6: Outreach Endpoints"""
import pytest
from datetime import date, timedelta


@pytest.fixture
def auth_setup(client):
    """Register, login, create company, contact, application"""
    # Register & login
    response = client.post('/api/v1/auth/register', json={
        "email": "outreach.test@example.com",
        "password": "SecurePass123!",
        "name": "Outreach Test User"
    })
    assert response.status_code == 201, f"Registration failed: {response.get_json()}"
    token = response.get_json()['token']
    
    # Onboarding (for dream_milestone)
    onboard_response = client.post('/api/v1/onboarding',
        headers={'Authorization': f'Bearer {token}'},
        json={
            "current_feeling": "Excited and ready",
            "dream_milestone": "Become a senior developer at FAANG",
            "weekly_application_goal": 5,
            "weekly_outreach_goal": 3
        }
    )
    assert onboard_response.status_code in [200, 201], f"Onboarding failed: {onboard_response.get_json()}"
    
    # Create company
    company_response = client.post('/api/v1/companies',
        headers={'Authorization': f'Bearer {token}'},
        json={"name": "Outreach Test Corp"}
    )
    assert company_response.status_code == 201, f"Company creation failed: {company_response.get_json()}"
    company_id = company_response.get_json()['id']
    
    # Create contact
    contact_response = client.post('/api/v1/contacts',
        headers={'Authorization': f'Bearer {token}'},
        json={
            "company_id": company_id,
            "name": "Jane Recruiter",
            "email": "jane@outreach.com"
        }
    )
    assert contact_response.status_code == 201, f"Contact creation failed: {contact_response.get_json()}"
    contact_id = contact_response.get_json()['id']
    
    # Create application
    app_response = client.post('/api/v1/applications',
        headers={'Authorization': f'Bearer {token}'},
        json={
            "company_id": company_id,
            "job_title": "Backend Engineer",
            "status": "Applied"
        }
    )
    assert app_response.status_code == 201, f"Application creation failed: {app_response.get_json()}"
    application_id = app_response.get_json()['id']
    
    return {
        'token': token,
        'company_id': company_id,
        'contact_id': contact_id,
        'application_id': application_id
    }


class TestBlock6Outreach:
    """Test outreach endpoints"""
    
    def test_generate_cold_outreach_template(self, client, auth_setup):
        """Test POST /api/v1/outreach/templates/generate (cold_outreach)"""
        response = client.post('/api/v1/outreach/templates/generate',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "contact_id": auth_setup['contact_id'],
                "company_id": auth_setup['company_id'],
                "template_type": "cold_outreach"
            }
        )
        assert response.status_code == 200, f"Failed: {response.get_json()}"
        data = response.get_json()
        assert 'subject' in data
        assert 'body' in data
        assert 'editing_tips' in data
        assert 'Jane Recruiter' in data['body'] or 'Jane' in data['body']  # Personalized
        assert 'Outreach Test Corp' in data['body']  # Personalized
        print(f"✅ Cold outreach template generated")
    
    def test_generate_follow_up_template(self, client, auth_setup):
        """Test POST /api/v1/outreach/templates/generate (follow_up)"""
        response = client.post('/api/v1/outreach/templates/generate',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "contact_id": auth_setup['contact_id'],
                "company_id": auth_setup['company_id'],
                "application_id": auth_setup['application_id'],
                "template_type": "follow_up_application"
            }
        )
        assert response.status_code == 200, f"Failed: {response.get_json()}"
        data = response.get_json()
        assert 'Backend Engineer' in data['body']  # Job title included
        print(f"✅ Follow-up template generated")
    
    def test_create_outreach_with_application(self, client, auth_setup):
        """Test POST /api/v1/outreach (linked to application)"""
        today = date.today().isoformat()
        follow_up = (date.today() + timedelta(days=7)).isoformat()
        
        response = client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "application_id": auth_setup['application_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "email",
                "message": "Hi Jane, I recently applied for the Backend Engineer position.",
                "sent_date": today,
                "follow_up_date": follow_up
            }
        )
        assert response.status_code == 201, f"Failed: {response.get_json()}"
        data = response.get_json()
        assert data['application_id'] == auth_setup['application_id']
        assert data['company_id'] is None
        assert data['channel'] == 'email'
        assert data['status'] == 'Sent'
        print(f"✅ Outreach created (linked to application)")
    
    def test_create_outreach_with_company(self, client, auth_setup):
        """Test POST /api/v1/outreach (linked to company only)"""
        today = date.today().isoformat()
        
        response = client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "company_id": auth_setup['company_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "linkedin",
                "message": "Hi Jane, I'm interested in opportunities at your company.",
                "sent_date": today
            }
        )
        assert response.status_code == 201, f"Failed: {response.get_json()}"
        data = response.get_json()
        assert data['company_id'] == auth_setup['company_id']
        assert data['application_id'] is None
        assert data['channel'] == 'linkedin'
        print(f"✅ Outreach created (linked to company)")
    
    def test_create_outreach_both_ids_fails(self, client, auth_setup):
        """Test XOR constraint: both IDs should fail"""
        today = date.today().isoformat()
        
        response = client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "application_id": auth_setup['application_id'],
                "company_id": auth_setup['company_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "email",
                "message": "Test message",
                "sent_date": today
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'exactly ONE' in data['error'] or 'one of' in data['error'].lower()
        print(f"✅ Both IDs rejected (XOR enforced)")
    
    def test_create_outreach_neither_id_fails(self, client, auth_setup):
        """Test XOR constraint: neither ID should fail"""
        today = date.today().isoformat()
        
        response = client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "contact_id": auth_setup['contact_id'],
                "channel": "email",
                "message": "Test message",
                "sent_date": today
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'exactly ONE' in data['error'] or 'required' in data['error'].lower()
        print(f"✅ Neither ID rejected (XOR enforced)")
    
    def test_create_outreach_invalid_channel(self, client, auth_setup):
        """Test channel validation"""
        today = date.today().isoformat()
        
        response = client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "application_id": auth_setup['application_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "twitter",
                "message": "Test message",
                "sent_date": today
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid channel' in data['error'] or 'channel' in data['error'].lower()
        print(f"✅ Invalid channel rejected")
    
    def test_create_outreach_short_message(self, client, auth_setup):
        """Test message length validation"""
        today = date.today().isoformat()
        
        response = client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "application_id": auth_setup['application_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "email",
                "message": "Hi",
                "sent_date": today
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'at least 10 characters' in data['error'] or 'message' in data['error'].lower()
        print(f"✅ Short message rejected")
    
    def test_create_outreach_invalid_date_format(self, client, auth_setup):
        """Test date format validation"""
        response = client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "application_id": auth_setup['application_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "email",
                "message": "Test message here",
                "sent_date": "01/20/2025"  # Wrong format
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'YYYY-MM-DD' in data['error'] or 'date' in data['error'].lower()
        print(f"✅ Invalid date format rejected")
    
    def test_get_all_outreach(self, client, auth_setup):
        """Test GET /api/v1/outreach"""
        # Create some outreach first
        today = date.today().isoformat()
        client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "application_id": auth_setup['application_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "email",
                "message": "First outreach message",
                "sent_date": today
            }
        )
        
        response = client.get('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"✅ Outreach list retrieved: {len(data)} item(s)")
    
    def test_get_outreach_by_application(self, client, auth_setup):
        """Test GET /api/v1/outreach?application_id=X"""
        today = date.today().isoformat()
        client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "application_id": auth_setup['application_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "email",
                "message": "Application-specific outreach message",
                "sent_date": today
            }
        )
        
        response = client.get(
            f'/api/v1/outreach?application_id={auth_setup["application_id"]}',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        assert all(o['application_id'] == auth_setup['application_id'] for o in data)
        print(f"✅ Application-filtered outreach retrieved")
    
    def test_get_outreach_by_company(self, client, auth_setup):
        """Test GET /api/v1/outreach?company_id=X"""
        today = date.today().isoformat()
        client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "company_id": auth_setup['company_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "linkedin",
                "message": "Company-specific outreach message",
                "sent_date": today
            }
        )
        
        response = client.get(
            f'/api/v1/outreach?company_id={auth_setup["company_id"]}',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        print(f"✅ Company-filtered outreach retrieved")
    
    def test_update_outreach_status(self, client, auth_setup):
        """Test PUT /api/v1/outreach/<id>"""
        # Create outreach
        today = date.today().isoformat()
        create_response = client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "application_id": auth_setup['application_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "email",
                "message": "Test outreach for status update",
                "sent_date": today
            }
        )
        outreach_id = create_response.get_json()['id']
        
        # Update status
        response = client.put(f'/api/v1/outreach/{outreach_id}',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={"status": "Responded"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'Responded'
        print(f"✅ Outreach status updated to Responded")
    
    def test_goal_updated_after_outreach(self, client, auth_setup):
        """Test that goal.outreach_current increments"""
        # Get current goal
        goal_response_before = client.get('/api/v1/goals/current',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'}
        )
        assert goal_response_before.status_code == 200
        outreach_before = goal_response_before.get_json()['goal']['outreach_current']
        
        # Create outreach
        today = date.today().isoformat()
        client.post('/api/v1/outreach',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'},
            json={
                "application_id": auth_setup['application_id'],
                "contact_id": auth_setup['contact_id'],
                "channel": "email",
                "message": "Test outreach for goal increment",
                "sent_date": today
            }
        )
        
        # Check goal again
        goal_response_after = client.get('/api/v1/goals/current',
            headers={'Authorization': f'Bearer {auth_setup["token"]}'}
        )
        outreach_after = goal_response_after.get_json()['goal']['outreach_current']
        
        assert outreach_after == outreach_before + 1
        print(f"✅ Goal incremented: {outreach_before} → {outreach_after}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])