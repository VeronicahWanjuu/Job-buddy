"""
Test Block 5: Companies & Contacts Endpoints
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))


class TestBlock5Companies:
    """Test company endpoints"""
    
    def test_get_companies_empty(self, client, auth_headers):
        """Test GET /api/v1/companies with no data"""
        response = client.get('/api/v1/companies',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
        print(f"✅ Empty companies list returned")
    
    def test_create_company(self, client, auth_headers):
        """Test POST /api/v1/companies"""
        response = client.post('/api/v1/companies',
            headers=auth_headers,
            json={
                "name": "Test Company Inc",
                "website": "https://test.com",
                "location": "San Francisco, CA",
                "industry": "Technology"
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == "Test Company Inc"
        assert data['industry'] == "Technology"
        print(f"✅ Company created: {data['name']}")
    
    def test_create_company_duplicate_name(self, client, auth_headers):
        """Test duplicate company name prevention"""
        # Create first
        client.post('/api/v1/companies',
            headers=auth_headers,
            json={"name": "Duplicate Corp"}
        )
        
        # Try duplicate
        response = client.post('/api/v1/companies',
            headers=auth_headers,
            json={"name": "duplicate corp"}  # Case insensitive
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'already exists' in data['error']
        print(f"✅ Duplicate name blocked")
    
    def test_create_company_short_name(self, client, auth_headers):
        """Test name length validation"""
        response = client.post('/api/v1/companies',
            headers=auth_headers,
            json={"name": "A"}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert '2 characters' in data['error']
        print(f"✅ Short name rejected")
    
    def test_get_single_company(self, client, auth_headers):
        """Test GET /api/v1/companies/<id>"""
        # Create company
        create_response = client.post('/api/v1/companies',
            headers=auth_headers,
            json={"name": "Single Test Corp"}
        )
        company_id = create_response.get_json()['id']
        
        # Get it
        response = client.get(f'/api/v1/companies/{company_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'company' in data
        assert 'applications' in data
        assert 'contacts' in data
        print(f"✅ Company retrieved with relations")
    
    def test_update_company(self, client, auth_headers):
        """Test PUT /api/v1/companies/<id>"""
        # Create
        create_response = client.post('/api/v1/companies',
            headers=auth_headers,
            json={"name": "Update Test Corp"}
        )
        company_id = create_response.get_json()['id']
        
        # Update
        response = client.put(f'/api/v1/companies/{company_id}',
            headers=auth_headers,
            json={
                "location": "New York",
                "notes": "Updated notes"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['location'] == "New York"
        print(f"✅ Company updated")
    
    def test_filter_companies_by_industry(self, client, auth_headers):
        """Test industry filter"""
        # Create companies with different industries
        client.post('/api/v1/companies',
            headers=auth_headers,
            json={"name": "Tech Corp", "industry": "Technology"}
        )
        client.post('/api/v1/companies',
            headers=auth_headers,
            json={"name": "Finance Corp", "industry": "Finance"}
        )
        
        # Filter by Technology
        response = client.get('/api/v1/companies?industry=Technology',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['industry'] == "Technology"
        print(f"✅ Industry filter working")
    
    def test_delete_company(self, client, auth_headers):
        """Test DELETE /api/v1/companies/<id>"""
        # Create
        create_response = client.post('/api/v1/companies',
            headers=auth_headers,
            json={"name": "Delete Test Corp"}
        )
        company_id = create_response.get_json()['id']
        
        # Delete
        response = client.delete(f'/api/v1/companies/{company_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        print(f"✅ Company deleted")


class TestBlock5Contacts:
    """Test contact endpoints"""
    
    @pytest.fixture
    def company_id(self, client, auth_headers):
        """Create a company and return its ID"""
        response = client.post('/api/v1/companies',
            headers=auth_headers,
            json={"name": "Contact Test Corp"}
        )
        return response.get_json()['id']
    
    def test_get_contacts_empty(self, client, auth_headers, company_id):
        """Test GET /api/v1/contacts with no data"""
        response = client.get(f'/api/v1/contacts?company_id={company_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
        print(f"✅ Empty contacts list returned")
    
    def test_create_contact(self, client, auth_headers, company_id):
        """Test POST /api/v1/contacts"""
        response = client.post('/api/v1/contacts',
            headers=auth_headers,
            json={
                "company_id": company_id,
                "name": "John Recruiter",
                "role": "Senior Recruiter",
                "email": "john@test.com",
                "linkedin_url": "https://linkedin.com/in/john"
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == "John Recruiter"
        assert data['email'] == "john@test.com"
        print(f"✅ Contact created: {data['name']}")
    
    def test_create_contact_invalid_email(self, client, auth_headers, company_id):
        """Test email validation"""
        response = client.post('/api/v1/contacts',
            headers=auth_headers,
            json={
                "company_id": company_id,
                "name": "Test Contact",
                "email": "invalid-email"
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'email' in data['error'].lower()
        print(f"✅ Invalid email rejected")
    
    def test_create_contact_duplicate_email(self, client, auth_headers, company_id):
        """Test duplicate email prevention"""
        # Create first
        client.post('/api/v1/contacts',
            headers=auth_headers,
            json={
                "company_id": company_id,
                "name": "First Contact",
                "email": "duplicate@test.com"
            }
        )
        
        # Try duplicate
        response = client.post('/api/v1/contacts',
            headers=auth_headers,
            json={
                "company_id": company_id,
                "name": "Second Contact",
                "email": "duplicate@test.com"
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'already exists' in data['error']
        print(f"✅ Duplicate email blocked")
    
    def test_create_contact_without_email(self, client, auth_headers, company_id):
        """Test that contacts without email are allowed"""
        response = client.post('/api/v1/contacts',
            headers=auth_headers,
            json={
                "company_id": company_id,
                "name": "No Email Contact",
                "role": "Manager"
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['email'] is None
        print(f"✅ Contact without email created")
    
    def test_multiple_contacts_null_email(self, client, auth_headers, company_id):
        """Test that multiple NULL emails are allowed"""
        for i in range(3):
            response = client.post('/api/v1/contacts',
                headers=auth_headers,
                json={
                    "company_id": company_id,
                    "name": f"No Email {i+1}"
                }
            )
            assert response.status_code == 201
        print(f"✅ Multiple NULL emails allowed")
    
    def test_update_contact(self, client, auth_headers, company_id):
        """Test PUT /api/v1/contacts/<id>"""
        # Create
        create_response = client.post('/api/v1/contacts',
            headers=auth_headers,
            json={
                "company_id": company_id,
                "name": "Update Test",
                "role": "Recruiter"
            }
        )
        contact_id = create_response.get_json()['id']
        
        # Update
        response = client.put(f'/api/v1/contacts/{contact_id}',
            headers=auth_headers,
            json={
                "role": "Senior Recruiter",
                "notes": "Promoted!"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['role'] == "Senior Recruiter"
        print(f"✅ Contact updated")
    
    def test_delete_contact(self, client, auth_headers, company_id):
        """Test DELETE /api/v1/contacts/<id>"""
        # Create
        create_response = client.post('/api/v1/contacts',
            headers=auth_headers,
            json={
                "company_id": company_id,
                "name": "Delete Test"
            }
        )
        contact_id = create_response.get_json()['id']
        
        # Delete
        response = client.delete(f'/api/v1/contacts/{contact_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        print(f"✅ Contact deleted")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])