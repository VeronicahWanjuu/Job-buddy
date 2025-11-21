"""
Streak Model
Handles user activity streaks and gamification points
"""

from backend.database.db import db, DatabaseError
from datetime import datetime, date, timedelta
from typing import Optional, Dict

class Streak:
    """Streak model with CRUD operations"""
    
    def __init__(self, streak_data: dict):
        self.id = streak_data.get('id')
        self.user_id = streak_data.get('user_id')
        self.current_streak = streak_data.get('current_streak', 0)
        self.longest_streak = streak_data.get('longest_streak', 0)
        self.last_activity_date = streak_data.get('last_activity_date')
        self.total_points = streak_data.get('total_points', 0)
        self.created_at = streak_data.get('created_at')
    
    # ================================================================
    # READ
    # ================================================================
    
    @classmethod
    def find_by_user_id(cls, user_id: int) -> Optional['Streak']:
        """
        Find streak by user ID
        Note: Streak is auto-created by trigger when user is created
        """
        streak_data = db.execute_one('''
            SELECT * FROM streaks WHERE user_id = ?
        ''', (user_id,))
        
        return cls(streak_data) if streak_data else None
    
    @classmethod
    def get_or_create(cls, user_id: int) -> 'Streak':
        """Get streak or create if doesn't exist (fallback)"""
        streak = cls.find_by_user_id(user_id)
        
        if not streak:
            # Shouldn't happen due to trigger, but just in case
            try:
                db.execute_insert('''
                    INSERT INTO streaks (user_id, current_streak, longest_streak, total_points)
                    VALUES (?, 0, 0, 0)
                ''', (user_id,))
                
                streak = cls.find_by_user_id(user_id)
            except DatabaseError:
                pass
        
        return streak
    
    # ================================================================
    # UPDATE STREAK
    # ================================================================
    
    def update_activity(self, points: int = 10) -> bool:
        """
        Update streak based on new activity (FR-6.1: Streak Tracking)
        
        Logic:
        - If last activity was yesterday: increment streak
        - If last activity was today: don't change streak, just add points
        - If last activity was 2+ days ago: reset streak to 1
        
        Args:
            points: Points to add for this activity (default: 10)
            
        Returns:
            True if updated successfully
        """
        today = date.today()
        
        try:
            if not self.last_activity_date:
                # First activity ever
                new_current_streak = 1
                new_longest_streak = max(1, self.longest_streak)
            else:
                last_activity = datetime.fromisoformat(self.last_activity_date).date()
                days_diff = (today - last_activity).days
                
                if days_diff == 0:
                    # Activity today, don't change streak count
                    new_current_streak = self.current_streak
                    new_longest_streak = self.longest_streak
                elif days_diff == 1:
                    # Activity yesterday, increment streak
                    new_current_streak = self.current_streak + 1
                    new_longest_streak = max(new_current_streak, self.longest_streak)
                else:
                    # Streak broken, reset to 1
                    new_current_streak = 1
                    new_longest_streak = self.longest_streak
            
            db.execute_update('''
                UPDATE streaks 
                SET current_streak = ?,
                    longest_streak = ?,
                    last_activity_date = ?,
                    total_points = total_points + ?
                WHERE user_id = ?
            ''', (new_current_streak, new_longest_streak, today.isoformat(), 
                  points, self.user_id))
            
            # Update instance
            self.current_streak = new_current_streak
            self.longest_streak = new_longest_streak
            self.last_activity_date = today.isoformat()
            self.total_points += points
            
            return True
        
        except DatabaseError:
            return False
    
    def add_points(self, points: int) -> bool:
        """
        Add points without updating streak (for micro-quests, etc.)
        
        Args:
            points: Points to add
        """
        try:
            db.execute_update('''
                UPDATE streaks 
                SET total_points = total_points + ?
                WHERE user_id = ?
            ''', (points, self.user_id))
            
            self.total_points += points
            return True
        except DatabaseError:
            return False
    
    def reset_streak(self) -> bool:
        """Reset current streak to 0 (admin function)"""
        try:
            db.execute_update('''
                UPDATE streaks 
                SET current_streak = 0
                WHERE user_id = ?
            ''', (self.user_id,))
            
            self.current_streak = 0
            return True
        except DatabaseError:
            return False
    
    # ================================================================
    # STATISTICS & CHECKS
    # ================================================================
    
    def is_active_today(self) -> bool:
        """Check if user was active today"""
        if not self.last_activity_date:
            return False
        
        try:
            last_activity = datetime.fromisoformat(self.last_activity_date).date()
            return last_activity == date.today()
        except:
            return False
    
    def days_since_last_activity(self) -> int:
        """Calculate days since last activity"""
        if not self.last_activity_date:
            return 999  # Never active
        
        try:
            last_activity = datetime.fromisoformat(self.last_activity_date).date()
            return (date.today() - last_activity).days
        except:
            return 999
    
    def will_break_tomorrow(self) -> bool:
        """Check if streak will break tomorrow if no activity"""
        if not self.last_activity_date or self.current_streak == 0:
            return False
        
        days_since = self.days_since_last_activity()
        return days_since >= 1
    
    def get_level(self) -> int:
        """
        Calculate user level based on total points (FR-6.3: Leveling System)
        Level 1: 0-99 points
        Level 2: 100-299 points
        Level 3: 300-599 points
        Level 4: 600-999 points
        Level 5: 1000+ points
        """
        if self.total_points < 100:
            return 1
        elif self.total_points < 300:
            return 2
        elif self.total_points < 600:
            return 3
        elif self.total_points < 1000:
            return 4
        else:
            return 5
    
    def points_to_next_level(self) -> int:
        """Calculate points needed to reach next level"""
        level = self.get_level()
        
        thresholds = {
            1: 100,
            2: 300,
            3: 600,
            4: 1000,
            5: 0  # Max level
        }
        
        next_threshold = thresholds.get(level, 0)
        if next_threshold == 0:
            return 0
        
        return next_threshold - self.total_points
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def to_dict(self) -> Dict:
        """Convert streak to dictionary with calculated fields"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_activity_date': self.last_activity_date,
            'total_points': self.total_points,
            'level': self.get_level(),
            'points_to_next_level': self.points_to_next_level(),
            'is_active_today': self.is_active_today(),
            'days_since_last_activity': self.days_since_last_activity(),
            'will_break_tomorrow': self.will_break_tomorrow(),
            'created_at': self.created_at
        }
    
    def __repr__(self) -> str:
        return f"<Streak(user_id={self.user_id}, current={self.current_streak}, longest={self.longest_streak}, points={self.total_points})>"
    
    def __str__(self) -> str:
        return f"{self.current_streak}-day streak ({self.total_points} points, Level {self.get_level()})"