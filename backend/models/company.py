"""
Company Model
Handles target companies for job applications and outreach
"""

from backend.database.db import db, DatabaseError
from datetime import datetime
from typing import Optional, List, Dict

class Company:
    """Company model with CRUD operations"""
    
    def __init__(self, company_data: dict):
        self.id = company_data.get('id')
        self.user_id = company_data.get('user_id')
        self.name = company_data.get('name')
        self.website = company_data.get('website')
        self.location = company_data.get('location')
        self.industry = company_data.get('industry')
        self.notes = company_data.get('notes')
        self.source = company_data.get('source', 'Manual')
        self.created_at = company_data.get('created_at')
    
    # ================================================================
    # VALIDATION
    # ================================================================
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate company name"""
        return name and isinstance(name, str) and len(name.strip()) >= 2
    
    @staticmethod
    def validate_source(source: str) -> bool:
        """Validate source value"""
        return source in ['Manual', 'CSV', 'API']
    
    # ================================================================
    # CREATE
    # ================================================================
    
    @classmethod
    def create(cls, user_id: int, name: str, website: str = None, 
               location: str = None, industry: str = None, 
               notes: str = None, source: str = 'Manual') -> 'Company':
        """
        Create new company (FR-3.1: Manual Company Entry)
        
        Args:
            user_id: Owner user ID
            name: Company name (required)
            website: Company website URL
            location: Company location
            industry: Industry/sector
            notes: User notes about the company
            source: How company was added (Manual/CSV/API)
            
        Returns:
            Company object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate name
        if not cls.validate_name(name):
            raise ValueError("Company name must be at least 2 characters long")
        
        # Validate source
        if not cls.validate_source(source):
            raise ValueError(f"Invalid source. Must be one of: Manual, CSV, API")
        
        # Check if company already exists for this user (case-insensitive)
        existing = cls.find_by_name(user_id, name)
        if existing:
            raise ValueError(f"Company '{name}' already exists in your list")
        
        try:
            company_id = db.execute_insert('''
                INSERT INTO companies 
                (user_id, name, website, location, industry, notes, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, name.strip(), website, location, industry, notes, source, 
                  datetime.now().isoformat()))
            
            return cls.find_by_id(company_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create company: {e}")
    
    # ================================================================
    # READ
    # ================================================================
    
    @classmethod
    def find_by_id(cls, company_id: int) -> Optional['Company']:
        """Find company by ID"""
        company_data = db.execute_one('''
            SELECT * FROM companies WHERE id = ?
        ''', (company_id,))
        
        return cls(company_data) if company_data else None
    
    @classmethod
    def find_by_name(cls, user_id: int, name: str) -> Optional['Company']:
        """Find company by name for specific user (case-insensitive)"""
        company_data = db.execute_one('''
            SELECT * FROM companies 
            WHERE user_id = ? AND name = ? COLLATE NOCASE
        ''', (user_id, name.strip()))
        
        return cls(company_data) if company_data else None
    
    @classmethod
    def get_all_for_user(cls, user_id: int, industry: str = None) -> List['Company']:
        """
        Get all companies for a user
        
        Args:
            user_id: User ID
            industry: Filter by industry (optional)
        """
        if industry:
            companies_data = db.execute_query('''
                SELECT * FROM companies 
                WHERE user_id = ? AND industry = ?
                ORDER BY name
            ''', (user_id, industry))
        else:
            companies_data = db.execute_query('''
                SELECT * FROM companies 
                WHERE user_id = ?
                ORDER BY name
            ''', (user_id,))
        
        return [cls(data) for data in companies_data]
    
    @classmethod
    def search(cls, user_id: int, query: str) -> List['Company']:
        """
        Search companies by name, location, or industry
        
        Args:
            user_id: User ID
            query: Search query
        """
        search_pattern = f"%{query}%"
        companies_data = db.execute_query('''
            SELECT * FROM companies 
            WHERE user_id = ? AND (
                name LIKE ? COLLATE NOCASE OR 
                location LIKE ? COLLATE NOCASE OR 
                industry LIKE ? COLLATE NOCASE
            )
            ORDER BY name
        ''', (user_id, search_pattern, search_pattern, search_pattern))
        
        return [cls(data) for data in companies_data]
    
    # ================================================================
    # UPDATE
    # ================================================================
    
    def update(self, name: str = None, website: str = None, 
               location: str = None, industry: str = None, notes: str = None) -> bool:
        """
        Update company details
        
        Returns:
            True if updated successfully
        """
        updates = []
        params = []
        
        if name:
            if not self.validate_name(name):
                raise ValueError("Company name must be at least 2 characters long")
            # Check for duplicates
            existing = Company.find_by_name(self.user_id, name)
            if existing and existing.id != self.id:
                raise ValueError(f"Company '{name}' already exists in your list")
            updates.append('name = ?')
            params.append(name.strip())
            self.name = name.strip()
        
        if website is not None:  # Allow empty string to clear website
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
    
    # ================================================================
    # DELETE
    # ================================================================
    
    def delete(self) -> bool:
        """
        Delete company (CASCADE will delete contacts, applications, outreach)
        WARNING: This permanently deletes the company and ALL related data
        """
        try:
            affected = db.execute_delete('''
                DELETE FROM companies WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    def get_contacts(self) -> List[Dict]:
        """Get all contacts at this company"""
        return db.execute_query('''
            SELECT * FROM contacts 
            WHERE company_id = ?
            ORDER BY name
        ''', (self.id,))
    
    def get_applications(self) -> List[Dict]:
        """Get all applications to this company"""
        return db.execute_query('''
            SELECT * FROM applications 
            WHERE company_id = ?
            ORDER BY created_at DESC
        ''', (self.id,))
    
    def get_outreach_activities(self) -> List[Dict]:
        """Get all outreach activities to this company"""
        return db.execute_query('''
            SELECT * FROM outreach_activities 
            WHERE company_id = ?
            ORDER BY sent_date DESC
        ''', (self.id,))
    
    # ================================================================
    # STATISTICS
    # ================================================================
    
    def get_stats(self) -> Dict:
        """Get company statistics"""
        stats = {}
        
        # Count contacts
        result = db.execute_one('''
            SELECT COUNT(*) as count FROM contacts WHERE company_id = ?
        ''', (self.id,))
        stats['total_contacts'] = result['count'] if result else 0
        
        # Count applications by status
        stats['applications'] = db.execute_query('''
            SELECT status, COUNT(*) as count
            FROM applications
            WHERE company_id = ?
            GROUP BY status
        ''', (self.id,))
        
        # Count outreach activities
        result = db.execute_one('''
            SELECT COUNT(*) as count FROM outreach_activities WHERE company_id = ?
        ''', (self.id,))
        stats['total_outreach'] = result['count'] if result else 0
        
        return stats
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def to_dict(self) -> Dict:
        """Convert company to dictionary"""
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
    
    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    def __str__(self) -> str:
        return self.name