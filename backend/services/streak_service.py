"""
Streak Service
Handles streak calculations and updates
"""
from datetime import date, timedelta
from models import db, Streak

def update_user_streak(user_id: int, points: int = 10) -> dict:
    streak = Streak.query.filter_by(user_id=user_id).first()
    if not streak:
        return {"error": "Streak not found"}

    today = date.today()
    last_activity_date = streak.last_activity_date

    if last_activity_date is None:
        new_streak = 1
    else:
        if last_activity_date == today:
            new_streak = streak.current_streak
        elif last_activity_date == (today - timedelta(days=1)):
            new_streak = streak.current_streak + 1
        else:
            new_streak = 1

    new_longest = max(streak.longest_streak or 0, new_streak)

    streak.current_streak = new_streak
    streak.longest_streak = new_longest
    streak.last_activity_date = today
    streak.total_points = (streak.total_points or 0) + points

    db.session.commit()

    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "total_points": streak.total_points,
    }