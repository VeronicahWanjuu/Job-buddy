"""
Notification Service
High-level notification creation functions
"""

from backend.models.notification import Notification
from backend.database.db import db
from typing import Optional


class NotificationService:
    """Service class for notification operations"""
    
    @staticmethod
    def create(user_id: int, notif_type: str, title: str, message: str,
               related_type: str = None, related_id: int = None):
        """Create notification - delegates to model"""
        return Notification.create(user_id, notif_type, title, message, related_type, related_id)


def create_notification(user_id: int, notif_type: str, title: str, message: str,
                       related_type: str = None, related_id: int = None):
    """Create a notification"""
    return Notification.create(user_id, notif_type, title, message, related_type, related_id)


def create_follow_up_reminder_notification(user_id: int, company_name: str, 
                                           contact_name: str, outreach_id: int = None):
    """Create follow-up reminder notification"""
    return Notification.create(
        user_id=user_id,
        notif_type='follow_up',
        title='Follow-up Reminder',
        message=f'Time to follow up with {contact_name} at {company_name}',
        related_type='outreach' if outreach_id else None,
        related_id=outreach_id
    )


def create_follow_up_notification(user_id: int, app_id: int, days_ahead: int = 7):
    """
    Wrapper for backward compatibility with applications.py
    Accepts days_ahead parameter but delegates to create_follow_up_reminder_notification
    """
    app_data = db.execute_one('''
        SELECT a.*, c.name as company_name 
        FROM applications a 
        JOIN companies c ON a.company_id = c.id 
        WHERE a.id = ?
    ''', (app_id,))
    
    if not app_data:
        return None
    
    return create_follow_up_reminder_notification(
        user_id=user_id,
        company_name=app_data['company_name'],
        contact_name='the team',
        outreach_id=None
    )


def create_goal_reminder_notification(user_id: int, goal_type: str, remaining: int):
    """Create goal reminder notification"""
    return Notification.create(
        user_id=user_id,
        notif_type='goal_reminder',
        title='Goal Reminder',
        message=f'You have {remaining} {goal_type} remaining this week!'
    )


def create_quest_completion_notification(user_id: int, quest_title: str, points: int):
    """Create quest completion notification"""
    return Notification.create(
        user_id=user_id,
        notif_type='micro_quest',
        title='Quest Completed! 🎉',
        message=f'You completed "{quest_title}" and earned {points} points!'
    )


def create_motivation_notification(user_id: int, message: str):
    """Create motivational notification"""
    return Notification.create(
        user_id=user_id,
        notif_type='motivation',
        title='Keep Going! 💪',
        message=message
    )


def create_system_notification(user_id: int, title: str, message: str):
    """Create system notification"""
    return Notification.create(
        user_id=user_id,
        notif_type='system',
        title=title,
        message=message
    )


def schedule_follow_up_notifications(user_id: int):
    """Schedule follow-up notifications for applications needing follow-up"""
    apps = db.execute_query('''
        SELECT a.id, a.job_title, c.name as company_name, a.applied_date
        FROM applications a
        JOIN companies c ON a.company_id = c.id
        WHERE a.user_id = ? AND a.status = 'Applied'
        AND DATE(a.applied_date) <= DATE('now', '-7 days')
    ''', (user_id,))
    
    count = 0
    for app in apps:
        create_follow_up_reminder_notification(
            user_id=user_id,
            company_name=app['company_name'],
            contact_name='the hiring team'
        )
        count += 1
    
    return count


def schedule_goal_reminder_notifications(user_id: int):
    """Schedule goal reminder notifications"""
    goal = db.execute_one('''
        SELECT * FROM goals 
        WHERE user_id = ? 
        AND week_start = DATE('now', 'weekday 0', '-7 days')
    ''', (user_id,))
    
    if not goal:
        return 0
    
    apps_remaining = goal['applications_goal'] - goal['applications_current']
    outreach_remaining = goal['outreach_goal'] - goal['outreach_current']
    
    count = 0
    if apps_remaining > 0:
        create_goal_reminder_notification(user_id, 'applications', apps_remaining)
        count += 1
    
    if outreach_remaining > 0:
        create_goal_reminder_notification(user_id, 'outreach', outreach_remaining)
        count += 1
    
    return count


# Export all functions (matches what __init__.py imports)
__all__ = [
    'NotificationService',
    'create_notification',
    'create_quest_completion_notification',
    'create_goal_reminder_notification',
    'create_follow_up_reminder_notification',
    'create_follow_up_notification',
    'create_motivation_notification',
    'create_system_notification',
    'schedule_follow_up_notifications',
    'schedule_goal_reminder_notifications'
]