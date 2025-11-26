"""
Notification Utilities
Backward compatibility wrapper for notification functions
"""

# Import all notification functions from services
from backend.services.notifications import (
    NotificationService,
    create_notification,
    create_quest_completion_notification,
    create_goal_reminder_notification,
    create_follow_up_reminder_notification,
    create_follow_up_notification,
    create_motivation_notification,
    create_system_notification,
    schedule_follow_up_notifications,
    schedule_goal_reminder_notifications
)

# Explicit exports for backward compatibility
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