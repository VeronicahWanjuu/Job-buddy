"""
CVAnalysis Model
Stores CV keyword analysis results
"""

from database.db import db, DatabaseError, json_encode, json_decode
from datetime import datetime

class CVAnalysis:
    """CVAnalysis model for tracking CV optimization"""
    
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.application_id = data.get('application_id')
        self.cv_filename = data.get('cv_filename')
        self.cv_file_path = data.get('cv_file_path')
        self.job_description = data.get('job_description')
        self.ats_score = data.get('ats_score')
        self.matched_keywords = json_decode(data.get('matched_keywords')) if data.get('matched_keywords') else []
        self.missing_keywords = json_decode(data.get('missing_keywords')) if data.get('missing_keywords') else []
        self.suggestions = json_decode(data.get('suggestions')) if data.get('suggestions') else []
        self.api_used = data.get('api_used', 'internal')
        self.created_at = data.get('created_at')
    
    @classmethod
    def create(cls, user_id: int, cv_filename: str, job_description: str,
               ats_score: int, matched_keywords: list, missing_keywords: list,
               suggestions: list, application_id: int = None, cv_file_path: str = None,
               api_used: str = 'internal') -> 'CVAnalysis':
        """Create new CV analysis"""
        # Validate ATS score
        if not 0 <= ats_score <= 100:
            raise ValueError("ATS score must be between 0 and 100")
        
        # Validate filename
        if not cv_filename or len(cv_filename.strip()) < 3:
            raise ValueError("CV filename must be at least 3 characters")
        
        # Validate job description
        if not job_description or len(job_description.strip()) < 20:
            raise ValueError("Job description must be at least 20 characters")
        
        # Validate keywords are lists
        if not isinstance(matched_keywords, list):
            raise ValueError("Matched keywords must be a list")
        if not isinstance(missing_keywords, list):
            raise ValueError("Missing keywords must be a list")
        if not isinstance(suggestions, list):
            raise ValueError("Suggestions must be a list")
        
        try:
            # Store only first 1000 chars of job description to save space
            jd_truncated = job_description[:1000] if len(job_description) > 1000 else job_description
            
            analysis_id = db.execute_insert('''
                INSERT INTO cv_analyses (user_id, application_id, cv_filename, cv_file_path,
                                        job_description, ats_score, matched_keywords, 
                                        missing_keywords, suggestions, api_used, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, application_id, cv_filename.strip(), cv_file_path, jd_truncated,
                  ats_score, json_encode(matched_keywords), json_encode(missing_keywords),
                  json_encode(suggestions), api_used, datetime.now().isoformat()))
            
            return cls.find_by_id(analysis_id)
        
        except DatabaseError as e:
            raise ValueError(f"Failed to create CV analysis: {e}")
    
    @classmethod
    def find_by_id(cls, analysis_id: int) -> 'CVAnalysis':
        """Find CV analysis by ID"""
        data = db.execute_one('''
            SELECT * FROM cv_analyses WHERE id = ?
        ''', (analysis_id,))
        
        return cls(data) if data else None
    
    @classmethod
    def find_by_user(cls, user_id: int, limit: int = 20) -> list:
        """Find all CV analyses for a user"""
        analyses_data = db.execute_query('''
            SELECT * FROM cv_analyses 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        return [cls(data) for data in analyses_data]
    
    @classmethod
    def find_by_application(cls, application_id: int) -> list:
        """Find all CV analyses for an application"""
        analyses_data = db.execute_query('''
            SELECT * FROM cv_analyses 
            WHERE application_id = ? 
            ORDER BY created_at DESC
        ''', (application_id,))
        
        return [cls(data) for data in analyses_data]
    
    @classmethod
    def get_with_application_details(cls, user_id: int) -> list:
        """Get CV analyses with application and company details"""
        analyses_data = db.execute_query('''
            SELECT 
                cv.*,
                a.job_title,
                a.status as application_status,
                c.name as company_name
            FROM cv_analyses cv
            LEFT JOIN applications a ON cv.application_id = a.id
            LEFT JOIN companies c ON a.company_id = c.id
            WHERE cv.user_id = ?
            ORDER BY cv.created_at DESC
        ''', (user_id,))
        
        return analyses_data
    
    @classmethod
    def get_average_score(cls, user_id: int) -> float:
        """Get average ATS score for user's analyses"""
        result = db.execute_one('''
            SELECT AVG(ats_score) as avg_score 
            FROM cv_analyses 
            WHERE user_id = ?
        ''', (user_id,))
        
        return round(result['avg_score'], 2) if result and result['avg_score'] else 0.0
    
    @classmethod
    def get_score_trend(cls, user_id: int, limit: int = 5) -> list:
        """Get recent ATS scores to show improvement trend"""
        analyses_data = db.execute_query('''
            SELECT ats_score, created_at 
            FROM cv_analyses 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        return [
            {'score': data['ats_score'], 'date': data['created_at']} 
            for data in analyses_data
        ]
    
    def delete(self) -> bool:
        """Delete CV analysis"""
        try:
            affected = db.execute_delete('''
                DELETE FROM cv_analyses WHERE id = ?
            ''', (self.id,))
            return affected > 0
        except DatabaseError:
            return False
    
    def get_application(self):
        """Get the application this analysis is linked to"""
        if not self.application_id:
            return None
        from models.application import Application
        return Application.find_by_id(self.application_id)
    
    def get_score_category(self) -> dict:
        """Get score category and color coding"""
        if self.ats_score >= 80:
            return {
                'category': 'Excellent',
                'color': 'green',
                'emoji': '🟢',
                'message': 'Your CV is well-optimized!'
            }
        elif self.ats_score >= 60:
            return {
                'category': 'Good',
                'color': 'yellow',
                'emoji': '🟡',
                'message': 'Good match! A few improvements will help.'
            }
        elif self.ats_score >= 40:
            return {
                'category': 'Fair',
                'color': 'orange',
                'emoji': '🟠',
                'message': 'Needs improvement. Add missing keywords.'
            }
        else:
            return {
                'category': 'Poor',
                'color': 'red',
                'emoji': '🔴',
                'message': 'Major gaps detected. Optimize your CV.'
            }
    
    def to_dict(self, include_full_jd: bool = False) -> dict:
        """Convert to dictionary"""
        score_info = self.get_score_category()
        
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'application_id': self.application_id,
            'cv_filename': self.cv_filename,
            'cv_file_path': self.cv_file_path,
            'ats_score': self.ats_score,
            'score_category': score_info['category'],
            'score_color': score_info['color'],
            'score_emoji': score_info['emoji'],
            'score_message': score_info['message'],
            'matched_keywords': self.matched_keywords,
            'missing_keywords': self.missing_keywords,
            'suggestions': self.suggestions,
            'api_used': self.api_used,
            'created_at': self.created_at
        }
        
        # Include full job description only if explicitly requested
        if include_full_jd:
            result['job_description'] = self.job_description
        else:
            result['job_description_preview'] = self.job_description[:100] + '...' if len(self.job_description) > 100 else self.job_description
        
        return result