"""
Company Model
Stores target companies for applications and outreach
"""

from database.db import db, DatabaseError
from datetime import datetime
import re

class Company:
    """Company model with CRUD operations"""
    
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.name = data.get('name')
        self.website = data.get('website')
        self.location = data.get('location')
        self.industry = data.get('industry')
        self.notes = data.get('notes')
        self.source = data.get('source', 'Manual')
        self.created_at = data.get('created_at')
    
    @staticmethod
    def validate_website(website: str) -> bool:
        """Validate website URL format"""
        if not website:
            return True  # Website is optional
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(website))
    
    @staticmethod
    def validate_source(source: str) -> bool:
        """Validate source is one of allowed values"""
        valid_sources = ['Manual', 'CSV', 'API']
        return source in valid_sources
    
    @classmethod
    def create(cls, user_id: int, name: str, website: str = None, 
               location: str = None, industry: str = None, 
               notes: str = None, source: str = 'Manual') -> 'Company':
        """Create new company"""
        # Validate name
        if not name or len(name.strip()) < 2:
            raise ValueError("Company name must be at least 2 characters")
        
        # Validate website if provided
        if website and not cls.validate_website(website):
            raise ValueError("Invalid website URL format")
        
        # Validate source
        if not cls.validate_source(source):
            raise ValueError(f"Invalid source. Must be one of: Manual, CSV, API")
        
        # Check for duplicate company name (case-insensitive)
        existing = cls.find_by_name(user_id, name)
        if existing:
            raise ValueError(f"Company '{name}' already exists")
        
        try:
            company_id = db.execute_insert('''
                INSERT INTO companies (user_id, name, website, location, industry, notes, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, name.strip(), website, location, industry, notes, source, datetime.now().isoformat()))
            
            return cls.find_by_id(company_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create company: {e}")
    
    @classmethod
    def find_by_id(cls, company_id: int) -> 'Company':
        """Find company by ID"""
        data = db.execute_one('''
            SELECT * FROM companies WHERE id = ?
        ''', (company_id,))
        
        return cls(data) if data else None
    
    @classmethod
    def find_by_name(cls, user_id: int, name: str) -> 'Company':
        """Find company by name (case-insensitive)"""
        data = db.execute_one('''
            SELECT * FROM companies WHERE user_id = ? AND LOWER(name) = LOWER(?)
        ''', (user_id, name))
        
        return cls(data) if data else None
    
    @classmethod
    def find_by_user(cls, user_id: int) -> list:
        """Find all companies for a user"""
        companies_data = db.execute_query('''
            SELECT * FROM companies WHERE user_id = ? ORDER BY name ASC
        ''', (user_id,))
        
        return [cls(data) for data in companies_data]
    
    @classmethod
    def search(cls, user_id: int, search_term: str) -> list:
        """Search companies by name or location"""
        companies_data = db.execute_query('''
            SELECT * FROM companies 
            WHERE user_id = ? 
            AND (LOWER(name) LIKE LOWER(?) OR LOWER(location) LIKE LOWER(?))
            ORDER BY name ASC
        ''', (user_id, f'%{search_term}%', f'%{search_term}%'))
        
        return [cls(data) for data in companies_data]
    
    def update(self, name: str = None, website: str = None, 
               location: str = None, industry: str = None, notes: str = None) -> bool:
        """Update company details"""
        updates = []
        params = []
        
        if name:
            if len(name.strip()) < 2:
                raise ValueError("Company name must be at least 2 characters")
            # Check for duplicate (excluding self)
            existing = Company.find_by_name(self.user_id, name)
            if existing and existing.id != self.id:
                raise ValueError(f"Company '{name}' already exists")
            updates.append('name = ?')
            params.append(name.strip())
            self.name = name.strip()
        
        if website is not None:  # Allow empty string to clear website
            if website and not self.validate_website(website):
                raise ValueError("Invalid website URL format")
            updates.append('website = ?')
            params.append(website)
            self.website = website
        
        if location is not None:
            updates.append('location = ?')
            params.append(location)
            self.location = location
        
        if industry is not None:
            updates.append('industry = ?')
            params.append(industry)
            self.industry = industry
        
        if notes is not None:
            updates.append('notes = ?')
            params.append(notes)
            self.notes = notes
        
        if not updates:
            return False
        
        params.append(self.id)
        
        try:
            db.execute_update(f'''
                UPDATE companies SET {', '.join(updates)} WHERE id = ?
            ''', tuple(params))
            return True
        except DatabaseError:
            return False
    
    def delete(self) -> bool:
        """Delete company (CASCADE will delete contacts, applications, outreach)"""
        try:
            affected = db.execute_delete('''
                DELETE FROM companies WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    def get_contacts(self) -> list:
        """Get all contacts for this company"""
        from models.contact import Contact
        return Contact.find_by_company(self.id)
    
    def get_applications(self) -> list:
        """Get all applications for this company"""
        from models.application import Application
        return Application.find_by_company(self.id)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'website': self.website,
            'location': self.location,
            'industry': self.industry,
            'notes': self.notes,
            'source': self.source,
            'created_at': self.created_at
        }