"""
Goal Model
Tracks weekly goals for applications and outreach
"""

from database.db import db, DatabaseError
from datetime import datetime, date, timedelta

class Goal:
    """Goal model with weekly tracking"""
    
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.week_start = data.get('week_start')
        self.applications_goal = data.get('applications_goal', 5)
        self.applications_current = data.get('applications_current', 0)
        self.outreach_goal = data.get('outreach_goal', 3)
        self.outreach_current = data.get('outreach_current', 0)
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    @staticmethod
    def get_current_week_start() -> date:
        """Get the Monday of the current week"""
        today = date.today()
        return today - timedelta(days=today.weekday())
    
    @classmethod
    def create(cls, user_id: int, applications_goal: int = 5, outreach_goal: int = 3) -> 'Goal':
        """Create new weekly goal"""
        # Validate goals are positive
        if applications_goal < 1:
            raise ValueError("Applications goal must be at least 1")
        if outreach_goal < 1:
            raise ValueError("Outreach goal must be at least 1")
        
        # Get current week start
        week_start = cls.get_current_week_start()
        
        # Check if goal already exists for this week
        existing = cls.find_by_user_and_week(user_id, week_start.isoformat())
        if existing:
            raise ValueError("Goal already exists for this week")
        
        try:
            goal_id = db.execute_insert('''
                INSERT INTO goals (user_id, week_start, applications_goal, applications_current, 
                                   outreach_goal, outreach_current, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, week_start.isoformat(), applications_goal, 0, outreach_goal, 0,
                  datetime.now().isoformat(), datetime.now().isoformat()))
            
            return cls.find_by_id(goal_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create goal: {e}")
    
    @classmethod
    def find_by_id(cls, goal_id: int) -> 'Goal':
        """Find goal by ID"""
        data = db.execute_one('''
            SELECT * FROM goals WHERE id = ?
        ''', (goal_id,))
        
        return cls(data) if data else None
    
    @classmethod
    def find_by_user_and_week(cls, user_id: int, week_start: str) -> 'Goal':
        """Find goal by user and week"""
        data = db.execute_one('''
            SELECT * FROM goals WHERE user_id = ? AND week_start = ?
        ''', (user_id, week_start))
        
        return cls(data) if data else None
    
    @classmethod
    def get_current(cls, user_id: int) -> 'Goal':
        """Get current week's goal, create if doesn't exist"""
        week_start = cls.get_current_week_start()
        goal = cls.find_by_user_and_week(user_id, week_start.isoformat())
        
        if not goal:
            # Create default goal if none exists
            goal = cls.create(user_id, applications_goal=5, outreach_goal=3)
        
        return goal
    
    @classmethod
    def get_all_for_user(cls, user_id: int) -> list:
        """Get all goals for a user (history)"""
        goals_data = db.execute_query('''
            SELECT * FROM goals WHERE user_id = ? ORDER BY week_start DESC
        ''', (user_id,))
        
        return [cls(data) for data in goals_data]
    
    def update_goals(self, applications_goal: int = None, outreach_goal: int = None) -> bool:
        """Update goal targets (can only update once per week)"""
        # Check if goal was updated this week (within 7 days of creation)
        if self.updated_at:
            updated_date = datetime.fromisoformat(self.updated_at).date()
            week_start = date.fromisoformat(self.week_start)
            
            if updated_date > week_start:
                raise ValueError("Goals can only be updated once per week. Wait until next Monday.")
        
        updates = []
        params = []
        
        if applications_goal is not None:
            if applications_goal < 1:
                raise ValueError("Applications goal must be at least 1")
            updates.append('applications_goal = ?')
            params.append(applications_goal)
            self.applications_goal = applications_goal
        
        if outreach_goal is not None:
            if outreach_goal < 1:
                raise ValueError("Outreach goal must be at least 1")
            updates.append('outreach_goal = ?')
            params.append(outreach_goal)
            self.outreach_goal = outreach_goal
        
        if not updates:
            return False
        
        updates.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        params.append(self.id)
        
        try:
            db.execute_update(f'''
                UPDATE goals SET {', '.join(updates)} WHERE id = ?
            ''', tuple(params))
            return True
        except DatabaseError:
            return False
    
    def increment_applications(self) -> bool:
        """Increment applications counter"""
        try:
            db.execute_update('''
                UPDATE goals 
                SET applications_current = applications_current + 1
                WHERE id = ?
            ''', (self.id,))
            
            self.applications_current += 1
            
            # Check if goal reached
            if self.applications_current >= self.applications_goal:
                self._handle_goal_reached('applications')
            
            return True
        except DatabaseError:
            return False
    
    def increment_outreach(self) -> bool:
        """Increment outreach counter"""
        try:
            db.execute_update('''
                UPDATE goals 
                SET outreach_current = outreach_current + 1
                WHERE id = ?
            ''', (self.id,))
            
            self.outreach_current += 1
            
            # Check if goal reached
            if self.outreach_current >= self.outreach_goal:
                self._handle_goal_reached('outreach')
            
            return True
        except DatabaseError:
            return False
    
    def _handle_goal_reached(self, goal_type: str):
        """Handle business logic when goal is reached"""
        # Create celebration notification
        try:
            if goal_type == 'applications':
                title = '🎉 Weekly Application Goal Reached!'
                message = f'Congratulations! You reached your goal of {self.applications_goal} applications this week!'
            else:
                title = '🎯 Weekly Outreach Goal Reached!'
                message = f'Amazing! You completed {self.outreach_goal} outreach activities this week!'
            
            db.execute_insert('''
                INSERT INTO notifications (user_id, type, title, message, related_type, related_id, is_read, emailed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.user_id,
                'goal_reminder',
                title,
                message,
                'goal',
                self.id,
                False,
                False,
                datetime.now().isoformat()
            ))
            
            # Award bonus points
            from models.streak import Streak
            streak = Streak.find_by_user(self.user_id)
            if streak:
                db.execute_update('''
                    UPDATE streaks 
                    SET total_points = total_points + 50
                    WHERE user_id = ?
                ''', (self.user_id,))
        except DatabaseError:
            pass
    
    def get_progress(self) -> dict:
        """Get goal progress with percentages"""
        applications_percentage = int((self.applications_current / self.applications_goal) * 100) if self.applications_goal > 0 else 0
        outreach_percentage = int((self.outreach_current / self.outreach_goal) * 100) if self.outreach_goal > 0 else 0
        overall_percentage = int((applications_percentage + outreach_percentage) / 2)
        
        # Calculate days remaining
        week_start = date.fromisoformat(self.week_start)
        week_end = week_start + timedelta(days=6)
        today = date.today()
        days_remaining = (week_end - today).days
        if days_remaining < 0:
            days_remaining = 0
        
        return {
            'week_start': self.week_start,
            'week_end': week_end.isoformat(),
            'applications_goal': self.applications_goal,
            'applications_current': self.applications_current,
            'applications_percentage': applications_percentage,
            'outreach_goal': self.outreach_goal,
            'outreach_current': self.outreach_current,
            'outreach_percentage': outreach_percentage,
            'overall_percentage': overall_percentage,
            'days_remaining': days_remaining
        }
    
    def delete(self) -> bool:
        """Delete goal"""
        try:
            affected = db.execute_delete('''
                DELETE FROM goals WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'week_start': self.week_start,
            'applications_goal': self.applications_goal,
            'applications_current': self.applications_current,
            'outreach_goal': self.outreach_goal,
            'outreach_current': self.outreach_current,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }