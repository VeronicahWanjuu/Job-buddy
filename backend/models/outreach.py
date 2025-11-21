"""
Outreach Model
Handles direct outreach activities to contacts
"""

from backend.database.db import db, DatabaseError
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict

class Outreach:
    """Outreach activity model with CRUD operations"""
    
    # Valid channel values
    VALID_CHANNELS = ['email', 'linkedin']
    
    # Valid status values
    VALID_STATUSES = ['Sent', 'Responded', 'No Response']
    
    def __init__(self, outreach_data: dict):
        self.id = outreach_data.get('id')
        self.user_id = outreach_data.get('user_id')
        self.application_id = outreach_data.get('application_id')
        self.company_id = outreach_data.get('company_id')
        self.contact_id = outreach_data.get('contact_id')
        self.channel = outreach_data.get('channel')
        self.message_template = outreach_data.get('message_template')
        self.sent_date = outreach_data.get('sent_date')
        self.follow_up_date = outreach_data.get('follow_up_date')
        self.status = outreach_data.get('status', 'Sent')
        self.created_at = outreach_data.get('created_at')
    
    # ================================================================
    # VALIDATION
    # ================================================================
    
    @classmethod
    def validate_channel(cls, channel: str) -> bool:
        """Validate channel value"""
        return channel in cls.VALID_CHANNELS
    
    @classmethod
    def validate_status(cls, status: str) -> bool:
        """Validate status value"""
        return status in cls.VALID_STATUSES
    
    @staticmethod
    def validate_exactly_one_link(application_id: int, company_id: int) -> bool:
        """Validate that exactly ONE of application_id or company_id is set"""
        return (application_id is not None and company_id is None) or \
               (application_id is None and company_id is not None)
    
    # ================================================================
    # CREATE
    # ================================================================
    
    @classmethod
    def create(cls, user_id: int, contact_id: int, channel: str,
               message_template: str, application_id: int = None, 
               company_id: int = None, sent_date: str = None,
               follow_up_date: str = None, status: str = 'Sent') -> 'Outreach':
        """
        Create new outreach activity (FR-4.2: Outreach Logging)
        
        Args:
            user_id: Owner user ID
            contact_id: Contact being reached out to
            channel: Communication channel (email/linkedin)
            message_template: Message content
            application_id: Related application ID (optional, XOR with company_id)
            company_id: Related company ID (optional, XOR with application_id)
            sent_date: Date message was sent (ISO format, default: today)
            follow_up_date: Date to follow up (ISO format, optional)
            status: Outreach status (default: Sent)
            
        Returns:
            Outreach object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate exactly one link (application XOR company)
        if not cls.validate_exactly_one_link(application_id, company_id):
            raise ValueError("Must provide exactly ONE of application_id or company_id")
        
        # Validate channel
        if not cls.validate_channel(channel):
            raise ValueError(f"Invalid channel. Must be one of: {', '.join(cls.VALID_CHANNELS)}")
        
        # Validate status
        if not cls.validate_status(status):
            raise ValueError(f"Invalid status. Must be one of: {', '.join(cls.VALID_STATUSES)}")
        
        # Validate message
        if not message_template or len(message_template.strip()) < 10:
            raise ValueError("Message template must be at least 10 characters long")
        
        # Default sent_date to today
        if not sent_date:
            sent_date = date.today().isoformat()
        
        try:
            outreach_id = db.execute_insert('''
                INSERT INTO outreach_activities 
                (user_id, application_id, company_id, contact_id, channel, 
                 message_template, sent_date, follow_up_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, application_id, company_id, contact_id, channel,
                  message_template, sent_date, follow_up_date, status, 
                  datetime.now().isoformat()))
            
            return cls.find_by_id(outreach_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create outreach activity: {e}")
    
    # ================================================================
    # READ
    # ================================================================
    
    @classmethod
    def find_by_id(cls, outreach_id: int) -> Optional['Outreach']:
        """Find outreach activity by ID"""
        outreach_data = db.execute_one('''
            SELECT * FROM outreach_activities WHERE id = ?
        ''', (outreach_id,))
        
        return cls(outreach_data) if outreach_data else None
    
    @classmethod
    def get_all_for_user(cls, user_id: int, status: str = None) -> List['Outreach']:
        """
        Get all outreach activities for a user
        
        Args:
            user_id: User ID
            status: Filter by status (optional)
        """
        if status:
            if not cls.validate_status(status):
                raise ValueError(f"Invalid status. Must be one of: {', '.join(cls.VALID_STATUSES)}")
            outreach_data = db.execute_query('''
                SELECT * FROM outreach_activities 
                WHERE user_id = ? AND status = ?
                ORDER BY sent_date DESC
            ''', (user_id, status))
        else:
            outreach_data = db.execute_query('''
                SELECT * FROM outreach_activities 
                WHERE user_id = ?
                ORDER BY sent_date DESC
            ''', (user_id,))
        
        return [cls(data) for data in outreach_data]
    
    @classmethod
    def get_all_for_application(cls, application_id: int) -> List['Outreach']:
        """Get all outreach activities for a specific application"""
        outreach_data = db.execute_query('''
            SELECT * FROM outreach_activities 
            WHERE application_id = ?
            ORDER BY sent_date DESC
        ''', (application_id,))
        
        return [cls(data) for data in outreach_data]
    
    @classmethod
    def get_all_for_company(cls, company_id: int) -> List['Outreach']:
        """Get all outreach activities for a specific company"""
        outreach_data = db.execute_query('''
            SELECT * FROM outreach_activities 
            WHERE company_id = ?
            ORDER BY sent_date DESC
        ''', (company_id,))
        
        return [cls(data) for data in outreach_data]
    
    @classmethod
    def get_all_for_contact(cls, contact_id: int) -> List['Outreach']:
        """Get all outreach activities to a specific contact"""
        outreach_data = db.execute_query('''
            SELECT * FROM outreach_activities 
            WHERE contact_id = ?
            ORDER BY sent_date DESC
        ''', (contact_id,))
        
        return [cls(data) for data in outreach_data]
    
    @classmethod
    def get_pending_follow_ups(cls, user_id: int) -> List['Outreach']:
        """
        Get outreach activities that need follow-up (FR-4.5)
        
        Returns activities where:
        - follow_up_date is today or in the past
        - status is still 'Sent'
        """
        today = date.today().isoformat()
        
        outreach_data = db.execute_query('''
            SELECT * FROM outreach_activities 
            WHERE user_id = ? 
            AND follow_up_date <= ?
            AND status = 'Sent'
            ORDER BY follow_up_date
        ''', (user_id, today))
        
        return [cls(data) for data in outreach_data]
    
    # ================================================================
    # UPDATE
    # ================================================================
    
    def update(self, message_template: str = None, sent_date: str = None,
               follow_up_date: str = None, status: str = None) -> bool:
        """
        Update outreach activity details
        
        Returns:
            True if updated successfully
        """
        updates = []
        params = []
        
        if message_template:
            if len(message_template.strip()) < 10:
                raise ValueError("Message template must be at least 10 characters long")
            updates.append('message_template = ?')
            params.append(message_template)
            self.message_template = message_template
        
        if sent_date is not None:
            updates.append('sent_date = ?')
            params.append(sent_date)
            self.sent_date = sent_date
        
        if follow_up_date is not None:
            updates.append('follow_up_date = ?')
            params.append(follow_up_date)
            self.follow_up_date = follow_up_date
        
        if status:
            if not self.validate_status(status):
                raise ValueError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")
            updates.append('status = ?')
            params.append(status)
            self.status = status
        
        if not updates:
            return False
        
        params.append(self.id)
        
        try:
            db.execute_update(f'''
                UPDATE outreach_activities SET {', '.join(updates)} WHERE id = ?
            ''', tuple(params))
            return True
        except DatabaseError:
            return False
    
    def mark_responded(self) -> bool:
        """Mark outreach as responded"""
        return self.update(status='Responded')
    
    def mark_no_response(self) -> bool:
        """Mark outreach as no response"""
        return self.update(status='No Response')
    
    def set_follow_up_date(self, days_from_now: int = 5) -> bool:
        """
        Set follow-up date (FR-4.5)
        
        Args:
            days_from_now: Number of days from today for follow-up
        """
        follow_up = (date.today() + timedelta(days=days_from_now)).isoformat()
        return self.update(follow_up_date=follow_up)
    
    # ================================================================
    # DELETE
    # ================================================================
    
    def delete(self) -> bool:
        """Delete outreach activity"""
        try:
            affected = db.execute_delete('''
                DELETE FROM outreach_activities WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    def get_contact(self) -> Optional[Dict]:
        """Get the contact for this outreach"""
        result = db.execute_one('''
            SELECT * FROM contacts WHERE id = ?
        ''', (self.contact_id,))
        
        return dict(result) if result else None
    
    def get_application(self) -> Optional[Dict]:
        """Get related application (if linked to application)"""
        if not self.application_id:
            return None
        
        result = db.execute_one('''
            SELECT * FROM applications WHERE id = ?
        ''', (self.application_id,))
        
        return dict(result) if result else None
    
    def get_company(self) -> Optional[Dict]:
        """Get related company"""
        if self.company_id:
            # Directly linked to company
            result = db.execute_one('''
                SELECT * FROM companies WHERE id = ?
            ''', (self.company_id,))
        elif self.application_id:
            # Get company through application
            result = db.execute_one('''
                SELECT c.* FROM companies c
                JOIN applications a ON c.id = a.company_id
                WHERE a.id = ?
            ''', (self.application_id,))
        else:
            return None
        
        return dict(result) if result else None
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def days_since_sent(self) -> int:
        """Calculate days since outreach was sent"""
        try:
            sent = datetime.fromisoformat(self.sent_date).date()
            return (date.today() - sent).days
        except:
            return 0
    
    def needs_follow_up(self) -> bool:
        """Check if follow-up is due (FR-4.5)"""
        if not self.follow_up_date or self.status != 'Sent':
            return False
        
        try:
            follow_up = datetime.fromisoformat(self.follow_up_date).date()
            return date.today() >= follow_up
        except:
            return False
    
    def to_dict(self, include_relations: bool = False) -> Dict:
        """
        Convert outreach to dictionary
        
        Args:
            include_relations: Include contact, company, and application details
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'application_id': self.application_id,
            'company_id': self.company_id,
            'contact_id': self.contact_id,
            'channel': self.channel,
            'message_template': self.message_template,
            'sent_date': self.sent_date,
            'follow_up_date': self.follow_up_date,
            'status': self.status,
            'created_at': self.created_at
        }
        
        if include_relations:
            data['contact'] = self.get_contact()
            data['application'] = self.get_application()
            data['company'] = self.get_company()
        
        # Add computed fields
        data['days_since_sent'] = self.days_since_sent()
        data['needs_follow_up'] = self.needs_follow_up()
        
        return data
    
    def __repr__(self) -> str:
        return f"<Outreach(id={self.id}, channel='{self.channel}', status='{self.status}')>"
    
    def __str__(self) -> str:
        contact = self.get_contact()
        contact_name = contact['name'] if contact else 'Unknown'
        return f"{self.channel.title()} to {contact_name} ({self.status})"
