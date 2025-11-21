"""
User Quest Model
Handles completed micro-quests for gamification
"""

from backend.database.db import db, DatabaseError
from datetime import datetime
from typing import Optional, List, Dict

class UserQuest:
    """User quest model for tracking completed micro-quests"""
    
    def __init__(self, quest_data: dict):
        self.id = quest_data.get('id')
        self.user_id = quest_data.get('user_id')
        self.quest_id = quest_data.get('quest_id')
        self.completed_at = quest_data.get('completed_at')
    
    # ================================================================
    # CREATE
    # ================================================================
    
    @classmethod
    def create(cls, user_id: int, quest_id: str) -> 'UserQuest':
        """
        Mark quest as completed (FR-6.2: Micro-Quests)
        
        Args:
            user_id: User who completed the quest
            quest_id: Quest identifier (e.g., 'mq-1', 'mq-2')
            
        Returns:
            UserQuest object
            
        Raises:
            ValueError: If validation fails or quest already completed
        """
        # Validate quest_id format
        if not quest_id or len(quest_id) < 2:
            raise ValueError("Quest ID must be at least 2 characters long")
        
        # Check if already completed
        if cls.is_completed(user_id, quest_id):
            raise ValueError(f"Quest '{quest_id}' already completed by this user")
        
        try:
            uq_id = db.execute_insert('''
                INSERT INTO user_quests (user_id, quest_id, completed_at)
                VALUES (?, ?, ?)
            ''', (user_id, quest_id, datetime.now().isoformat()))
            
            return cls.find_by_id(uq_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to mark quest as completed: {e}")
    
    # ================================================================
    # READ
    # ================================================================
    
    @classmethod
    def find_by_id(cls, uq_id: int) -> Optional['UserQuest']:
        """Find user quest by ID"""
        quest_data = db.execute_one('''
            SELECT * FROM user_quests WHERE id = ?
        ''', (uq_id,))
        
        return cls(quest_data) if quest_data else None
    
    @classmethod
    def get_all_for_user(cls, user_id: int) -> List['UserQuest']:
        """Get all completed quests for a user"""
        quests_data = db.execute_query('''
            SELECT * FROM user_quests 
            WHERE user_id = ?
            ORDER BY completed_at DESC
        ''', (user_id,))
        
        return [cls(data) for data in quests_data]
    
    @classmethod
    def is_completed(cls, user_id: int, quest_id: str) -> bool:
        """
        Check if user has completed a specific quest
        
        Args:
            user_id: User ID
            quest_id: Quest identifier
        """
        result = db.execute_one('''
            SELECT id FROM user_quests 
            WHERE user_id = ? AND quest_id = ?
        ''', (user_id, quest_id))
        
        return result is not None
    
    @classmethod
    def get_completed_count(cls, user_id: int) -> int:
        """Get total number of quests completed by user"""
        result = db.execute_one('''
            SELECT COUNT(*) as count FROM user_quests 
            WHERE user_id = ?
        ''', (user_id,))
        
        return result['count'] if result else 0
    
    @classmethod
    def get_completed_quest_ids(cls, user_id: int) -> List[str]:
        """
        Get list of all completed quest IDs for a user
        
        Useful for checking which quests are still available
        """
        results = db.execute_query('''
            SELECT quest_id FROM user_quests 
            WHERE user_id = ?
            ORDER BY completed_at DESC
        ''', (user_id,))
        
        return [row['quest_id'] for row in results]
    
    # ================================================================
    # DELETE
    # ================================================================
    
    def delete(self) -> bool:
        """Delete quest completion record (admin function)"""
        try:
            affected = db.execute_delete('''
                DELETE FROM user_quests WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    @classmethod
    def reset_user_quests(cls, user_id: int) -> int:
        """
        Reset all completed quests for a user (admin function)
        
        Returns:
            Number of quest completions deleted
        """
        try:
            count = db.execute_delete('''
                DELETE FROM user_quests WHERE user_id = ?
            ''', (user_id,))
            
            return count
        except DatabaseError:
            return 0
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def to_dict(self) -> Dict:
        """Convert user quest to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quest_id': self.quest_id,
            'completed_at': self.completed_at
        }
    
    def __repr__(self) -> str:
        return f"<UserQuest(id={self.id}, user_id={self.user_id}, quest_id='{self.quest_id}')>"
    
    def __str__(self) -> str:
        return f"Quest {self.quest_id} completed"