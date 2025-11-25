"""
Notification Service

Helper functions for creating notifications using DatabaseManager
"""
from datetime import datetime, timedelta
from database.db import db

def create_follow_up_notification(user_id: int, application_id: int, days_ahead: int = 7):
    """
    Create a follow-up notification for an application
    
    Args:
        user_id: User ID
        application_id: Application ID
        days_ahead: Days in the future to schedule notification
    """
    # Fetch application and company
    application = db.query_one(
        "SELECT id, company_id FROM applications WHERE id = ? AND user_id = ?",
        (application_id, user_id),
    )
    
    if not application:
        return
    
    company = db.query_one(
        "SELECT id, name FROM companies WHERE id = ? AND user_id = ?",
        (application["company_id"], user_id),
    )
    
    if not company:
        return
    
    notify_at = datetime.now() + timedelta(days=days_ahead)
    
    db.execute(
        """
        INSERT INTO notifications
        (user_id, type, title, message, related_type, related_id, created_at, is_read)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            "follow_up",
            f"Follow up on {company['name']} Application",
            f"It has been {days_ahead} days since you applied. Consider sending a follow-up.",
            "application",
            application_id,
            notify_at.isoformat(),
            0,
        ),
    )
    db.commit()

def create_motivation_notification(user_id: int, message: str):
    """
    Create a motivational notification
    
    Args:
        user_id: User ID
        message: Motivation message
    """
    db.execute(
        """
        INSERT INTO notifications
        (user_id, type, title, message, related_type, related_id, created_at, is_read)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            "motivation",
            "Stay Strong! 💪",
            message,
            None,
            None,
            datetime.now().isoformat(),
            0,
        ),
    )
    db.commit()

def create_quest_completion_notification(user_id: int, quest_title: str, points: int):
    """
    Create a notification for quest completion
    
    Args:
        user_id: User ID
        quest_title: Title of completed quest
        points: Points earned
    """
    db.execute(
        """
        INSERT INTO notifications
        (user_id, type, title, message, related_type, related_id, created_at, is_read)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            "system",
            "Quest Completed! 🎉",
            f"You completed '{quest_title}' and earned {points} points!",
            "micro_quest",
            None,
            datetime.now().isoformat(),
            0,
        ),
    )
    db.commit()