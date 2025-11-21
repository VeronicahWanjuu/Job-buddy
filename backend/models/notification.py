"""
Notification Model
Handles in-app and email notifications
"""

from backend.database.db import db, DatabaseError
from datetime import datetime, timedelta
from typing import Optional, List, Dict

class Notification:
    """Notification model with CRUD operations"""
    
    # Valid notification types
    VALID_TYPES = ['follow_up', 'goal_reminder', 'micro_quest', 'motivation', 'system']
    
    # Valid related types
    VALID_RELATED_TYPES = ['application', 'outreach', 'micro_quest', 'goal', None]
    
    def __init__(self, notif_data: dict):
        self.id = notif_data.get('id')
        self.user_id = notif_data.get('user_id')
        self.type = notif_data.get('type')
        self.title = notif_data.get('title')
        self.message = notif_data.get('message')
        self.related_type = notif_data.get('related_type')
        self.related_id = notif_data.get('related_id')
        self.is_read = notif_data.get('is_read', False)
        self.emailed = notif_data.get('emailed', False)
        self.created_at = notif_data.get('created_at')
    
    # ================================================================
    # VALIDATION
    # ================================================================
    
    @classmethod
    def validate_type(cls, notif_type: str) -> bool:
        """Validate notification type"""
        return notif_type in cls.VALID_TYPES
    
    @classmethod
    def validate_related_type(cls, related_type: str) -> bool:
        """Validate related type"""
        return related_type in cls.VALID_RELATED_TYPES
    
    # ================================================================
    # CREATE
    # ================================================================
    
    @classmethod
    def create(cls, user_id: int, notif_type: str, title: str, message: str,
               related_type: str = None, related_id: int = None) -> 'Notification':
        """
        Create new notification (FR-9.1: In-App Notifications)
        
        Args:
            user_id: User to notify
            notif_type: Notification type (follow_up, goal_reminder, etc.)
            title: Notification title
            message: Notification message
            related_type: Type of related entity (optional)
            related_id: ID of related entity (optional)
            
        Returns:
            Notification object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate type
        if not cls.validate_type(notif_type):
            raise ValueError(f"Invalid notification type. Must be one of: {', '.join(cls.VALID_TYPES)}")
        
        # Validate related_type if provided
        if related_type and not cls.validate_related_type(related_type):
            raise ValueError(f"Invalid related type. Must be one of: {', '.join(str(t) for t in cls.VALID_RELATED_TYPES if t)}")
        
        # Validate title and message
        if not title or len(title.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        
        if not message or len(message.strip()) < 10:
            raise ValueError("Message must be at least 10 characters long")
        
        try:
            notif_id = db.execute_insert('''
                INSERT INTO notifications 
                (user_id, type, title, message, related_type, related_id, 
                 is_read, emailed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, FALSE, FALSE, ?)
            ''', (user_id, notif_type, title.strip(), message.strip(), 
                  related_type, related_id, datetime.now().isoformat()))
            
            return cls.find_by_id(notif_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create notification: {e}")
    
    # ================================================================
    # READ
    # ================================================================
    
    @classmethod
    def find_by_id(cls, notif_id: int) -> Optional['Notification']:
        """Find notification by ID"""
        notif_data = db.execute_one('''
            SELECT * FROM notifications WHERE id = ?
        ''', (notif_id,))
        
        return cls(notif_data) if notif_data else None
    
    @classmethod
    def get_all_for_user(cls, user_id: int, unread_only: bool = False) -> List['Notification']:
        """
        Get all notifications for a user (FR-9.1)
        
        Args:
            user_id: User ID
            unread_only: Only return unread notifications
        """
        if unread_only:
            notifs_data = db.execute_query('''
                SELECT * FROM notifications 
                WHERE user_id = ? AND is_read = FALSE
                ORDER BY created_at DESC
            ''', (user_id,))
        else:
            notifs_data = db.execute_query('''
                SELECT * FROM notifications 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
        
        return [cls(data) for data in notifs_data]
    
    @classmethod
    def get_by_type(cls, user_id: int, notif_type: str) -> List['Notification']:
        """Get notifications by type for a user"""
        if not cls.validate_type(notif_type):
            raise ValueError(f"Invalid notification type. Must be one of: {', '.join(cls.VALID_TYPES)}")
        
        notifs_data = db.execute_query('''
            SELECT * FROM notifications 
            WHERE user_id = ? AND type = ?
            ORDER BY created_at DESC
        ''', (user_id, notif_type))
        
        return [cls(data) for data in notifs_data]
    
    @classmethod
    def get_unemailed(cls, user_id: int) -> List['Notification']:
        """
        Get notifications that haven't been emailed yet (FR-9.2)
        
        Used by email service to batch send notifications
        """
        notifs_data = db.execute_query('''
            SELECT * FROM notifications 
            WHERE user_id = ? AND emailed = FALSE
            ORDER BY created_at
        ''', (user_id,))
        
        return [cls(data) for data in notifs_data]
    
    # ================================================================
    # UPDATE
    # ================================================================
    
    def mark_as_read(self) -> bool:
        """Mark notification as read"""
        try:
            db.execute_update('''
                UPDATE notifications 
                SET is_read = TRUE
                WHERE id = ?
            ''', (self.id,))
            
            self.is_read = True
            return True
        except DatabaseError:
            return False
    
    def mark_as_unread(self) -> bool:
        """Mark notification as unread"""
        try:
            db.execute_update('''
                UPDATE notifications 
                SET is_read = FALSE
                WHERE id = ?
            ''', (self.id,))
            
            self.is_read = False
            return True
        except DatabaseError:
            return False
    
    def mark_as_emailed(self) -> bool:
        """Mark notification as emailed (FR-9.2)"""
        try:
            db.execute_update('''
                UPDATE notifications 
                SET emailed = TRUE
                WHERE id = ?
            ''', (self.id,))
            
            self.emailed = True
            return True
        except DatabaseError:
            return False
    
    @classmethod
    def mark_all_as_read(cls, user_id: int) -> int:
        """
        Mark all notifications as read for a user
        
        Returns:
            Number of notifications marked as read
        """
        try:
            count = db.execute_update('''
                UPDATE notifications 
                SET is_read = TRUE
                WHERE user_id = ? AND is_read = FALSE
            ''', (user_id,))
            
            return count
        except DatabaseError:
            return 0
    
    # ================================================================
    # DELETE
    # ================================================================
    
    def delete(self) -> bool:
        """Delete notification"""
        try:
            affected = db.execute_delete('''
                DELETE FROM notifications WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    @classmethod
    def delete_old(cls, user_id: int, days_old: int = 30) -> int:
        """
        Delete notifications older than specified days
        
        Args:
            user_id: User ID
            days_old: Delete notifications older than this many days
            
        Returns:
            Number of notifications deleted
        """
        cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
        
        try:
            count = db.execute_delete('''
                DELETE FROM notifications 
                WHERE user_id = ? AND created_at < ?
            ''', (user_id, cutoff_date))
            
            return count
        except DatabaseError:
            return 0
    
    # ================================================================
    # RELATED ENTITY
    # ================================================================
    
    def get_related_entity(self) -> Optional[Dict]:
        """Get the related entity (application, outreach, etc.)"""
        if not self.related_type or not self.related_id:
            return None
        
        table_map = {
            'application': 'applications',
            'outreach': 'outreach_activities',
            'goal': 'goals',
            'micro_quest': 'user_quests'
        }
        
        table = table_map.get(self.related_type)
        if not table:
            return None
        
        try:
            result = db.execute_one(f'''
                SELECT * FROM {table} WHERE id = ?
            ''', (self.related_id,))
            
            return dict(result) if result else None
        except DatabaseError:
            return None
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def to_dict(self, include_related: bool = False) -> Dict:
        """
        Convert notification to dictionary
        
        Args:
            include_related: Include related entity details
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'related_type': self.related_type,
            'related_id': self.related_id,
            'is_read': self.is_read,
            'emailed': self.emailed,
            'created_at': self.created_at
        }
        
        if include_related:
            data['related_entity'] = self.get_related_entity()
        
        return data
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type='{self.type}', read={self.is_read})>"
    
    def __str__(self) -> str:
        return f"{self.type.replace('_', ' ').title()}: {self.title}"