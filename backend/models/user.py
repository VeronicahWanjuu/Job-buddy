"""
User Model

"""

from database.db import db, DatabaseError, json_encode, json_decode
from datetime import datetime
import hashlib
import re

class User:
    """User model with CRUD operations"""
    
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
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
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
        """Hash password (use bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @classmethod
    def create(cls, email: str, password: str, name: str) -> 'User':
        """Create new user"""
        # Validate email
        if not cls.validate_email(email):
            raise ValueError("Invalid email format")
        
        # Validate password
        is_valid, error_msg = cls.validate_password(password)
        if not is_valid:
            raise ValueError(error_msg)
        
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
            ''', (email, password_hash, name, datetime.now()))
            
            # Fetch created user
            return cls.find_by_id(user_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create user: {e}")
    
    @classmethod
    def find_by_id(cls, user_id: int) -> 'User':
        """Find user by ID"""
        user_data = db.execute_one('''
            SELECT * FROM users WHERE id = ?
        ''', (user_id,))
        
        return cls(user_data) if user_data else None
    
    @classmethod
    def find_by_email(cls, email: str) -> 'User':
        """Find user by email"""
        user_data = db.execute_one('''
            SELECT * FROM users WHERE email = ? COLLATE NOCASE
        ''', (email,))
        
        return cls(user_data) if user_data else None
    
    @classmethod
    def authenticate(cls, email: str, password: str) -> 'User':
        """Authenticate user"""
        user = cls.find_by_email(email)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("Account is inactive")
        
        # Verify password
        password_hash = cls.hash_password(password)
        if password_hash != user.password_hash:
            raise ValueError("Invalid email or password")
        
        # Update last login
        db.execute_update('''
            UPDATE users SET last_login = ? WHERE id = ?
        ''', (datetime.now(), user.id))
        
        return user
    
    def update_profile(self, name: str = None, notification_prefs: dict = None) -> bool:
        """Update user profile"""
        updates = []
        params = []
        
        if name:
            updates.append('name = ?')
            params.append(name)
            self.name = name
        
        if notification_prefs:
            updates.append('notification_preferences = ?')
            params.append(json_encode(notification_prefs))
            self.notification_preferences = notification_prefs
        
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
    
    def delete(self) -> bool:
        """Delete user (CASCADE will delete all related data)"""
        try:
            affected = db.execute_delete('''
                DELETE FROM users WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    def get_onboarding_data(self) -> dict:
        """Get user's onboarding data with dream milestone"""
        result = db.execute_one('''
            SELECT * FROM onboarding_data WHERE user_id = ?
        ''', (self.id,))
        
        return result if result else None
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (exclude password_hash)"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_active': self.is_active,
            'email_notifications_enabled': self.email_notifications_enabled,
            'notification_preferences': self.notification_preferences
        }