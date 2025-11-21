"""
CV Analysis Model
Handles CV/resume analysis and ATS scoring
"""

from backend.database.db import db, DatabaseError, json_encode, json_decode
from datetime import datetime
from typing import Optional, List, Dict

class CVAnalysis:
    """CV analysis model with CRUD operations"""
    
    def __init__(self, cv_data: dict):
        self.id = cv_data.get('id')
        self.user_id = cv_data.get('user_id')
        self.application_id = cv_data.get('application_id')
        self.cv_filename = cv_data.get('cv_filename')
        self.cv_file_path = cv_data.get('cv_file_path')
        self.job_description = cv_data.get('job_description')
        self.ats_score = cv_data.get('ats_score')
        self.matched_keywords = json_decode(cv_data.get('matched_keywords'))
        self.missing_keywords = json_decode(cv_data.get('missing_keywords'))
        self.suggestions = json_decode(cv_data.get('suggestions'))
        self.api_used = cv_data.get('api_used', 'internal')
        self.created_at = cv_data.get('created_at')
    
    # ================================================================
    # VALIDATION
    # ================================================================
    
    @staticmethod
    def validate_ats_score(score: int) -> bool:
        """Validate ATS score is between 0 and 100"""
        return isinstance(score, int) and 0 <= score <= 100
    
    # ================================================================
    # CREATE
    # ================================================================
    
    @classmethod
    def create(cls, user_id: int, cv_filename: str, job_description: str,
               ats_score: int, matched_keywords: List[str] = None, 
               missing_keywords: List[str] = None, suggestions: List[Dict] = None,
               application_id: int = None, cv_file_path: str = None,
               api_used: str = 'internal') -> 'CVAnalysis':
        """
        Create new CV analysis (FR-7.1: ATS Scoring)
        
        Args:
            user_id: Owner user ID
            cv_filename: Name of CV file
            job_description: Job description text
            ats_score: ATS compatibility score (0-100)
            matched_keywords: List of matched keywords (default: [])
            missing_keywords: List of missing keywords (default: [])
            suggestions: List of improvement suggestions (default: [])
            application_id: Related application ID (optional)
            cv_file_path: Path to stored CV file (optional)
            api_used: API used for analysis (internal/external)
            
        Returns:
            CVAnalysis object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate ATS score
        if not cls.validate_ats_score(ats_score):
            raise ValueError("ATS score must be an integer between 0 and 100")
        
        # Validate filename
        if not cv_filename or len(cv_filename.strip()) < 3:
            raise ValueError("CV filename must be at least 3 characters long")
        
        # Validate job description
        if not job_description or len(job_description.strip()) < 50:
            raise ValueError("Job description must be at least 50 characters long")
        
        # ✅ FIX: Convert None to empty lists BEFORE json_encode
        matched_keywords = matched_keywords if matched_keywords is not None else []
        missing_keywords = missing_keywords if missing_keywords is not None else []
        suggestions = suggestions if suggestions is not None else []
        
        try:
            cv_id = db.execute_insert('''
                INSERT INTO cv_analyses 
                (user_id, application_id, cv_filename, cv_file_path, job_description,
                 ats_score, matched_keywords, missing_keywords, suggestions, api_used, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, application_id, cv_filename.strip(), cv_file_path, 
                  job_description.strip(), ats_score, 
                  json_encode(matched_keywords),      # ✅ Now always valid list
                  json_encode(missing_keywords),      # ✅ Now always valid list
                  json_encode(suggestions),           # ✅ Now always valid list
                  api_used, datetime.now().isoformat()))
            
            return cls.find_by_id(cv_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create CV analysis: {e}")
    
    # ================================================================
    # READ
    # ================================================================
    
    @classmethod
    def find_by_id(cls, cv_id: int) -> Optional['CVAnalysis']:
        """Find CV analysis by ID"""
        cv_data = db.execute_one('''
            SELECT * FROM cv_analyses WHERE id = ?
        ''', (cv_id,))
        
        return cls(cv_data) if cv_data else None
    
    @classmethod
    def get_all_for_user(cls, user_id: int) -> List['CVAnalysis']:
        """Get all CV analyses for a user"""
        cv_data = db.execute_query('''
            SELECT * FROM cv_analyses 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        return [cls(data) for data in cv_data]
    
    @classmethod
    def get_all_for_application(cls, application_id: int) -> List['CVAnalysis']:
        """Get all CV analyses for a specific application"""
        cv_data = db.execute_query('''
            SELECT * FROM cv_analyses 
            WHERE application_id = ?
            ORDER BY created_at DESC
        ''', (application_id,))
        
        return [cls(data) for data in cv_data]
    
    @classmethod
    def get_latest_for_application(cls, application_id: int) -> Optional['CVAnalysis']:
        """Get most recent CV analysis for an application"""
        cv_data = db.execute_one('''
            SELECT * FROM cv_analyses 
            WHERE application_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (application_id,))
        
        return cls(cv_data) if cv_data else None
    
    # ================================================================
    # DELETE
    # ================================================================
    
    def delete(self) -> bool:
        """Delete CV analysis"""
        try:
            affected = db.execute_delete('''
                DELETE FROM cv_analyses WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    # ================================================================
    # RELATIONSHIPS
    # ================================================================
    
    def get_application(self) -> Optional[Dict]:
        """Get related application (if linked)"""
        if not self.application_id:
            return None
        
        result = db.execute_one('''
            SELECT * FROM applications WHERE id = ?
        ''', (self.application_id,))
        
        return dict(result) if result else None
    
    # ================================================================
    # ANALYSIS METHODS
    # ================================================================
    
    def get_score_category(self) -> str:
        """
        Categorize ATS score (FR-7.2: Score Interpretation)
        
        Returns:
            'Excellent', 'Good', 'Fair', or 'Poor'
        """
        if self.ats_score >= 80:
            return 'Excellent'
        elif self.ats_score >= 60:
            return 'Good'
        elif self.ats_score >= 40:
            return 'Fair'
        else:
            return 'Poor'
    
    def get_score_color(self) -> str:
        """Get color code for score visualization"""
        category = self.get_score_category()
        
        colors = {
            'Excellent': 'green',
            'Good': 'blue',
            'Fair': 'orange',
            'Poor': 'red'
        }
        
        return colors.get(category, 'gray')
    
    def get_keyword_match_rate(self) -> float:
        """Calculate percentage of matched keywords"""
        if not self.matched_keywords and not self.missing_keywords:
            return 0.0
        
        total_keywords = len(self.matched_keywords or []) + len(self.missing_keywords or [])
        if total_keywords == 0:
            return 0.0
        
        matched_count = len(self.matched_keywords or [])
        return (matched_count / total_keywords) * 100
    
    def get_priority_suggestions(self, max_count: int = 5) -> List[Dict]:
        """
        Get top priority suggestions (FR-7.3: Actionable Suggestions)
        
        Args:
            max_count: Maximum number of suggestions to return
        """
        if not self.suggestions:
            return []
        
        # Return top N suggestions
        return self.suggestions[:max_count]
    
    def needs_improvement(self) -> bool:
        """Check if CV needs significant improvement (score < 60)"""
        return self.ats_score < 60
    
    # ================================================================
    # UTILITY
    # ================================================================
    
    def to_dict(self, include_application: bool = False) -> Dict:
        """
        Convert CV analysis to dictionary
        
        Args:
            include_application: Include application details
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'application_id': self.application_id,
            'cv_filename': self.cv_filename,
            'cv_file_path': self.cv_file_path,
            'job_description': self.job_description,
            'ats_score': self.ats_score,
            'matched_keywords': self.matched_keywords,
            'missing_keywords': self.missing_keywords,
            'suggestions': self.suggestions,
            'api_used': self.api_used,
            'created_at': self.created_at,
            # Computed fields
            'score_category': self.get_score_category(),
            'score_color': self.get_score_color(),
            'keyword_match_rate': round(self.get_keyword_match_rate(), 1),
            'needs_improvement': self.needs_improvement()
        }
        
        if include_application:
            data['application'] = self.get_application()
        
        return data
    
    def __repr__(self) -> str:
        return f"<CVAnalysis(id={self.id}, score={self.ats_score}, user_id={self.user_id})>"
    
    def __str__(self) -> str:
        return f"CV Analysis: {self.cv_filename} (ATS Score: {self.ats_score}/100)"