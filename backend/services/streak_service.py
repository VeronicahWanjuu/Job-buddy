"""
Streak Service

Handles streak calculations and updates using DatabaseManager (raw SQL)
"""
from datetime import date, timedelta
from database.db import db

def update_user_streak(user_id: int, points: int = 10) -> dict:
    """
    Update user's streak based on activity
    
    Args:
        user_id: User ID
        points: Points to add (default 10)
        
    Returns:
        Dict with current_streak, longest_streak, total_points
    """
    # Fetch streak row for the user
    streak_row = db.query_one(
        """
        SELECT id, current_streak, longest_streak, last_activity_date, total_points
        FROM streaks
        WHERE user_id = ?
        """,
        (user_id,),
    )
    
    if not streak_row:
        return {"error": "Streak not found"}
    
    today = date.today()
    last_activity_date = streak_row["last_activity_date"]
    
    if last_activity_date is None:
        # First activity
        new_streak = 1
    else:
        # last_activity_date is stored as 'YYYY-MM-DD' string
        last_date = date.fromisoformat(last_activity_date)
        
        if last_date == today:
            # Same day - streak doesn't change
            new_streak = streak_row["current_streak"]
        elif last_date == (today - timedelta(days=1)):
            # Consecutive day - increment streak
            new_streak = streak_row["current_streak"] + 1
        else:
            # Gap - reset streak
            new_streak = 1
    
    new_longest = max(streak_row["longest_streak"] or 0, new_streak)
    new_total_points = (streak_row["total_points"] or 0) + points
    
    db.execute(
        """
        UPDATE streaks
        SET current_streak = ?, longest_streak = ?, last_activity_date = ?, total_points = ?
        WHERE user_id = ?
        """,
        (new_streak, new_longest, today.isoformat(), new_total_points, user_id),
    )
    db.commit()
    
    return {
        "current_streak": new_streak,
        "longest_streak": new_longest,
        "total_points": new_total_points,
    }