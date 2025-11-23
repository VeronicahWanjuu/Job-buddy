"""
Notification Service
Helper functions for creating notifications
"""
from datetime import datetime, timedelta
from models import db, Notification, Application, Company

def create_follow_up_notification(user_id: int, application_id: int, days_ahead: int = 7):
    application = Application.query.get(application_id)
    if not application:
        return

    company = Company.query.get(application.company_id)
    if not company:
        return

    notify_at = datetime.now() + timedelta(days=days_ahead)

    notification = Notification(
        user_id=user_id,
        type="follow_up",
        title=f"Follow up on {company.name} Application",
        message=f"It has been {days_ahead} days since you applied. Consider sending a follow-up.",
        related_type="application",
        related_id=application_id,
        created_at=notify_at,
        is_read=False,
    )
    db.session.add(notification)
    db.session.commit()

def create_motivation_notification(user_id: int, message: str):
    notification = Notification(
        user_id=user_id,
        type="motivation",
        title="Stay Strong! 💪",
        message=message,
        created_at=datetime.now(),
        is_read=False,
    )
    db.session.add(notification)
    db.session.commit()

def create_quest_completion_notification(user_id: int, quest_title: str, points: int):
    notification = Notification(
        user_id=user_id,
        type="system",
        title="Quest Completed! 🎉",
        message=f"You completed '{quest_title}' and earned {points} points!",
        related_type="micro_quest",
        related_id=None,
        created_at=datetime.now(),
        is_read=False,
    )
    db.session.add(notification)
    db.session.commit()