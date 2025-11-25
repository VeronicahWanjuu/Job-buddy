from flask import Blueprint, request, jsonify, current_app
from backend.database.db import db
from backend.utils.decorators import require_auth
from werkzeug.utils import secure_filename
import os
import PyPDF2
import docx
import json
import re
from datetime import datetime

cv_matcher_bp = Blueprint('cv_matcher', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")

def normalize_text(text):
    """Normalize text: lowercase, remove extra spaces and punctuation"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_keywords(text):
    """Extract skills and keywords from text"""
    # Common technical skills
    technical_skills = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'react', 'angular', 'vue', 'node.js', 'nodejs', 'express', 'django', 'flask', 'spring',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'jenkins', 'git', 'github',
        'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
        'machine learning', 'deep learning', 'ai', 'data science', 'tensorflow', 'pytorch',
        'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'ci/cd', 'devops',
        'html', 'css', 'sass', 'webpack', 'babel', 'npm', 'yarn',
        'unit testing', 'integration testing', 'test driven development', 'tdd'
    ]
    
    # Soft skills
    soft_skills = [
        'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
        'critical thinking', 'time management', 'collaboration', 'adaptability',
        'presentation', 'mentoring', 'project management'
    ]
    
    all_skills = technical_skills + soft_skills
    normalized_text = normalize_text(text)
    
    found_keywords = []
    for skill in all_skills:
        if skill in normalized_text:
            found_keywords.append(skill)
    
    return list(set(found_keywords))  # Remove duplicates

def calculate_ats_score(cv_keywords, jd_keywords):
    """Calculate ATS score based on keyword matching"""
    if not jd_keywords:
        return 0
    
    matched = set(cv_keywords) & set(jd_keywords)
    score = (len(matched) / len(jd_keywords)) * 100
    return min(int(score), 100)  # Cap at 100

def generate_suggestions(matched_keywords, missing_keywords):
    """Generate improvement suggestions"""
    suggestions = []
    
    if len(missing_keywords) > 0:
        suggestions.append({
            "category": "Missing Keywords",
            "suggestion": f"Add these keywords to your CV: {', '.join(missing_keywords[:5])}"
        })
    
    if len(matched_keywords) < 5:
        suggestions.append({
            "category": "Keyword Density",
            "suggestion": "Include more relevant technical skills and tools mentioned in the job description."
        })
    
    suggestions.append({
        "category": "Formatting",
        "suggestion": "Use clear section headers like 'Skills', 'Experience', 'Education' to help ATS systems parse your CV."
    })
    
    suggestions.append({
        "category": "Quantify Achievements",
        "suggestion": "Add metrics and numbers to your achievements (e.g., 'Improved performance by 40%')."
    })
    
    return suggestions


@cv_matcher_bp.route('/analyze', methods=['POST'])
@require_auth
def analyze_cv():
    """
    POST /api/v1/cv/analyze
    
    Analyze CV against job description (protected)
    
    Form data:
        - cv_file: PDF or DOCX file (required)
        - jd_text: Job description text (optional if jd_file provided)
        - jd_file: Job description file (optional if jd_text provided)
        - application_id: Link to application (optional)
    
    Returns:
        {
            "analysis_id": 1,
            "ats_score": 75,
            "matched_keywords": [...],
            "missing_keywords": [...],
            "suggestions": [...],
            "cv_file_path": "..."
        }
    """
    try:
        # Check if CV file is present
        if 'cv_file' not in request.files:
            return jsonify({"error": "cv_file is required"}), 400
        
        cv_file = request.files['cv_file']
        
        if cv_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(cv_file.filename):
            return jsonify({"error": "Invalid file type. Only PDF and DOCX allowed"}), 400
        
        # Check file size
        cv_file.seek(0, os.SEEK_END)
        file_size = cv_file.tell()
        cv_file.seek(0)
        
        max_size = current_app.config['MAX_CONTENT_LENGTH']
        if file_size > max_size:
            return jsonify({"error": f"File too large. Maximum size is {max_size // (1024*1024)}MB"}), 400
        
        # Get job description
        jd_text = request.form.get('jd_text', '').strip()
        jd_file = request.files.get('jd_file')
        application_id = request.form.get('application_id')
        
        if not jd_text and not jd_file:
            return jsonify({"error": "Either jd_text or jd_file is required"}), 400
        
        # Verify application if provided
        if application_id:
            app = db.query_one(
                "SELECT id FROM applications WHERE id = ? AND user_id = ?",
                (application_id, request.user_id)
            )
            if not app:
                return jsonify({"error": "Application not found"}), 404
        
        # Save CV file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = secure_filename(cv_file.filename)
        filename = f"{request.user_id}_{timestamp}_{original_filename}"
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        cv_file_path = os.path.join(upload_folder, filename)
        cv_file.save(cv_file_path)
        
        # Extract text from CV
        try:
            if cv_file_path.endswith('.pdf'):
                cv_text = extract_text_from_pdf(cv_file_path)
            elif cv_file_path.endswith('.docx') or cv_file_path.endswith('.doc'):
                cv_text = extract_text_from_docx(cv_file_path)
            else:
                return jsonify({"error": "Unsupported file format"}), 400
        except Exception as e:
            # Clean up file
            if os.path.exists(cv_file_path):
                os.remove(cv_file_path)
            return jsonify({"error": f"Failed to extract text from CV: {str(e)}"}), 500
        
        # Extract text from JD
        if jd_file and jd_file.filename:
            # Save temporarily
            jd_temp_path = os.path.join(upload_folder, f"temp_jd_{timestamp}.txt")
            jd_file.save(jd_temp_path)
            
            try:
                if jd_temp_path.endswith('.pdf'):
                    jd_text = extract_text_from_pdf(jd_temp_path)
                elif jd_temp_path.endswith('.docx') or jd_temp_path.endswith('.doc'):
                    jd_text = extract_text_from_docx(jd_temp_path)
                else:
                    with open(jd_temp_path, 'r', encoding='utf-8') as f:
                        jd_text = f.read()
            finally:
                # Clean up temp file
                if os.path.exists(jd_temp_path):
                    os.remove(jd_temp_path)
        
        if not jd_text or len(jd_text.strip()) < 50:
            if os.path.exists(cv_file_path):
                os.remove(cv_file_path)
            return jsonify({"error": "Job description is too short (minimum 50 characters)"}), 400
        
        # Extract keywords
        cv_keywords = extract_keywords(cv_text)
        jd_keywords = extract_keywords(jd_text)
        
        # Calculate matched and missing keywords
        matched_keywords = list(set(cv_keywords) & set(jd_keywords))
        missing_keywords = list(set(jd_keywords) - set(cv_keywords))
        
        # Calculate ATS score
        ats_score = calculate_ats_score(cv_keywords, jd_keywords)
        
        # Generate suggestions
        suggestions = generate_suggestions(matched_keywords, missing_keywords)
        
        # Insert into database
        db.execute(
            """
            INSERT INTO cv_analyses
            (user_id, application_id, cv_filename, cv_file_path, job_description,
             ats_score, matched_keywords, missing_keywords, suggestions, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                request.user_id,
                application_id if application_id else None,
                original_filename,
                cv_file_path,
                jd_text,
                ats_score,
                json.dumps(matched_keywords),
                json.dumps(missing_keywords),
                json.dumps(suggestions)
            )
        )
        db.commit()
        
        # Fetch created analysis
        analysis = db.query_one(
            """
            SELECT id, ats_score, matched_keywords, missing_keywords, suggestions, 
                   cv_filename, cv_file_path, created_at
            FROM cv_analyses
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (request.user_id,)
        )
        
        # Parse JSON fields
        result = dict(analysis)
        result['matched_keywords'] = json.loads(result['matched_keywords']) if result['matched_keywords'] else []
        result['missing_keywords'] = json.loads(result['missing_keywords']) if result['missing_keywords'] else []
        result['suggestions'] = json.loads(result['suggestions']) if result['suggestions'] else []
        
        return jsonify({
            "analysis_id": result['id'],
            "ats_score": result['ats_score'],
            "matched_keywords": result['matched_keywords'],
            "missing_keywords": result['missing_keywords'],
            "suggestions": result['suggestions'],
            "cv_filename": result['cv_filename'],
            "cv_file_path": result['cv_file_path'],
            "created_at": result['created_at']
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cv_matcher_bp.route('/history', methods=['GET'])
@require_auth
def get_cv_history():
    """
    GET /api/v1/cv/history
    
    Get CV analysis history (protected)
    
    Returns:
        [
            {
                "id": 1,
                "ats_score": 75,
                "cv_filename": "resume.pdf",
                "created_at": "2025-01-15T10:00:00",
                "application_id": 2
            },
            ...
        ]
    """
    try:
        analyses = db.query(
            """
            SELECT id, ats_score, cv_filename, created_at, application_id
            FROM cv_analyses
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (request.user_id,)
        )
        
        return jsonify(analyses), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cv_matcher_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
@require_auth
def get_cv_analysis(analysis_id):
    """
    GET /api/v1/cv/analysis/<id>
    
    Get single CV analysis details (protected)
    
    Returns:
        {
            "id": 1,
            "ats_score": 75,
            "matched_keywords": [...],
            "missing_keywords": [...],
            "suggestions": [...],
            "cv_filename": "...",
            "job_description": "...",
            "created_at": "..."
        }
    """
    try:
        analysis = db.query_one(
            """
            SELECT *
            FROM cv_analyses
            WHERE id = ? AND user_id = ?
            """,
            (analysis_id, request.user_id)
        )
        
        if not analysis:
            return jsonify({"error": "Analysis not found"}), 404
        
        # Parse JSON fields
        result = dict(analysis)
        result['matched_keywords'] = json.loads(result['matched_keywords']) if result['matched_keywords'] else []
        result['missing_keywords'] = json.loads(result['missing_keywords']) if result['missing_keywords'] else []
        result['suggestions'] = json.loads(result['suggestions']) if result['suggestions'] else []
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500