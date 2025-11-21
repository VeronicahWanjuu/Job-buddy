"""
OutreachActivity Model
Logs direct outreach to contacts with follow-up scheduling
"""

from database.db import db, DatabaseError
from datetime import datetime, date, timedelta

class OutreachActivity:
    """OutreachActivity model with CRUD operations"""
    
    VALID_CHANNELS = ['email', 'linkedin']
    VALID_STATUSES = ['Sent', 'Responded', 'No Response']
    
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.application_id = data.get('application_id')
        self.company_id = data.get('company_id')
        self.contact_id = data.get('contact_id')
        self.channel = data.get('channel')
        self.message_template = data.get('message_template')
        self.sent_date = data.get('sent_date')
        self.follow_up_date = data.get('follow_up_date')
        self.status = data.get('status', 'Sent')
        self.created_at = data.get('created_at')
    
    @staticmethod
    def validate_channel(channel: str) -> bool:
        """Validate channel is one of allowed values"""
        return channel in OutreachActivity.VALID_CHANNELS
    
    @staticmethod
    def validate_status(status: str) -> bool:
        """Validate status is one of allowed values"""
        return status in OutreachActivity.VALID_STATUSES
    
    @staticmethod
    def validate_exactly_one_link(application_id: int, company_id: int) -> bool:
        """Validate that EXACTLY ONE of application_id OR company_id is set"""
        return (application_id is not None and company_id is None) or \
               (application_id is None and company_id is not None)
    
    @classmethod
    def create(cls, user_id: int, contact_id: int, channel: str, message_template: str,
               sent_date: str, application_id: int = None, company_id: int = None,
               follow_up_date: str = None, status: str = 'Sent') -> 'OutreachActivity':
        """Create new outreach activity"""
        # Validate exactly one link
        if not cls.validate_exactly_one_link(application_id, company_id):
            raise ValueError("Must provide EXACTLY ONE of application_id OR company_id")
        
        # Validate channel
        if not cls.validate_channel(channel):
            raise ValueError(f"Invalid channel. Must be one of: {', '.join(cls.VALID_CHANNELS)}")
        
        # Validate status
        if not cls.validate_status(status):
            raise ValueError(f"Invalid status. Must be one of: {', '.join(cls.VALID_STATUSES)}")
        
        # Validate message not empty
        if not message_template or len(message_template.strip()) < 10:
            raise ValueError("Message template must be at least 10 characters")
        
        try:
            outreach_id = db.execute_insert('''
                INSERT INTO outreach_activities 
                (user_id, application_id, company_id, contact_id, channel, message_template, 
                 sent_date, follow_up_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, application_id, company_id, contact_id, channel, message_template.strip(),
                  sent_date, follow_up_date, status, datetime.now().isoformat()))
            
            outreach = cls.find_by_id(outreach_id)
            
            # Handle post-creation actions
            cls._handle_outreach_created(outreach)
            
            return outreach
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create outreach activity: {e}")
    
    @classmethod
    def find_by_id(cls, outreach_id: int) -> 'OutreachActivity':
        """Find outreach activity by ID"""
        data = db.execute_one('''
            SELECT * FROM outreach_activities WHERE id = ?
        ''', (outreach_id,))
        
        return cls(data) if data else None
    
    @classmethod
    def find_by_user(cls, user_id: int) -> list:
        """Find all outreach activities for a user"""
        outreach_data = db.execute_query('''
            SELECT * FROM outreach_activities WHERE user_id = ? ORDER BY sent_date DESC
        ''', (user_id,))
        
        return [cls(data) for data in outreach_data]
    
    @classmethod
    def find_by_application(cls, application_id: int) -> list:
        """Find all outreach activities for an application"""
        outreach_data = db.execute_query('''
            SELECT * FROM outreach_activities WHERE application_id = ? ORDER BY sent_date DESC
        ''', (application_id,))
        
        return [cls(data) for data in outreach_data]
    
    @classmethod
    def find_by_company(cls, company_id: int) -> list:
        """Find all outreach activities for a company"""
        outreach_data = db.execute_query('''
            SELECT * FROM outreach_activities WHERE company_id = ? ORDER BY sent_date DESC
        ''', (company_id,))
        
        return [cls(data) for data in outreach_data]
    
    @classmethod
    def find_by_contact(cls, contact_id: int) -> list:
        """Find all outreach activities for a contact"""
        outreach_data = db.execute_query('''
            SELECT * FROM outreach_activities WHERE contact_id = ? ORDER BY sent_date DESC
        ''', (contact_id,))
        
        return [cls(data) for data in outreach_data]
    
    @classmethod
    def get_with_details(cls, user_id: int) -> list:
        """Get outreach activities with contact and company details"""
        outreach_data = db.execute_query('''
            SELECT 
                o.*,
                c.name as contact_name,
                c.role as contact_role,
                c.email as contact_email,
                comp.name as company_name,
                comp.location as company_location,
                a.job_title as application_job_title
            FROM outreach_activities o
            JOIN contacts c ON o.contact_id = c.id
            JOIN companies comp ON c.company_id = comp.id
            LEFT JOIN applications a ON o.application_id = a.id
            WHERE o.user_id = ?
            ORDER BY o.sent_date DESC
        ''', (user_id,))
        
        return outreach_data
    
    @staticmethod
    def _handle_outreach_created(outreach: 'OutreachActivity'):
        """Handle business logic when outreach is created"""
        # 1. Create follow-up notification if follow_up_date is set
        if outreach.follow_up_date:
            try:
                db.execute_insert('''
                    INSERT INTO notifications (user_id, type, title, message, related_type, related_id, is_read, emailed, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    outreach.user_id,
                    'follow_up',
                    'Follow up on Outreach',
                    f'It has been 5 days since your outreach. Consider sending a follow-up message.',
                    'outreach',
                    outreach.id,
                    False,
                    False,
                    outreach.follow_up_date
                ))
            except DatabaseError:
                pass
        
        # 2. Update weekly goal counter
        try:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            
            db.execute_update('''
                UPDATE goals 
                SET outreach_current = outreach_current + 1
                WHERE user_id = ? AND week_start = ?
            ''', (outreach.user_id, week_start.isoformat()))
        except DatabaseError:
            pass
        
        # 3. Update streak
        try:
            from models.streak import Streak
            Streak.update_streak(outreach.user_id)
        except:
            pass
    
    def update_status(self, new_status: str) -> bool:
        """Update outreach status"""
        if not self.validate_status(new_status):
            raise ValueError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")
        
        try:
            db.execute_update('''
                UPDATE outreach_activities 
                SET status = ?
                WHERE id = ?
            ''', (new_status, self.id))
            
            self.status = new_status
            return True
        except DatabaseError:
            return False
    
    def schedule_follow_up(self, follow_up_date: str) -> bool:
        """Schedule or update follow-up date"""
        try:
            db.execute_update('''
                UPDATE outreach_activities 
                SET follow_up_date = ?
                WHERE id = ?
            ''', (follow_up_date, self.id))
            
            self.follow_up_date = follow_up_date
            
            # Create/update follow-up notification
            db.execute_insert('''
                INSERT INTO notifications (user_id, type, title, message, related_type, related_id, is_read, emailed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.user_id,
                'follow_up',
                'Follow up on Outreach',
                f'It has been 5 days since your outreach. Consider sending a follow-up message.',
                'outreach',
                self.id,
                False,
                False,
                follow_up_date
            ))
            
            return True
        except DatabaseError:
            return False
    
    def update(self, message_template: str = None, follow_up_date: str = None) -> bool:
        """Update outreach details"""
        updates = []
        params = []
        
        if message_template:
            if len(message_template.strip()) < 10:
                raise ValueError("Message template must be at least 10 characters")
            updates.append('message_template = ?')
            params.append(message_template.strip())
            self.message_template = message_template.strip()
        
        if follow_up_date is not None:
            updates.append('follow_up_date = ?')
            params.append(follow_up_date)
            self.follow_up_date = follow_up_date
        
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
    
    def delete(self) -> bool:
        """Delete outreach activity"""
        try:
            affected = db.execute_delete('''
                DELETE FROM outreach_activities WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    def get_contact(self):
        """Get the contact for this outreach"""
        from models.contact import Contact
        return Contact.find_by_id(self.contact_id)
    
    def get_application(self):
        """Get the application for this outreach (if linked)"""
        if not self.application_id:
            return None
        from models.application import Application
        return Application.find_by_id(self.application_id)
    
    def get_company(self):
        """Get the company for this outreach (if directly linked)"""
        if not self.company_id:
            return None
        from models.company import Company
        return Company.find_by_id(self.company_id)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
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