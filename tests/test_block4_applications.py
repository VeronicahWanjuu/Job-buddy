"""
Test Block 4: Applications CRUD Endpoints
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))


class TestBlock4Applications:
    """Test all application endpoints"""
    
    @pytest.fixture
    def auth_with_company(self, client, auth_headers):
        """Complete onboarding and return headers with company_id"""
        # Complete onboarding (creates companies)
        client.post('/api/v1/onboarding',
            headers=auth_headers,
            json={
                "current_feeling": "Excited and ready",
                "dream_milestone": "Land a FAANG position",
                "weekly_application_goal": 5,
                "weekly_outreach_goal": 3,
                "companies": [
                    {"name": "TestCorp", "website": "https://test.com"}
                ]
            }
        )
        
        # Get company_id
        companies_response = client.get('/api/v1/companies',
            headers=auth_headers
        )
        
        # FIX: Handle both response formats
        companies_data = companies_response.get_json()
        
        # Debug: print response to see structure
        print(f"Companies response: {companies_data}")
        
        # Try different response structures
        if isinstance(companies_data, list):
            # Response is directly a list
            company_id = companies_data[0]['id']
        elif isinstance(companies_data, dict):
            # Response is a dict with 'companies' key
            if 'companies' in companies_data:
                company_id = companies_data['companies'][0]['id']
            else:
                # Single company returned as dict
                company_id = companies_data['id']
        else:
            raise ValueError(f"Unexpected response format: {companies_data}")
        
        return {'headers': auth_headers, 'company_id': company_id}
    
    def test_get_applications_empty(self, client, auth_with_company):
        """Test GET /api/v1/applications with no data"""
        response = client.get('/api/v1/applications',
            headers=auth_with_company['headers']
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'applications' in data
        assert 'grouped_by_status' in data
        assert len(data['applications']) == 0
        print(f"✅ Empty applications list returned")
    
    def test_create_application_planned(self, client, auth_with_company):
        """Test POST /api/v1/applications with Planned status"""
        response = client.post('/api/v1/applications',
            headers=auth_with_company['headers'],
            json={
                "company_id": auth_with_company['company_id'],
                "job_title": "Software Engineer",
                "job_url": "https://test.com/jobs/123",
                "status": "Planned",
                "notes": "Great opportunity"
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['job_title'] == "Software Engineer"
        assert data['status'] == "Planned"
        assert data['applied_date'] is None
        print(f"✅ Application created: {data['job_title']}")
    
    def test_create_application_applied(self, client, auth_with_company):
        """Test POST with Applied status (triggers side effects)"""
        response = client.post('/api/v1/applications',
            headers=auth_with_company['headers'],
            json={
                "company_id": auth_with_company['company_id'],
                "job_title": "Backend Developer",
                "status": "Applied"
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == "Applied"
        assert data['applied_date'] is not None
        print(f"✅ Applied application: applied_date={data['applied_date']}")
    
    def test_create_application_invalid_status(self, client, auth_with_company):
        """Test with invalid status"""
        response = client.post('/api/v1/applications',
            headers=auth_with_company['headers'],
            json={
                "company_id": auth_with_company['company_id'],
                "job_title": "Test Job",
                "status": "InvalidStatus"
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        print(f"✅ Invalid status rejected")
    
    def test_create_application_invalid_company(self, client, auth_with_company):
        """Test with non-existent company"""
        response = client.post('/api/v1/applications',
            headers=auth_with_company['headers'],
            json={
                "company_id": 99999,
                "job_title": "Test Job",
                "status": "Planned"
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Company not found' in data['error']
        print(f"✅ Invalid company rejected")
    
    def test_get_single_application(self, client, auth_with_company):
        """Test GET /api/v1/applications/<id>"""
        # Create application
        create_response = client.post('/api/v1/applications',
            headers=auth_with_company['headers'],
            json={
                "company_id": auth_with_company['company_id'],
                "job_title": "Frontend Developer",
                "status": "Planned"
            }
        )
        app_id = create_response.get_json()['id']
        
        # Get it
        response = client.get(f'/api/v1/applications/{app_id}',
            headers=auth_with_company['headers']
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'application' in data
        assert 'outreach' in data
        assert 'cv_analyses' in data
        assert data['application']['job_title'] == "Frontend Developer"
        print(f"✅ Application retrieved: {data['application']['job_title']}")
    
    def test_update_application_status(self, client, auth_with_company):
        """Test PUT /api/v1/applications/<id>"""
        # Create
        create_response = client.post('/api/v1/applications',
            headers=auth_with_company['headers'],
            json={
                "company_id": auth_with_company['company_id'],
                "job_title": "Data Scientist",
                "status": "Planned"
            }
        )
        app_id = create_response.get_json()['id']
        
        # Update to Applied
        response = client.put(f'/api/v1/applications/{app_id}',
            headers=auth_with_company['headers'],
            json={
                "status": "Applied",
                "notes": "Applied via company website"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == "Applied"
        assert data['applied_date'] is not None
        print(f"✅ Application updated: Status={data['status']}")
    
    def test_update_to_rejected_creates_notification(self, client, auth_with_company):
        """Test that rejection creates motivation notification"""
        # Create and apply
        create_response = client.post('/api/v1/applications',
            headers=auth_with_company['headers'],
            json={
                "company_id": auth_with_company['company_id'],
                "job_title": "DevOps Engineer",
                "status": "Applied"
            }
        )
        app_id = create_response.get_json()['id']
        
        # Update to Rejected
        response = client.put(f'/api/v1/applications/{app_id}',
            headers=auth_with_company['headers'],
            json={"status": "Rejected"}
        )
        
        assert response.status_code == 200
        
        # Check notifications
        notif_response = client.get('/api/v1/notifications',
            headers=auth_with_company['headers']
        )
        notifs = notif_response.get_json()['notifications']
        assert any(n['type'] == 'motivation' for n in notifs)
        print(f"✅ Rejection notification created")
    
    def test_delete_application(self, client, auth_with_company):
        """Test DELETE /api/v1/applications/<id>"""
        # Create application
        create_response = client.post('/api/v1/applications',
            headers=auth_with_company['headers'],
            json={
                "company_id": auth_with_company['company_id'],
                "job_title": "Mobile Developer",
                "status": "Planned"
            }
        )
        app_id = create_response.get_json()['id']
        
        # Delete it
        response = client.delete(f'/api/v1/applications/{app_id}',
            headers=auth_with_company['headers']
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        
        # Verify deleted
        get_response = client.get(f'/api/v1/applications/{app_id}',
            headers=auth_with_company['headers']
        )
        assert get_response.status_code == 404
        print(f"✅ Application deleted successfully")
    
    def test_get_applications_with_data(self, client, auth_with_company):
        """Test GET /api/v1/applications returns grouped data"""
        # Create multiple applications
        statuses = ['Planned', 'Applied', 'Interview', 'Offer', 'Rejected']
        for status in statuses:
            client.post('/api/v1/applications',
                headers=auth_with_company['headers'],
                json={
                    "company_id": auth_with_company['company_id'],
                    "job_title": f"{status} Position",
                    "status": status
                }
            )
        
        response = client.get('/api/v1/applications',
            headers=auth_with_company['headers']
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['applications']) == 5
        
        # Check grouping
        for status in statuses:
            assert status in data['grouped_by_status']
            assert len(data['grouped_by_status'][status]) == 1
        
        print(f"✅ Applications grouped by status correctly")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])