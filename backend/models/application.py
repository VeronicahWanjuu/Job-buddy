"""
Application Model
Handles job applications and their lifecycle
"""

from backend.database.db import db, DatabaseError
from datetime import datetime, date
from typing import Optional, List, Dict

class Application:
    """Application model with CRUD operations"""
    
    # Valid status values
    VALID_STATUSES = ['Planned', 'Applied', 'Interview', 'Offer', 'Rejected']
    
    def __init__(self, app_data: dict):
        self.id = app_data.get('id')
        self.user_id = app_data.get('user_id')
        self.company_id = app_data.get('company_id')
        self.job_title = app_data.get('job_title')
        self.job_url = app_data.get('job_url')
        self.status = app_data.get('status', 'Planned')
        self.applied_date = app_data.get('applied_date')
        self.notes = app_data.get('notes')
        self.created_at = app_data.get('created_at')
        self.updated_at = app_data.get('updated_at')
    
    # ================================================================
    # VALIDATION
    # ================================================================
    
    @staticmethod
    def validate_job_title(job_title: str) -> bool:
        """Validate job title"""
        return job_title and isinstance(job_title, str) and len(job_title.strip()) >= 2
    
    @classmethod
    def validate_status(cls, status: str) -> bool:
        """Validate status value"""
        return status in cls.VALID_STATUSES
    
    # ================================================================
    # CREATE
    # ================================================================
    
    @classmethod
    def create(cls, user_id: int, company_id: int, job_title: str,
               job_url: str = None, status: str = 'Planned', 
               applied_date: str = None, notes: str = None) -> 'Application':
        """
        Create new application (FR-3.2: Application Logging)
        
        Args:
            user_id: Owner user ID
            company_id: Target company ID
            job_title: Job position title
            job_url: URL to job posting
            status: Application status (default: Planned)
            applied_date: Date application was submitted (ISO format)
            notes: User notes about application
            
        Returns:
            Application object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate job title
        if not cls.validate_job_title(job_title):
            raise ValueError("Job title must be at least 2 characters long")
        
        # Validate status
        if not cls.validate_status(status):
            raise ValueError(f"Invalid status. Must be one of: {', '.join(cls.VALID_STATUSES)}")
        
        # If status is 'Applied', applied_date is required
        if status == 'Applied' and not applied_date:
            applied_date = date.today().isoformat()
        
        try:
            app_id = db.execute_insert('''
                INSERT INTO applications 
                (user_id, company_id, job_title, job_url, status, applied_date, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, company_id, job_title.strip(), job_url, status, 
                  applied_date, notes, datetime.now().isoformat(), datetime.now().isoformat()))
            
            return cls.find_by_id(app_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create application: {e}")
    
    # ================================================================
    # READ
    # ================================================================
    
    @classmethod
    def find_by_id(cls, app_id: int) -> Optional['Application']:
        """Find application by ID"""
        app_data = db.execute_one('''
            SELECT * FROM applications WHERE id = ?
        ''', (app_id,))
        
        return cls(app_data) if app_data else None
    
    @classmethod
    def get_all_for_user(cls, user_id: int, status: str = None) -> List['Application']:
        """
        Get all applications for a user
        
        Args:
            user_id: User ID
            status: Filter by status (optional)
        """
        if status:
            if not cls.validate_status(status):
                raise ValueError(f"Invalid status. Must be one of: {', '.join(cls.VALID_STATUSES)}")
            apps_data = db.execute_query('''
                SELECT * FROM applications 
                WHERE user_id = ? AND status = ?
                ORDER BY created_at DESC
            ''', (user_id, status))
        else:
            apps_data = db.execute_query('''
                SELECT * FROM applications 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
        
        return [cls(data) for data in apps_data]
    
    @classmethod
    def get_all_for_company(cls, company_id: int) -> List['Application']:
        """Get all applications to a specific company"""
        apps_data = db.execute_query('''
            SELECT * FROM applications 
            WHERE company_id = ?
            ORDER BY created_at DESC
        ''', (company_id,))
        
        return [cls(data) for data in apps_data]
    
    @classmethod
    def get_detailed(cls, user_id: int) -> List[Dict]:
        """
        Get applications with company details using view (FR-3.6)
        """
        return db.execute_query('''
            SELECT * FROM v_applications_detailed
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
    
    @classmethod
    def search(cls, user_id: int, query: str) -> List['Application']:
        """
        Search applications by job title or company name
        
        Args:
            user_id: User ID
            query: Search query
        """
        search_pattern = f"%{query}%"
        apps_data = db.execute_query('''
            SELECT a.* FROM applications a
            JOIN companies c ON a.company_id = c.id
            WHERE a.user_id = ? AND (
                a.job_title LIKE ? COLLATE NOCASE OR 
                c.name LIKE ? COLLATE NOCASE
            )
            ORDER BY a.created_at DESC
        ''', (user_id, search_pattern, search_pattern))
        
        return [cls(data) for data in apps_data]
    
    # ================================================================
    # UPDATE
    # ================================================================
    
    def update(self, job_title: str = None, job_url: str = None, 
               status: str = None, applied_date: str = None, notes: str = None) -> bool:
        """
        Update application details (FR-3.4: Drag-and-drop status change)
        
        Returns:
            True if updated successfully
        """
        updates = []
        params = []
        
        if job_title:
            if not self.validate_job_title(job_title):
                raise ValueError("Job title must be at least 2 characters long")
            updates.append('job_title = ?')
            params.append(job_title.strip())
            self.job_title = job_title.strip()
        
        if job_url is not None:
            updates.append('job_url = ?')
            params.append(job_url)
            self.job_url = job_url
        
        if status:
            if not self.validate_status(status):
                raise ValueError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")
            updates.append('status = ?')
            params.append(status)
            self.status = status
            
            # Auto-set applied_date when moving to 'Applied' status
            if status == 'Applied' and not self.applied_date:
                updates.append('applied_date = ?')
                params.append(date.today().isoformat())
                self.applied_date = date.today().isoformat()
        
        if applied_date is not None:
            updates.append('applied_date = ?')
            params.append(applied_date)
            self.applied_date = applied_date
        
        if notes is not None:
            updates.append('notes = ?')
            params.append(notes)
            self.notes = notes
        
        if not updates:
            return False
        
        # Trigger will auto-update updated_at
        params.append(self.id)
        
        try:
            db.execute_update(f'''
                UPDATE applications SET {', '.join(updates)} WHERE id = ?
            ''', tuple(params))
            
            # Refresh updated_at from database
            app = Application.find_by_id(self.id)
            if app:
                self.updated_at = app.updated_at
            
            return True
        except DatabaseError:
            return False
    
    def update_status(self, new_status: str) -> bool:
        """
        Update application status (FR-3.4: Drag-and-drop)
        
        Args:
            new_status: New status value
            
        Returns:
            True if updated successfully
        """
        return self.update(status=new_status)
    
    # ================================================================
    # DELETE
    # ================================================================
    
    def delete(self) -> bool:
        """
        Delete application (CASCADE will delete related data)
        """
        try:
            affected = db.execute_delete('''
                DELETE FROM applications WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    def get_company(self) -> Optional[Dict]:
        """Get the company for this application"""
        result = db.execute_one('''
            SELECT * FROM companies WHERE id = ?
        ''', (self.company_id,))
        
        return dict(result) if result else None
    
    def get_outreach_activities(self) -> List[Dict]:
        """Get outreach activities related to this application"""
        return db.execute_query('''
            SELECT * FROM outreach_activities 
            WHERE application_id = ?
            ORDER BY sent_date DESC
        ''', (self.id,))
    
    def get_cv_analyses(self) -> List[Dict]:
        """Get CV analyses for this application"""
        return db.execute_query('''
            SELECT * FROM cv_analyses 
            WHERE application_id = ?
            ORDER BY created_at DESC
        ''', (self.id,))
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def days_since_applied(self) -> Optional[int]:
        """Calculate days since application was submitted"""
        if not self.applied_date:
            return None
        
        try:
            applied = datetime.fromisoformat(self.applied_date).date()
            return (date.today() - applied).days
        except:
            return None
    
    def needs_follow_up(self, days_threshold: int = 7) -> bool:
        """
        Check if application needs follow-up (FR-3.8)
        
        Args:
            days_threshold: Number of days before follow-up needed
        """
        if self.status != 'Applied':
            return False
        
        days = self.days_since_applied()
        if days is None:
            return False
        
        return days >= days_threshold
    
    def to_dict(self, include_company: bool = False) -> Dict:
        """
        Convert application to dictionary
        
        Args:
            include_company: Include company details
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'job_title': self.job_title,
            'job_url': self.job_url,
            'status': self.status,
            'applied_date': self.applied_date,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if include_company:
            company = self.get_company()
            data['company'] = company
        
        # Add computed fields
        data['days_since_applied'] = self.days_since_applied()
        data['needs_follow_up'] = self.needs_follow_up()
        
        return data
    
    def __repr__(self) -> str:
        return f"<Application(id={self.id}, job_title='{self.job_title}', status='{self.status}')>"
    
    def __str__(self) -> str:
        company = self.get_company()
        company_name = company['name'] if company else 'Unknown'
        return f"{self.job_title} at {company_name} ({self.status})"