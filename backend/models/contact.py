"""
Contact Model
Handles contacts at target companies
"""

from backend.database.db import db, DatabaseError
from datetime import datetime
from typing import Optional, List, Dict
import re

class Contact:
    """Contact model with CRUD operations"""
    
    def __init__(self, contact_data: dict):
        self.id = contact_data.get('id')
        self.company_id = contact_data.get('company_id')
        self.name = contact_data.get('name')
        self.role = contact_data.get('role')
        self.email = contact_data.get('email')
        self.linkedin_url = contact_data.get('linkedin_url')
        self.notes = contact_data.get('notes')
        self.source = contact_data.get('source', 'Manual')
        self.created_at = contact_data.get('created_at')
    
    # ================================================================
    # VALIDATION
    # ================================================================
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate contact name"""
        return name and isinstance(name, str) and len(name.strip()) >= 2
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return True  # Email is optional
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_source(source: str) -> bool:
        """Validate source value"""
        return source in ['Manual', 'API']
    
    # ================================================================
    # CREATE
    # ================================================================
    
    @classmethod
    def create(cls, company_id: int, name: str, role: str = None,
               email: str = None, linkedin_url: str = None, 
               notes: str = None, source: str = 'Manual') -> 'Contact':
        """
        Create new contact (FR-4.1: Contact Discovery)
        
        Args:
            company_id: Company this contact works at
            name: Contact name (required)
            role: Job title/role
            email: Contact email
            linkedin_url: LinkedIn profile URL
            notes: User notes about contact
            source: How contact was added (Manual/API)
            
        Returns:
            Contact object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate name
        if not cls.validate_name(name):
            raise ValueError("Contact name must be at least 2 characters long")
        
        # Validate email if provided
        if email and not cls.validate_email(email):
            raise ValueError("Invalid email format")
        
        # Validate source
        if not cls.validate_source(source):
            raise ValueError(f"Invalid source. Must be one of: Manual, API")
        
        # Check if contact with same email already exists at this company
        if email:
            existing = cls.find_by_email(company_id, email)
            if existing:
                raise ValueError(f"Contact with email '{email}' already exists at this company")
        
        try:
            contact_id = db.execute_insert('''
                INSERT INTO contacts 
                (company_id, name, role, email, linkedin_url, notes, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company_id, name.strip(), role, email.lower() if email else None, 
                  linkedin_url, notes, source, datetime.now().isoformat()))
            
            return cls.find_by_id(contact_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create contact: {e}")
    
    # ================================================================
    # READ
    # ================================================================
    
    @classmethod
    def find_by_id(cls, contact_id: int) -> Optional['Contact']:
        """Find contact by ID"""
        contact_data = db.execute_one('''
            SELECT * FROM contacts WHERE id = ?
        ''', (contact_id,))
        
        return cls(contact_data) if contact_data else None
    
    @classmethod
    def find_by_email(cls, company_id: int, email: str) -> Optional['Contact']:
        """Find contact by email at specific company (case-insensitive)"""
        if not email:
            return None
        
        contact_data = db.execute_one('''
            SELECT * FROM contacts 
            WHERE company_id = ? AND email = ? COLLATE NOCASE
        ''', (company_id, email.strip()))
        
        return cls(contact_data) if contact_data else None
    
    @classmethod
    def get_all_for_company(cls, company_id: int) -> List['Contact']:
        """Get all contacts at a specific company"""
        contacts_data = db.execute_query('''
            SELECT * FROM contacts 
            WHERE company_id = ?
            ORDER BY name
        ''', (company_id,))
        
        return [cls(data) for data in contacts_data]
    
    @classmethod
    def get_all_for_user(cls, user_id: int) -> List['Contact']:
        """Get all contacts for a user (across all their companies)"""
        contacts_data = db.execute_query('''
            SELECT c.* FROM contacts c
            JOIN companies comp ON c.company_id = comp.id
            WHERE comp.user_id = ?
            ORDER BY c.name
        ''', (user_id,))
        
        return [cls(data) for data in contacts_data]
    
    @classmethod
    def search(cls, user_id: int, query: str) -> List['Contact']:
        """
        Search contacts by name, role, or email
        
        Args:
            user_id: User ID
            query: Search query
        """
        search_pattern = f"%{query}%"
        contacts_data = db.execute_query('''
            SELECT c.* FROM contacts c
            JOIN companies comp ON c.company_id = comp.id
            WHERE comp.user_id = ? AND (
                c.name LIKE ? COLLATE NOCASE OR 
                c.role LIKE ? COLLATE NOCASE OR 
                c.email LIKE ? COLLATE NOCASE
            )
            ORDER BY c.name
        ''', (user_id, search_pattern, search_pattern, search_pattern))
        
        return [cls(data) for data in contacts_data]
    
    # ================================================================
    # UPDATE
    # ================================================================
    
    def update(self, name: str = None, role: str = None, email: str = None,
               linkedin_url: str = None, notes: str = None) -> bool:
        """
        Update contact details
        
        Returns:
            True if updated successfully
        """
        updates = []
        params = []
        
        if name:
            if not self.validate_name(name):
                raise ValueError("Contact name must be at least 2 characters long")
            updates.append('name = ?')
            params.append(name.strip())
            self.name = name.strip()
        
        if role is not None:
            updates.append('role = ?')
            params.append(role)
            self.role = role
        
        if email is not None:
            if email and not self.validate_email(email):
                raise ValueError("Invalid email format")
            # Check for duplicate email at same company
            if email:
                existing = Contact.find_by_email(self.company_id, email)
                if existing and existing.id != self.id:
                    raise ValueError(f"Contact with email '{email}' already exists at this company")
            updates.append('email = ?')
            params.append(email.lower() if email else None)
            self.email = email.lower() if email else None
        
        if linkedin_url is not None:
            updates.append('linkedin_url = ?')
            params.append(linkedin_url)
            self.linkedin_url = linkedin_url
        
        if notes is not None:
            updates.append('notes = ?')
            params.append(notes)
            self.notes = notes
        
        if not updates:
            return False
        
        params.append(self.id)
        
        try:
            db.execute_update(f'''
                UPDATE contacts SET {', '.join(updates)} WHERE id = ?
            ''', tuple(params))
            return True
        except DatabaseError:
            return False
    
    # ================================================================
    # DELETE
    # ================================================================
    
    def delete(self) -> bool:
        """
        Delete contact (CASCADE will delete related outreach activities)
        """
        try:
            affected = db.execute_delete('''
                DELETE FROM contacts WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    def get_company(self) -> Optional[Dict]:
        """Get the company this contact works at"""
        result = db.execute_one('''
            SELECT * FROM companies WHERE id = ?
        ''', (self.company_id,))
        
        return dict(result) if result else None
    
    def get_outreach_activities(self) -> List[Dict]:
        """Get all outreach activities sent to this contact"""
        return db.execute_query('''
            SELECT * FROM outreach_activities 
            WHERE contact_id = ?
            ORDER BY sent_date DESC
        ''', (self.id,))
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def to_dict(self, include_company: bool = False) -> Dict:
        """
        Convert contact to dictionary
        
        Args:
            include_company: Include company details
        """
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'role': self.role,
            'email': self.email,
            'linkedin_url': self.linkedin_url,
            'notes': self.notes,
            'source': self.source,
            'created_at': self.created_at
        }
        
        if include_company:
            company = self.get_company()
            data['company'] = company
        
        return data
    
    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name='{self.name}', company_id={self.company_id})>"
    
    def __str__(self) -> str:
        return f"{self.name}" + (f" ({self.role})" if self.role else "")