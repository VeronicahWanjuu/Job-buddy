"""
Goal Model
Handles weekly application and outreach goals
"""

from backend.database.db import db, DatabaseError
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict

class Goal:
    """Weekly goal model with CRUD operations"""
    
    def __init__(self, goal_data: dict):
        self.id = goal_data.get('id')
        self.user_id = goal_data.get('user_id')
        self.week_start = goal_data.get('week_start')
        self.applications_goal = goal_data.get('applications_goal', 5)
        self.applications_current = goal_data.get('applications_current', 0)
        self.outreach_goal = goal_data.get('outreach_goal', 3)
        self.outreach_current = goal_data.get('outreach_current', 0)
        self.created_at = goal_data.get('created_at')
        self.updated_at = goal_data.get('updated_at')
    
    # ================================================================
    # VALIDATION
    # ================================================================
    
    @staticmethod
    def validate_goal_value(value: int) -> bool:
        """Validate goal values are positive integers"""
        return isinstance(value, int) and value > 0
    
    @staticmethod
    def get_week_start(target_date: date = None) -> date:
        """
        Get Monday of the week for a given date
        
        Args:
            target_date: Date to find week start for (default: today)
        """
        if not target_date:
            target_date = date.today()
        
        # Calculate Monday (0 = Monday, 6 = Sunday)
        return target_date - timedelta(days=target_date.weekday())
    
    # ================================================================
    # CREATE
    # ================================================================
    
    @classmethod
    def create(cls, user_id: int, applications_goal: int = 5, 
               outreach_goal: int = 3, week_start: date = None) -> 'Goal':
        """
        Create new weekly goal (FR-5.1: Goal Setting)
        
        Args:
            user_id: Owner user ID
            applications_goal: Target number of applications (default: 5)
            outreach_goal: Target number of outreach activities (default: 3)
            week_start: Week starting date (default: current week Monday)
            
        Returns:
            Goal object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate goals
        if not cls.validate_goal_value(applications_goal):
            raise ValueError("Applications goal must be a positive integer")
        
        if not cls.validate_goal_value(outreach_goal):
            raise ValueError("Outreach goal must be a positive integer")
        
        # Get week start
        if not week_start:
            week_start = cls.get_week_start()
        
        # Check if goal already exists for this week
        existing = cls.find_by_week(user_id, week_start)
        if existing:
            raise ValueError(f"Goal already exists for week starting {week_start}")
        
        try:
            goal_id = db.execute_insert('''
                INSERT INTO goals 
                (user_id, week_start, applications_goal, applications_current, 
                 outreach_goal, outreach_current, created_at, updated_at)
                VALUES (?, ?, ?, 0, ?, 0, ?, ?)
            ''', (user_id, week_start.isoformat(), applications_goal, outreach_goal,
                  datetime.now().isoformat(), datetime.now().isoformat()))
            
            return cls.find_by_id(goal_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create goal: {e}")
    
    # ================================================================
    # READ
    # ================================================================
    
    @classmethod
    def find_by_id(cls, goal_id: int) -> Optional['Goal']:
        """Find goal by ID"""
        goal_data = db.execute_one('''
            SELECT * FROM goals WHERE id = ?
        ''', (goal_id,))
        
        return cls(goal_data) if goal_data else None
    
    @classmethod
    def find_by_week(cls, user_id: int, week_start: date) -> Optional['Goal']:
        """Find goal for specific week"""
        goal_data = db.execute_one('''
            SELECT * FROM goals 
            WHERE user_id = ? AND week_start = ?
        ''', (user_id, week_start.isoformat()))
        
        return cls(goal_data) if goal_data else None
    
    @classmethod
    def get_current_week(cls, user_id: int) -> Optional['Goal']:
        """
        Get goal for current week (FR-5.2: Weekly Progress Tracking)
        """
        week_start = cls.get_week_start()
        return cls.find_by_week(user_id, week_start)
    
    @classmethod
    def get_or_create_current_week(cls, user_id: int, 
                                    applications_goal: int = 5,
                                    outreach_goal: int = 3) -> 'Goal':
        """
        Get current week's goal or create if doesn't exist
        """
        goal = cls.get_current_week(user_id)
        if not goal:
            goal = cls.create(user_id, applications_goal, outreach_goal)
        return goal
    
    @classmethod
    def get_all_for_user(cls, user_id: int, limit: int = None) -> List['Goal']:
        """
        Get all goals for a user (ordered by most recent first)
        
        Args:
            user_id: User ID
            limit: Maximum number of goals to return (optional)
        """
        if limit:
            goals_data = db.execute_query('''
                SELECT * FROM goals 
                WHERE user_id = ?
                ORDER BY week_start DESC
                LIMIT ?
            ''', (user_id, limit))
        else:
            goals_data = db.execute_query('''
                SELECT * FROM goals 
                WHERE user_id = ?
                ORDER BY week_start DESC
            ''', (user_id,))
        
        return [cls(data) for data in goals_data]
    
    # ================================================================
    # UPDATE
    # ================================================================
    
    def update_targets(self, applications_goal: int = None, 
                      outreach_goal: int = None) -> bool:
        """
        Update goal targets (FR-5.1: Editable Goals)
        
        Returns:
            True if updated successfully
        """
        updates = []
        params = []
        
        if applications_goal is not None:
            if not self.validate_goal_value(applications_goal):
                raise ValueError("Applications goal must be a positive integer")
            updates.append('applications_goal = ?')
            params.append(applications_goal)
            self.applications_goal = applications_goal
        
        if outreach_goal is not None:
            if not self.validate_goal_value(outreach_goal):
                raise ValueError("Outreach goal must be a positive integer")
            updates.append('outreach_goal = ?')
            params.append(outreach_goal)
            self.outreach_goal = outreach_goal
        
        if not updates:
            return False
        
        # Trigger will auto-update updated_at
        params.append(self.id)
        
        try:
            db.execute_update(f'''
                UPDATE goals SET {', '.join(updates)} WHERE id = ?
            ''', tuple(params))
            
            # Refresh updated_at from database
            goal = Goal.find_by_id(self.id)
            if goal:
                self.updated_at = goal.updated_at
            
            return True
        except DatabaseError:
            return False
    
    def increment_applications(self, count: int = 1) -> bool:
        """
        Increment applications count (called when user logs an application)
        
        Args:
            count: Number to increment by (default: 1)
        """
        try:
            db.execute_update('''
                UPDATE goals 
                SET applications_current = applications_current + ?
                WHERE id = ?
            ''', (count, self.id))
            
            self.applications_current += count
            return True
        except DatabaseError:
            return False
    
    def increment_outreach(self, count: int = 1) -> bool:
        """
        Increment outreach count (called when user logs outreach)
        
        Args:
            count: Number to increment by (default: 1)
        """
        try:
            db.execute_update('''
                UPDATE goals 
                SET outreach_current = outreach_current + ?
                WHERE id = ?
            ''', (count, self.id))
            
            self.outreach_current += count
            return True
        except DatabaseError:
            return False
    
    def reset_progress(self) -> bool:
        """Reset current progress to 0 (for manual resets)"""
        try:
            db.execute_update('''
                UPDATE goals 
                SET applications_current = 0, outreach_current = 0
                WHERE id = ?
            ''', (self.id,))
            
            self.applications_current = 0
            self.outreach_current = 0
            return True
        except DatabaseError:
            return False
    
    # ================================================================
    # DELETE
    # ================================================================
    
    def delete(self) -> bool:
        """Delete goal"""
        try:
            affected = db.execute_delete('''
                DELETE FROM goals WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    # ================================================================
    # STATISTICS & CALCULATIONS
    # ================================================================
    
    def applications_progress_percentage(self) -> float:
        """Calculate applications progress as percentage"""
        if self.applications_goal == 0:
            return 0.0
        return min((self.applications_current / self.applications_goal) * 100, 100.0)
    
    def outreach_progress_percentage(self) -> float:
        """Calculate outreach progress as percentage"""
        if self.outreach_goal == 0:
            return 0.0
        return min((self.outreach_current / self.outreach_goal) * 100, 100.0)
    
    def overall_progress_percentage(self) -> float:
        """Calculate overall progress (average of both goals)"""
        app_progress = self.applications_progress_percentage()
        outreach_progress = self.outreach_progress_percentage()
        return (app_progress + outreach_progress) / 2
    
    def is_applications_complete(self) -> bool:
        """Check if applications goal is met"""
        return self.applications_current >= self.applications_goal
    
    def is_outreach_complete(self) -> bool:
        """Check if outreach goal is met"""
        return self.outreach_current >= self.outreach_goal
    
    def is_complete(self) -> bool:
        """Check if both goals are met"""
        return self.is_applications_complete() and self.is_outreach_complete()
    
    def days_remaining_in_week(self) -> int:
        """Calculate days remaining in this goal's week"""
        try:
            week_start = datetime.fromisoformat(self.week_start).date()
            week_end = week_start + timedelta(days=6)  # Sunday
            today = date.today()
            
            if today > week_end:
                return 0
            elif today < week_start:
                return 7
            else:
                return (week_end - today).days + 1
        except:
            return 0
    
    def is_current_week(self) -> bool:
        """Check if this goal is for the current week"""
        try:
            week_start = datetime.fromisoformat(self.week_start).date()
            current_week_start = self.get_week_start()
            return week_start == current_week_start
        except:
            return False
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def to_dict(self) -> Dict:
        """Convert goal to dictionary with calculated fields"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'week_start': self.week_start,
            'applications_goal': self.applications_goal,
            'applications_current': self.applications_current,
            'applications_remaining': max(0, self.applications_goal - self.applications_current),
            'applications_progress': round(self.applications_progress_percentage(), 1),
            'applications_complete': self.is_applications_complete(),
            'outreach_goal': self.outreach_goal,
            'outreach_current': self.outreach_current,
            'outreach_remaining': max(0, self.outreach_goal - self.outreach_current),
            'outreach_progress': round(self.outreach_progress_percentage(), 1),
            'outreach_complete': self.is_outreach_complete(),
            'overall_progress': round(self.overall_progress_percentage(), 1),
            'is_complete': self.is_complete(),
            'days_remaining': self.days_remaining_in_week(),
            'is_current_week': self.is_current_week(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self) -> str:
        return f"<Goal(id={self.id}, week={self.week_start}, apps={self.applications_current}/{self.applications_goal})>"
    
    def __str__(self) -> str:
        return f"Week of {self.week_start}: {self.applications_current}/{self.applications_goal} apps, {self.outreach_current}/{self.outreach_goal} outreach"