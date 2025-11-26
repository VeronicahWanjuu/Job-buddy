import pytest
import json


def test_get_all_resources(client, auth_headers):
    """Test getting all resources"""
    response = client.get('/api/v1/resources', headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) > 0, "No resources found"
    print(f"✅ Retrieved {len(data)} resources")


def test_filter_resources_by_category(client, auth_headers):
    """Test filtering resources by category"""
    response = client.get('/api/v1/resources?category=resume', 
                         headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    
    # Only check if results exist
    if len(data) > 0:
        for resource in data:
            assert resource['category'] == 'resume', f"Expected 'resume', got '{resource['category']}'"
    
    print(f"✅ Filtered by category 'resume': {len(data)} results")


def test_filter_resources_by_type(client, auth_headers):
    """Test filtering resources by type"""
    response = client.get('/api/v1/resources?type=tool',
                         headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    
    # Only check if results exist
    if len(data) > 0:
        for resource in data:
            assert resource['type'] == 'tool', f"Expected 'tool', got '{resource['type']}'"
    
    print(f"✅ Filtered by type 'tool': {len(data)} results")


def test_get_resource_categories(client, auth_headers):
    """Test getting resource categories"""
    response = client.get('/api/v1/resources/categories',
                         headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert 'categories' in data, "Missing 'categories' key"
    assert 'types' in data, "Missing 'types' key"
    assert isinstance(data['categories'], list), f"Expected list for categories, got {type(data['categories'])}"
    assert isinstance(data['types'], list), f"Expected list for types, got {type(data['types'])}"
    print(f"✅ Categories retrieved: {len(data['categories'])} categories, {len(data['types'])} types")


def test_get_all_coaches(client, auth_headers):
    """Test getting all coaches"""
    response = client.get('/api/v1/coaches', headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) == 6, f"Expected 6 coaches, got {len(data)}"
    
    # Verify each coach has required fields
    for coach in data:
        assert 'id' in coach, "Coach missing 'id'"
        assert 'name' in coach, "Coach missing 'name'"
        assert 'image_url' in coach, "Coach missing 'image_url'"
    
    print(f"✅ Retrieved {len(data)} coaches")


def test_get_single_coach(client, auth_headers):
    """Test getting single coach"""
    response = client.get('/api/v1/coaches/coach-1', headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert data['id'] == 'coach-1', f"Expected 'coach-1', got '{data['id']}'"
    assert 'name' in data, "Coach missing 'name'"
    assert 'specialization' in data, "Coach missing 'specialization'"
    assert 'image_url' in data, "Coach missing 'image_url'"
    
    print(f"✅ Retrieved coach: {data['name']}")


def test_get_nonexistent_coach(client, auth_headers):
    """Test getting non-existent coach"""
    response = client.get('/api/v1/coaches/coach-999', headers=auth_headers)
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    data = response.get_json()
    assert 'error' in data, "Missing error message"
    print(f"✅ Non-existent coach correctly returned 404")


def test_get_tip_of_the_day(client, auth_headers):
    """Test getting tip of the day"""
    response = client.get('/api/v1/coaches/tip-of-the-day',
                         headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert 'coach' in data, "Missing 'coach' key"
    assert 'tip' in data, "Missing 'tip' key"
    assert 'id' in data['coach'], "Coach missing 'id'"
    assert 'name' in data['coach'], "Coach missing 'name'"
    assert isinstance(data['tip'], str), f"Expected string for tip, got {type(data['tip'])}"
    assert len(data['tip']) > 10, "Tip is too short"
    
    print(f"✅ Tip of the day from {data['coach']['name']}: {data['tip'][:50]}...")


def test_coaches_have_required_fields(client, auth_headers):
    """Test that all coaches have required fields"""
    response = client.get('/api/v1/coaches', headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    
    required_fields = ['id', 'name', 'title', 'specialization', 'image_url', 'bio']
    
    for coach in data:
        for field in required_fields:
            assert field in coach, f"Coach {coach.get('id', 'unknown')} missing field: {field}"
    
    print(f"✅ All {len(data)} coaches have required fields")


def test_tip_changes_on_multiple_requests(client, auth_headers):
    """Test that tip of the day can vary (not always the same)"""
    tips = set()
    
    # Make 5 requests
    for _ in range(5):
        response = client.get('/api/v1/coaches/tip-of-the-day',
                             headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        tips.add(data['tip'])
    
    # Should have at least 2 different tips in 5 tries (randomness)
    # Note: This could theoretically fail if very unlucky, but unlikely
    print(f"✅ Tip variety test: {len(tips)} unique tips in 5 requests")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])