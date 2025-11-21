"""
Onboarding Data Model
Handles user onboarding information (feeling + dream milestone)
"""

from backend.database.db import db, DatabaseError
from datetime import datetime
from typing import Optional, Dict

class OnboardingData:
    """Onboarding data model"""
    
    # Valid feelings
    VALID_FEELINGS = [
        'Excited and ready',
        'Overwhelmed but motivated',
        'Frustrated and stuck',
        'Just getting started'
    ]
    
    def __init__(self, onboarding_data: dict):
        self.id = onboarding_data.get('id')
        self.user_id = onboarding_data.get('user_id')
        self.current_feeling = onboarding_data.get('current_feeling')
        self.dream_milestone = onboarding_data.get('dream_milestone')
        self.completed_at = onboarding_data.get('completed_at')
    
    # ================================================================
    # VALIDATION
    # ================================================================
    
    @classmethod
    def validate_feeling(cls, feeling: str) -> bool:
        """Validate feeling value"""
        return feeling in cls.VALID_FEELINGS
    
    # ================================================================
    # CREATE
    # ================================================================
    
    @classmethod
    def create(cls, user_id: int, current_feeling: str, dream_milestone: str) -> 'OnboardingData':
        """
        Create onboarding data (FR-2.1: Onboarding)
        
        Args:
            user_id: User ID
            current_feeling: User's current feeling about job search
            dream_milestone: User's career dream/goal
            
        Returns:
            OnboardingData object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate feeling
        if not cls.validate_feeling(current_feeling):
            raise ValueError(f"Invalid feeling. Must be one of: {', '.join(cls.VALID_FEELINGS)}")
        
        # Validate dream milestone
        if not dream_milestone or len(dream_milestone.strip()) < 10:
            raise ValueError("Dream milestone must be at least 10 characters long")
        
        # Check if onboarding data already exists for this user
        existing = cls.find_by_user_id(user_id)
        if existing:
            raise ValueError("Onboarding data already exists for this user")
        
        try:
            onboarding_id = db.execute_insert('''
                INSERT INTO onboarding_data 
                (user_id, current_feeling, dream_milestone, completed_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, current_feeling, dream_milestone.strip(), 
                  datetime.now().isoformat()))
            
            return cls.find_by_id(onboarding_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create onboarding data: {e}")
    
    # ================================================================
    # READ
    # ================================================================
    
    @classmethod
    def find_by_id(cls, onboarding_id: int) -> Optional['OnboardingData']:
        """Find onboarding data by ID"""
        onboarding_data = db.execute_one('''
            SELECT * FROM onboarding_data WHERE id = ?
        ''', (onboarding_id,))
        
        return cls(onboarding_data) if onboarding_data else None
    
    @classmethod
    def find_by_user_id(cls, user_id: int) -> Optional['OnboardingData']:
        """Find onboarding data by user ID (1:1 relationship)"""
        onboarding_data = db.execute_one('''
            SELECT * FROM onboarding_data WHERE user_id = ?
        ''', (user_id,))
        
        return cls(onboarding_data) if onboarding_data else None
    
    # ================================================================
    # UPDATE
    # ================================================================
    
    def update(self, current_feeling: str = None, dream_milestone: str = None) -> bool:
        """
        Update onboarding data
        
        Returns:
            True if updated successfully
        """
        updates = []
        params = []
        
        if current_feeling:
            if not self.validate_feeling(current_feeling):
                raise ValueError(f"Invalid feeling. Must be one of: {', '.join(self.VALID_FEELINGS)}")
            updates.append('current_feeling = ?')
            params.append(current_feeling)
            self.current_feeling = current_feeling
        
        if dream_milestone:
            if len(dream_milestone.strip()) < 10:
                raise ValueError("Dream milestone must be at least 10 characters long")
            updates.append('dream_milestone = ?')
            params.append(dream_milestone.strip())
            self.dream_milestone = dream_milestone.strip()
        
        if not updates:
            return False
        
        params.append(self.user_id)
        
        try:
            db.execute_update(f'''
                UPDATE onboarding_data SET {', '.join(updates)} WHERE user_id = ?
            ''', tuple(params))
            return True
        except DatabaseError:
            return False
    
    # ================================================================
    # DELETE
    # ================================================================
    
    def delete(self) -> bool:
        """Delete onboarding data"""
        try:
            affected = db.execute_delete('''
                DELETE FROM onboarding_data WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def to_dict(self) -> Dict:
        """Convert onboarding data to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'current_feeling': self.current_feeling,
            'dream_milestone': self.dream_milestone,
            'completed_at': self.completed_at
        }
    
    def __repr__(self) -> str:
        return f"<OnboardingData(user_id={self.user_id}, feeling='{self.current_feeling}')>"
    
    def __str__(self) -> str:
        return f"{self.current_feeling}: {self.dream_milestone[:50]}..."