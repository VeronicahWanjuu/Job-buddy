"""
User Model
Handles user authentication, profile management, and relationships
"""

from backend.database.db import db, DatabaseError, json_encode, json_decode
from datetime import datetime
import hashlib
import re
from typing import Optional, Dict, List

class User:
    """User model with complete CRUD operations"""
    
    def __init__(self, user_data: dict):
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.name = user_data.get('name')
        self.created_at = user_data.get('created_at')
        self.last_login = user_data.get('last_login')
        self.is_active = user_data.get('is_active', True)
        self.email_notifications_enabled = user_data.get('email_notifications_enabled', True)
        self.notification_preferences = json_decode(user_data.get('notification_preferences'))
    
    # ================================================================
    # VALIDATION METHODS
    # ================================================================
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength (FR-1.1.1 requirements)
        Returns: (is_valid, error_message)
        """
        if not password or not isinstance(password, str):
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256 (use bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return User.hash_password(password) == password_hash
    
    # ================================================================
    # CREATE/REGISTER
    # ================================================================
    
    @classmethod
    def create(cls, email: str, password: str, name: str) -> 'User':
        """
        Create new user (FR-1.1: Registration)
        
        Args:
            email: User email address
            password: Plain text password (will be hashed)
            name: User full name
            
        Returns:
            User object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate email
        if not cls.validate_email(email):
            raise ValueError("Invalid email format")
        
        # Validate password
        is_valid, error_msg = cls.validate_password(password)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Validate name
        if not name or len(name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        
        # Check if email exists
        existing = cls.find_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        
        # Hash password
        password_hash = cls.hash_password(password)
        
        # Insert user
        try:
            user_id = db.execute_insert('''
                INSERT INTO users (email, password_hash, name, created_at)
                VALUES (?, ?, ?, ?)
            ''', (email.lower().strip(), password_hash, name.strip(), datetime.now().isoformat()))
            
            # Fetch created user
            return cls.find_by_id(user_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create user: {e}")
    
    # ================================================================
    # READ/FIND
    # ================================================================
    
    @classmethod
    def find_by_id(cls, user_id: int) -> Optional['User']:
        """Find user by ID"""
        user_data = db.execute_one('''
            SELECT * FROM users WHERE id = ?
        ''', (user_id,))
        
        return cls(user_data) if user_data else None
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """Find user by email (case-insensitive)"""
        user_data = db.execute_one('''
            SELECT * FROM users WHERE email = ? COLLATE NOCASE
        ''', (email.strip(),))
        
        return cls(user_data) if user_data else None
    
    @classmethod
    def get_all(cls) -> List['User']:
        """Get all users (admin function)"""
        users_data = db.execute_query('SELECT * FROM users ORDER BY created_at DESC')
        return [cls(user_data) for user_data in users_data]
    
    # ================================================================
    # AUTHENTICATION
    # ================================================================
    
    @classmethod
    def authenticate(cls, email: str, password: str) -> 'User':
        """
        Authenticate user (FR-1.2: Login)
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            User object if authentication successful
            
        Raises:
            ValueError: If authentication fails
        """
        user = cls.find_by_email(email)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("Account is inactive")
        
        # Verify password
        if not cls.verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        # Update last login
        db.execute_update('''
            UPDATE users SET last_login = ? WHERE id = ?
        ''', (datetime.now().isoformat(), user.id))
        
        user.last_login = datetime.now().isoformat()
        
        return user
    
    # ================================================================
    # UPDATE
    # ================================================================
    
    def update_profile(self, name: str = None, email: str = None) -> bool:
        """
        Update user profile
        
        Args:
            name: New name (optional)
            email: New email (optional)
            
        Returns:
            True if updated successfully
        """
        updates = []
        params = []
        
        if name:
            if len(name.strip()) < 2:
                raise ValueError("Name must be at least 2 characters long")
            updates.append('name = ?')
            params.append(name.strip())
            self.name = name.strip()
        
        if email:
            if not self.validate_email(email):
                raise ValueError("Invalid email format")
            # Check if email already exists
            existing = User.find_by_email(email)
            if existing and existing.id != self.id:
                raise ValueError("Email already registered")
            updates.append('email = ?')
            params.append(email.lower().strip())
            self.email = email.lower().strip()
        
        if not updates:
            return False
        
        params.append(self.id)
        
        try:
            db.execute_update(f'''
                UPDATE users SET {', '.join(updates)} WHERE id = ?
            ''', tuple(params))
            return True
        except DatabaseError:
            return False
    
    def update_notification_preferences(self, preferences: dict) -> bool:
        """
        Update notification preferences (FR-9.3)
        
        Args:
            preferences: Dict with notification settings
            Example: {
                "follow_up": {"in_app": true, "email": false},
                "goal_reminder": {"in_app": true, "email": true}
            }
        """
        try:
            db.execute_update('''
                UPDATE users 
                SET notification_preferences = ?
                WHERE id = ?
            ''', (json_encode(preferences), self.id))
            
            self.notification_preferences = preferences
            return True
        except DatabaseError:
            return False
    
    def toggle_email_notifications(self, enabled: bool) -> bool:
        """Enable/disable all email notifications (FR-9.2)"""
        try:
            db.execute_update('''
                UPDATE users 
                SET email_notifications_enabled = ?
                WHERE id = ?
            ''', (enabled, self.id))
            
            self.email_notifications_enabled = enabled
            return True
        except DatabaseError:
            return False
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Change user password
        
        Args:
            old_password: Current password
            new_password: New password
            
        Returns:
            True if changed successfully
            
        Raises:
            ValueError: If validation fails
        """
        # Verify old password
        if not self.verify_password(old_password, self.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        is_valid, error_msg = self.validate_password(new_password)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Hash new password
        new_hash = self.hash_password(new_password)
        
        try:
            db.execute_update('''
                UPDATE users SET password_hash = ? WHERE id = ?
            ''', (new_hash, self.id))
            
            self.password_hash = new_hash
            return True
        except DatabaseError:
            return False
    
    def deactivate(self) -> bool:
        """Deactivate user account"""
        try:
            db.execute_update('''
                UPDATE users SET is_active = FALSE WHERE id = ?
            ''', (self.id,))
            self.is_active = False
            return True
        except DatabaseError:
            return False
    
    def activate(self) -> bool:
        """Reactivate user account"""
        try:
            db.execute_update('''
                UPDATE users SET is_active = TRUE WHERE id = ?
            ''', (self.id,))
            self.is_active = True
            return True
        except DatabaseError:
            return False
    
    # ================================================================
    # DELETE
    # ================================================================
    
    def delete(self) -> bool:
        """
        Delete user (CASCADE will delete all related data)
        WARNING: This permanently deletes the user and ALL their data
        """
        try:
            affected = db.execute_delete('''
                DELETE FROM users WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    def get_onboarding_data(self) -> Optional[Dict]:
        """Get user's onboarding data with dream milestone (FR-2.1)"""
        result = db.execute_one('''
            SELECT * FROM onboarding_data WHERE user_id = ?
        ''', (self.id,))
        
        return dict(result) if result else None
    
    def get_companies(self) -> List[Dict]:
        """Get all companies for this user"""
        return db.execute_query('''
            SELECT * FROM companies WHERE user_id = ? ORDER BY created_at DESC
        ''', (self.id,))
    
    def get_applications(self, status: str = None) -> List[Dict]:
        """
        Get all applications for this user
        
        Args:
            status: Filter by status (optional)
        """
        if status:
            return db.execute_query('''
                SELECT * FROM applications 
                WHERE user_id = ? AND status = ?
                ORDER BY created_at DESC
            ''', (self.id, status))
        else:
            return db.execute_query('''
                SELECT * FROM applications 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (self.id,))
    
    def get_streak(self) -> Optional[Dict]:
        """Get user's streak data"""
        result = db.execute_one('''
            SELECT * FROM streaks WHERE user_id = ?
        ''', (self.id,))
        
        return dict(result) if result else None
    
    def get_current_week_goals(self) -> Optional[Dict]:
        """Get user's goals for current week"""
        from datetime import date, timedelta
        
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        
        result = db.execute_one('''
            SELECT * FROM goals 
            WHERE user_id = ? AND week_start = ?
        ''', (self.id, monday.isoformat()))
        
        return dict(result) if result else None
    
    def get_unread_notifications(self) -> List[Dict]:
        """Get unread notifications for this user"""
        return db.execute_query('''
            SELECT * FROM notifications 
            WHERE user_id = ? AND is_read = FALSE
            ORDER BY created_at DESC
        ''', (self.id,))
    
    # ================================================================
    # STATISTICS
    # ================================================================
    
    def get_stats(self) -> Dict:
        """Get comprehensive user statistics"""
        stats = {}
        
        # Application counts by status
        stats['applications'] = db.execute_query('''
            SELECT status, COUNT(*) as count
            FROM applications
            WHERE user_id = ?
            GROUP BY status
        ''', (self.id,))
        
        # Total companies
        result = db.execute_one('''
            SELECT COUNT(*) as count FROM companies WHERE user_id = ?
        ''', (self.id,))
        stats['total_companies'] = result['count'] if result else 0
        
        # Total outreach activities
        result = db.execute_one('''
            SELECT COUNT(*) as count FROM outreach_activities WHERE user_id = ?
        ''', (self.id,))
        stats['total_outreach'] = result['count'] if result else 0
        
        # Streak data
        streak = self.get_streak()
        if streak:
            stats['streak'] = {
                'current': streak['current_streak'],
                'longest': streak['longest_streak'],
                'points': streak['total_points']
            }
        
        # Current week goals
        goals = self.get_current_week_goals()
        if goals:
            stats['weekly_goals'] = {
                'applications': f"{goals['applications_current']}/{goals['applications_goal']}",
                'outreach': f"{goals['outreach_current']}/{goals['outreach_goal']}"
            }
        
        return stats
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def to_dict(self, include_sensitive: bool = False) -> Dict:
        """
        Convert user to dictionary
        
        Args:
            include_sensitive: Include password_hash (default: False)
        """
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_active': self.is_active,
            'email_notifications_enabled': self.email_notifications_enabled,
            'notification_preferences': self.notification_preferences
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.email})"