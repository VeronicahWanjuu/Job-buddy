import pytest
import json
from datetime import date, timedelta


def test_get_current_goal(client, auth_headers):
    """Test getting current week's goal"""
    response = client.get('/api/v1/goals/current', headers=auth_headers)
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert 'goal' in data
    assert 'applications_percentage' in data
    assert 'days_remaining' in data
    print(f"✅ Current goal retrieved")


def test_update_goals_success(client, auth_headers):
    """Test updating weekly goals"""
    payload = {
        "applications_goal": 10,
        "outreach_goal": 7
    }
    response = client.post('/api/v1/goals/update', 
                          headers=auth_headers,
                          json=payload)  # Use json= instead of data=
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert data['applications_goal'] == 10
    assert data['outreach_goal'] == 7
    print(f"✅ Goals updated successfully")


def test_update_goals_twice_fails(client, auth_headers):
    """Test updating goals twice in same week fails"""
    payload = {"applications_goal": 10, "outreach_goal": 7}
    
    # First update
    response1 = client.post('/api/v1/goals/update', 
                           headers=auth_headers,
                           json=payload)
    assert response1.status_code == 200, f"First update failed: {response1.get_json()}"
    
    # Second update (should fail)
    response2 = client.post('/api/v1/goals/update', 
                           headers=auth_headers,
                           json=payload)
    assert response2.status_code == 400, f"Expected 400, got {response2.status_code}"
    data = response2.get_json()
    assert 'error' in data or 'message' in data
    print(f"✅ Second update correctly rejected")


def test_update_goals_negative_fails(client, auth_headers):
    """Test negative goals are rejected"""
    payload = {"applications_goal": -5, "outreach_goal": 3}
    response = client.post('/api/v1/goals/update',
                          headers=auth_headers,
                          json=payload)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    data = response.get_json()
    assert 'error' in data or 'message' in data
    print(f"✅ Negative goals rejected")


def test_get_streak(client, auth_headers):
    """Test getting streak information"""
    response = client.get('/api/v1/goals/streak', headers=auth_headers)
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert 'current_streak' in data
    assert 'longest_streak' in data
    assert 'total_points' in data
    assert 'level' in data
    print(f"✅ Streak retrieved: {data['current_streak']} days, Level {data['level']}")


def test_get_micro_quests(client, auth_headers):
    """Test getting available micro-quests"""
    response = client.get('/api/v1/goals/micro-quests', headers=auth_headers)
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) <= 3, f"Expected max 3 quests, got {len(data)}"
    print(f"✅ Micro-quests retrieved: {len(data)} available")


def test_complete_micro_quest(client, auth_headers):
    """Test completing a micro-quest"""
    # First get available quests to find a valid quest_id
    quests_response = client.get('/api/v1/goals/micro-quests', headers=auth_headers)
    quests = quests_response.get_json()
    
    if not quests:
        pytest.skip("No micro-quests available to test")
    
    quest_id = quests[0]['id']
    
    response = client.post(f'/api/v1/goals/micro-quests/{quest_id}/complete',
                          headers=auth_headers)
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert 'points_earned' in data
    assert 'new_total_points' in data
    assert data['points_earned'] > 0
    print(f"✅ Quest completed: earned {data['points_earned']} points")


def test_complete_same_quest_twice_fails(client, auth_headers):
    """Test completing same quest twice fails"""
    # Get available quests
    quests_response = client.get('/api/v1/goals/micro-quests', headers=auth_headers)
    quests = quests_response.get_json()
    
    if not quests:
        pytest.skip("No micro-quests available to test")
    
    quest_id = quests[0]['id']
    
    # First completion
    response1 = client.post(f'/api/v1/goals/micro-quests/{quest_id}/complete',
                           headers=auth_headers)
    assert response1.status_code == 200, f"First completion failed: {response1.get_json()}"
    
    # Second completion (should fail)
    response2 = client.post(f'/api/v1/goals/micro-quests/{quest_id}/complete',
                           headers=auth_headers)
    assert response2.status_code == 400, f"Expected 400, got {response2.status_code}"
    data = response2.get_json()
    assert 'error' in data or 'already' in str(data).lower()
    print(f"✅ Duplicate quest completion rejected")


def test_complete_nonexistent_quest(client, auth_headers):
    """Test completing non-existent quest fails"""
    response = client.post('/api/v1/goals/micro-quests/mq-999/complete',
                          headers=auth_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.get_json()}"
    data = response.get_json()
    assert 'error' in data or 'not found' in str(data).lower()
    print(f"✅ Non-existent quest correctly rejected")


def test_goal_initialization_on_registration(client):
    """Test that goal is automatically created on user registration"""
    # Register new user
    response = client.post('/api/v1/auth/register', json={
        "email": "goal.test@example.com",
        "password": "SecurePass123!",
        "name": "Goal Test User"
    })
    assert response.status_code == 201
    token = response.get_json()['token']
    
    # Check that goal exists
    goal_response = client.get('/api/v1/goals/current',
                               headers={'Authorization': f'Bearer {token}'})
    assert goal_response.status_code == 200
    data = goal_response.get_json()
    assert 'goal' in data
    print(f"✅ Goal auto-created on registration")


def test_streak_initialization(client):
    """Test that streak is automatically created"""
    # Register new user
    response = client.post('/api/v1/auth/register', json={
        "email": "streak.test@example.com",
        "password": "SecurePass123!",
        "name": "Streak Test User"
    })
    assert response.status_code == 201
    token = response.get_json()['token']
    
    # Check that streak exists
    streak_response = client.get('/api/v1/goals/streak',
                                 headers={'Authorization': f'Bearer {token}'})
    assert streak_response.status_code == 200
    data = streak_response.get_json()
    assert data['current_streak'] == 0
    assert data['longest_streak'] == 0
    assert data['total_points'] == 0
    assert data['level'] >= 1
    print(f"✅ Streak auto-created on registration")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])