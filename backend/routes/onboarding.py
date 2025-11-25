from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.utils.decorators import require_auth
from datetime import date, timedelta

onboarding_bp = Blueprint('onboarding', __name__)

VALID_FEELINGS = [
    'Excited and ready',
    'Overwhelmed but motivated',
    'Frustrated and stuck',
    'Just getting started'
]

@onboarding_bp.route('', methods=['POST'])
@require_auth
def create_onboarding():
    """
    POST /api/v1/onboarding
    
    Create onboarding data for user (protected)
    
    Request body:
        {
            "current_feeling": "Excited and ready",
            "dream_milestone": "Become a Senior Developer at FAANG",
            "weekly_application_goal": 7,
            "weekly_outreach_goal": 5,
            "companies": [
                {"name": "Google", "website": "https://google.com"},
                {"name": "Microsoft", "website": "https://microsoft.com"}
            ]
        }
    
    Returns:
        {
            "onboarding": {...},
            "goal": {...},
            "companies_created": 2
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        if not data.get('current_feeling'):
            return jsonify({"error": "current_feeling is required"}), 400
        if not data.get('dream_milestone'):
            return jsonify({"error": "dream_milestone is required"}), 400
        
        current_feeling = data['current_feeling']
        dream_milestone = data['dream_milestone'].strip()
        weekly_application_goal = data.get('weekly_application_goal', 5)
        weekly_outreach_goal = data.get('weekly_outreach_goal', 3)
        companies = data.get('companies', [])
        
        # Validate current_feeling
        if current_feeling not in VALID_FEELINGS:
            return jsonify({
                "error": f"Invalid feeling. Must be one of: {', '.join(VALID_FEELINGS)}"
            }), 400
        
        # Validate dream_milestone length
        if len(dream_milestone) < 10:
            return jsonify({"error": "dream_milestone must be at least 10 characters"}), 400
        
        # Validate goals are positive
        if weekly_application_goal < 1 or weekly_outreach_goal < 1:
            return jsonify({"error": "Goals must be positive integers"}), 400
        
        # Check if onboarding already exists
        existing = db.query_one(
            "SELECT id FROM onboarding_data WHERE user_id = ?",
            (request.user_id,)
        )
        
        if existing:
            return jsonify({"error": "Onboarding already completed"}), 400
        
        # Insert onboarding data
        db.execute(
            """
            INSERT INTO onboarding_data
            (user_id, current_feeling, dream_milestone, completed_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (request.user_id, current_feeling, dream_milestone)
        )
        db.commit()
        
        # Fetch created onboarding
        onboarding = db.query_one(
            "SELECT * FROM onboarding_data WHERE user_id = ?",
            (request.user_id,)
        )
        
        # Compute week_start (Monday of current week)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Insert initial goal row
        db.execute(
            """
            INSERT INTO goals
            (user_id, week_start, applications_goal, applications_current, 
             outreach_goal, outreach_current, created_at, updated_at)
            VALUES (?, ?, ?, 0, ?, 0, date('now'), NULL)
            """,
            (request.user_id, week_start.isoformat(), weekly_application_goal, weekly_outreach_goal)
        )
        db.commit()
        
        # Fetch created goal
        goal = db.query_one(
            "SELECT * FROM goals WHERE user_id = ? AND week_start = ?",
            (request.user_id, week_start.isoformat())
        )
        
        # Create companies
        companies_created = 0
        for company_data in companies:
            if not company_data.get('name'):
                continue
            
            name = company_data['name'].strip()
            website = company_data.get('website', '').strip() or None
            
            # Check if company already exists for this user
            existing_company = db.query_one(
                "SELECT id FROM companies WHERE user_id = ? AND LOWER(name) = LOWER(?)",
                (request.user_id, name)
            )
            
            if not existing_company:
                db.execute(
                    """
                    INSERT INTO companies (user_id, name, website, created_at)
                    VALUES (?, ?, ?, date('now'))
                    """,
                    (request.user_id, name, website)
                )
                companies_created += 1
        
        db.commit()
        
        return jsonify({
            "onboarding": onboarding,
            "goal": goal,
            "companies_created": companies_created
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@onboarding_bp.route('', methods=['GET'])
@require_auth
def get_onboarding():
    """
    GET /api/v1/onboarding
    
    Get onboarding data for current user (protected)
    
    Returns:
        {
            "completed": true,
            "current_feeling": "...",
            "dream_milestone": "...",
            "completed_at": "..."
        }
        
        OR
        
        {
            "completed": false
        }
    """
    try:
        onboarding = db.query_one(
            "SELECT * FROM onboarding_data WHERE user_id = ?",
            (request.user_id,)
        )
        
        if not onboarding:
            return jsonify({"completed": False}), 200
        
        return jsonify({
            "completed": True,
            "id": onboarding['id'],
            "current_feeling": onboarding['current_feeling'],
            "dream_milestone": onboarding['dream_milestone'],
            "completed_at": onboarding['completed_at']
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500