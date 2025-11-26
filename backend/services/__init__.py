from .streak_service import update_user_streak
from .notifications import (  # ✅ CORRECT FILE! (no _service)
    create_follow_up_notification,
    create_motivation_notification,
    create_quest_completion_notification,
    create_notification,
    create_goal_reminder_notification,
    create_follow_up_reminder_notification,
    create_system_notification,
    schedule_follow_up_notifications,
    schedule_goal_reminder_notifications,
    NotificationService,
)

__all__ = [
    'update_user_streak',
    'create_follow_up_notification',
    'create_motivation_notification',
    'create_quest_completion_notification',
    'create_notification',
    'create_goal_reminder_notification',
    'create_follow_up_reminder_notification',
    'create_system_notification',
    'schedule_follow_up_notifications',
    'schedule_goal_reminder_notifications',
    'NotificationService',
]