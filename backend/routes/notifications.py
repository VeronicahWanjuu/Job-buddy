from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.utils.decorators import require_auth
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

VALID_NOTIFICATION_TYPES = ['follow_up', 'goal_reminder', 'micro_quest', 'motivation', 'system']

@notifications_bp.route('', methods=['GET'])
@require_auth
def get_notifications():
    """
    GET /api/v1/notifications
    
    Get all notifications for user (protected)
    
    Query params:
        - unread: Filter unread only (true/false)
    
    Returns:
        {
            "notifications": [...],
            "unread_count": 5
        }
    """
    try:
        unread_only = request.args.get('unread', '').lower() == 'true'
        
        # Build query
        if unread_only:
            notifications = db.query(
                """
                SELECT *
                FROM notifications
                WHERE user_id = ? AND is_read = 0
                ORDER BY datetime(created_at) DESC
                """,
                (request.user_id,)
            )
        else:
            notifications = db.query(
                """
                SELECT *
                FROM notifications
                WHERE user_id = ?
                ORDER BY datetime(created_at) DESC
                """,
                (request.user_id,)
            )
        
        # Get unread count
        unread_count_row = db.query_one(
            "SELECT COUNT(*) AS cnt FROM notifications WHERE user_id = ? AND is_read = 0",
            (request.user_id,)
        )
        unread_count = unread_count_row['cnt'] if unread_count_row else 0
        
        return jsonify({
            "notifications": notifications,
            "unread_count": unread_count
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route('/unread-count', methods=['GET'])
@require_auth
def get_unread_count():
    """
    GET /api/v1/notifications/unread-count
    
    Get count of unread notifications (protected)
    
    This endpoint is polled by frontend every 60 seconds
    
    Returns:
        {
            "unread_count": 5
        }
    """
    try:
        unread_count_row = db.query_one(
            "SELECT COUNT(*) AS cnt FROM notifications WHERE user_id = ? AND is_read = 0",
            (request.user_id,)
        )
        
        unread_count = unread_count_row['cnt'] if unread_count_row else 0
        
        return jsonify({"unread_count": unread_count}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route('/<int:notif_id>/read', methods=['PUT'])
@require_auth
def mark_notification_read(notif_id):
    """
    PUT /api/v1/notifications/<id>/read
    
    Mark notification as read (protected)
    
    Returns:
        {
            "message": "Notification marked as read",
            "notification": {...}
        }
    """
    try:
        # Verify notification belongs to user
        notif = db.query_one(
            "SELECT id, is_read FROM notifications WHERE id = ? AND user_id = ?",
            (notif_id, request.user_id)
        )
        
        if not notif:
            return jsonify({"error": "Notification not found"}), 404
        
        # Update to read
        db.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = ?",
            (notif_id,)
        )
        db.commit()
        
        updated_notif = db.query_one(
            "SELECT * FROM notifications WHERE id = ?",
            (notif_id,)
        )
        
        return jsonify({
            "message": "Notification marked as read",
            "notification": updated_notif
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route('/read-all', methods=['PUT'])
@require_auth
def mark_all_read():
    """
    PUT /api/v1/notifications/read-all
    
    Mark all notifications as read (protected)
    
    Returns:
        {
            "message": "All notifications marked as read",
            "count": 10
        }
    """
    try:
        # Count unread before update
        unread_count_row = db.query_one(
            "SELECT COUNT(*) AS cnt FROM notifications WHERE user_id = ? AND is_read = 0",
            (request.user_id,)
        )
        count = unread_count_row['cnt'] if unread_count_row else 0
        
        # Update all to read
        db.execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0",
            (request.user_id,)
        )
        db.commit()
        
        return jsonify({
            "message": "All notifications marked as read",
            "count": count
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route('/<int:notif_id>', methods=['DELETE'])
@require_auth
def delete_notification(notif_id):
    """
    DELETE /api/v1/notifications/<id>
    
    Delete notification (protected)
    
    Returns:
        {
            "message": "Notification deleted successfully"
        }
    """
    try:
        # Verify notification belongs to user
        notif = db.query_one(
            "SELECT id FROM notifications WHERE id = ? AND user_id = ?",
            (notif_id, request.user_id)
        )
        
        if not notif:
            return jsonify({"error": "Notification not found"}), 404
        
        # Delete notification
        db.execute(
            "DELETE FROM notifications WHERE id = ?",
            (notif_id,)
        )
        db.commit()
        
        return jsonify({"message": "Notification deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route('/clear-all', methods=['DELETE'])
@require_auth
def clear_all_notifications():
    """
    DELETE /api/v1/notifications/clear-all
    
    Delete all notifications for user (protected)
    
    Returns:
        {
            "message": "All notifications cleared",
            "count": 15
        }
    """
    try:
        # Count before delete
        count_row = db.query_one(
            "SELECT COUNT(*) AS cnt FROM notifications WHERE user_id = ?",
            (request.user_id,)
        )
        count = count_row['cnt'] if count_row else 0
        
        # Delete all notifications
        db.execute(
            "DELETE FROM notifications WHERE user_id = ?",
            (request.user_id,)
        )
        db.commit()
        
        return jsonify({
            "message": "All notifications cleared",
            "count": count
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500