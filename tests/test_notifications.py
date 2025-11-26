import pytest
import json
from backend.services.notification_service import create_notification


def test_get_notifications(client, auth_headers):
    """Test getting all notifications"""
    response = client.get('/api/v1/notifications', headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert 'notifications' in data, "Missing 'notifications' key"
    assert 'unread_count' in data, "Missing 'unread_count' key"
    assert isinstance(data['notifications'], list), f"Expected list, got {type(data['notifications'])}"
    assert isinstance(data['unread_count'], int), f"Expected int, got {type(data['unread_count'])}"
    print(f"✅ Retrieved {len(data['notifications'])} notifications, {data['unread_count']} unread")


def test_get_unread_notifications(client, auth_headers):
    """Test getting only unread notifications"""
    response = client.get('/api/v1/notifications?unread=true',
                         headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert 'notifications' in data, "Missing 'notifications' key"
    
    # Check all notifications are unread
    for notif in data['notifications']:
        assert notif['is_read'] == 0 or notif['is_read'] == False, f"Found read notification: {notif['id']}"
    
    print(f"✅ Retrieved {len(data['notifications'])} unread notifications")


def test_get_unread_count(client, auth_headers):
    """Test getting unread count"""
    response = client.get('/api/v1/notifications/unread-count',
                         headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert 'unread_count' in data, "Missing 'unread_count' key"
    assert isinstance(data['unread_count'], int), f"Expected int, got {type(data['unread_count'])}"
    assert data['unread_count'] >= 0, "Unread count should be non-negative"
    print(f"✅ Unread count: {data['unread_count']}")


def test_mark_notification_read(client, auth_headers, app):
    """Test marking notification as read"""
    # Create a test notification first
    with app.app_context():
        from backend.database.db import db
        
        # Get user_id from token
        user_response = client.get('/api/v1/notifications', headers=auth_headers)
        assert user_response.status_code == 200
        
        # Create a notification using the service
        create_notification(
            user_id=1,  # This will be the test user from auth_headers
            notif_type='system',
            title='Test Notification',
            message='This is a test notification for marking as read'
        )
    
    # Get the notification
    response = client.get('/api/v1/notifications', headers=auth_headers)
    data = response.get_json()
    
    if len(data['notifications']) > 0:
        notif_id = data['notifications'][0]['id']
        
        # Mark as read
        response = client.put(f'/api/v1/notifications/{notif_id}/read',
                             headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.get_json()}"
        result = response.get_json()
        assert 'notification' in result, "Missing 'notification' key"
        assert result['notification']['is_read'] == 1 or result['notification']['is_read'] == True, "Notification not marked as read"
        print(f"✅ Notification {notif_id} marked as read")
    else:
        print("⚠️  No notifications to test (skipped)")


def test_mark_all_read(client, auth_headers, app):
    """Test marking all notifications as read - FIXED"""
    # Create some test notifications
    with app.app_context():
        create_notification(1, 'system', 'Test 1', 'This is test message one here')
        create_notification(1, 'system', 'Test 2', 'This is test message two here')
        create_notification(1, 'system', 'Test 3', 'This is test message three here')
    
    response = client.put('/api/v1/notifications/read-all',
                         headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert 'count' in data, "Missing 'count' key"
    assert isinstance(data['count'], int), f"Expected int, got {type(data['count'])}"
    print(f"✅ Marked {data['count']} notifications as read")
    
    # Verify all are read
    verify_response = client.get('/api/v1/notifications/unread-count',
                                 headers=auth_headers)
    verify_data = verify_response.get_json()
    assert verify_data['unread_count'] == 0, "Still have unread notifications after marking all as read"


def test_delete_notification(client, auth_headers, app):
    """Test deleting a notification"""
    # Create a test notification
    with app.app_context():
        create_notification(1, 'system', 'To Delete', 'This notification will be deleted soon')
    
    # Get the notification
    response = client.get('/api/v1/notifications', headers=auth_headers)
    data = response.get_json()
    
    if len(data['notifications']) > 0:
        notif_id = data['notifications'][0]['id']
        initial_count = len(data['notifications'])
        
        # Delete it
        response = client.delete(f'/api/v1/notifications/{notif_id}',
                                headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.get_json()}"
        result = response.get_json()
        assert 'message' in result, "Missing success message"
        print(f"✅ Notification {notif_id} deleted")
        
        # Verify it's gone
        verify_response = client.get('/api/v1/notifications', headers=auth_headers)
        verify_data = verify_response.get_json()
        assert len(verify_data['notifications']) == initial_count - 1, "Notification not deleted"
    else:
        print("⚠️  No notifications to delete (skipped)")


def test_clear_all_notifications(client, auth_headers, app):
    """Test clearing all notifications - FIXED"""
    # Create some test notifications
    with app.app_context():
        create_notification(1, 'system', 'Clear Test 1', 'Clear test message one here')
        create_notification(1, 'system', 'Clear Test 2', 'Clear test message two here')
        create_notification(1, 'goal_reminder', 'Clear Test 3', 'Clear test message three')
    
    response = client.delete('/api/v1/notifications/clear-all',
                            headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    data = response.get_json()
    assert 'count' in data, "Missing 'count' key"
    assert isinstance(data['count'], int), f"Expected int, got {type(data['count'])}"
    print(f"✅ Cleared {data['count']} notifications")
    
    # Verify all are cleared
    verify_response = client.get('/api/v1/notifications', headers=auth_headers)
    verify_data = verify_response.get_json()
    assert len(verify_data['notifications']) == 0, "Notifications not cleared"


def test_delete_nonexistent_notification(client, auth_headers):
    """Test deleting non-existent notification"""
    response = client.delete('/api/v1/notifications/9999',
                            headers=auth_headers)
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    data = response.get_json()
    assert 'error' in data, "Missing error message"
    print(f"✅ Non-existent notification correctly returned 404")


def test_mark_nonexistent_notification_read(client, auth_headers):
    """Test marking non-existent notification as read"""
    response = client.put('/api/v1/notifications/9999/read',
                         headers=auth_headers)
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    data = response.get_json()
    assert 'error' in data, "Missing error message"
    print(f"✅ Non-existent notification mark as read correctly returned 404")


def test_notification_filtering_works(client, auth_headers, app):
    """Test that unread filter actually filters - FIXED"""
    # Clear all first
    client.delete('/api/v1/notifications/clear-all', headers=auth_headers)
    
    # Create some notifications
    with app.app_context():
        create_notification(1, 'system', 'Unread 1', 'Unread message one here now')
        create_notification(1, 'system', 'Unread 2', 'Unread message two here now')
    
    # Get all
    all_response = client.get('/api/v1/notifications', headers=auth_headers)
    all_data = all_response.get_json()
    total_count = len(all_data['notifications'])
    
    # Mark one as read
    if total_count > 0:
        notif_id = all_data['notifications'][0]['id']
        client.put(f'/api/v1/notifications/{notif_id}/read', headers=auth_headers)
    
    # Get unread only
    unread_response = client.get('/api/v1/notifications?unread=true',
                                 headers=auth_headers)
    unread_data = unread_response.get_json()
    
    assert len(unread_data['notifications']) == total_count - 1, "Unread filter not working correctly"
    print(f"✅ Unread filtering works: {len(unread_data['notifications'])} unread out of {total_count} total")


def test_notification_created_at_sorted(client, auth_headers, app):
    """Test that notifications are sorted by created_at DESC - FIXED"""
    # Clear all first
    client.delete('/api/v1/notifications/clear-all', headers=auth_headers)
    
    # Create notifications in sequence
    with app.app_context():
        create_notification(1, 'system', 'First', 'First notification message here')
        create_notification(1, 'system', 'Second', 'Second notification message now')
        create_notification(1, 'system', 'Third', 'Third notification message too')
    
    response = client.get('/api/v1/notifications', headers=auth_headers)
    data = response.get_json()
    
    if len(data['notifications']) >= 2:
        # Check that first notification was created after or at same time as second
        first_created = data['notifications'][0]['created_at']
        second_created = data['notifications'][1]['created_at']
        
        # Should be DESC order (newest first)
        assert first_created >= second_created, "Notifications not sorted by created_at DESC"
        print(f"✅ Notifications correctly sorted (newest first)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])