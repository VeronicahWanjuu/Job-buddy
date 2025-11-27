from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.utils.decorators import require_auth
from backend.utils.validators import validate_date
from backend.services.streak_service import update_user_streak
from backend.services.notification_service import create_follow_up_notification
from datetime import date, timedelta
import json
import os

outreach_bp = Blueprint('outreach', __name__)

VALID_CHANNELS = ['email', 'linkedin']

@outreach_bp.route('/templates/generate', methods=['POST'])
@require_auth
def generate_template():
    """
    POST /api/v1/outreach/templates/generate
    
    Generate personalized outreach template (protected)
    
    Request body:
        {
            "contact_id": 1,
            "company_id": 1,
            "application_id": 2,  # optional
            "template_type": "cold_outreach"
        }
    
    Returns:
        {
            "subject": "...",
            "body": "...",
            "editing_tips": "..."
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        contact_id = data.get('contact_id')
        company_id = data.get('company_id')
        application_id = data.get('application_id')
        template_type = data.get('template_type', 'cold_outreach')
        
        if not contact_id or not company_id:
            return jsonify({"error": "contact_id and company_id are required"}), 400
        
        # Fetch contact
        contact = db.query_one(
            """
            SELECT c.*, comp.user_id
            FROM contacts c
            JOIN companies comp ON c.company_id = comp.id
            WHERE c.id = ?
            """,
            (contact_id,)
        )
        
        if not contact or contact['user_id'] != request.user_id:
            return jsonify({"error": "Contact not found"}), 404
        
        # Fetch company
        company = db.query_one(
            "SELECT * FROM companies WHERE id = ? AND user_id = ?",
            (company_id, request.user_id)
        )
        
        if not company:
            return jsonify({"error": "Company not found"}), 404
        
        # Fetch user
        user = db.query_one(
            "SELECT * FROM users WHERE id = ?",
            (request.user_id,)
        )
        
        # Fetch onboarding data for dream_milestone
        onboarding = db.query_one(
            "SELECT dream_milestone FROM onboarding_data WHERE user_id = ?",
            (request.user_id,)
        )
        
        dream_milestone = onboarding['dream_milestone'] if onboarding else "achieving my career goals"
        
        # Fetch application if provided
        application = None
        if application_id:
            application = db.query_one(
                "SELECT * FROM applications WHERE id = ? AND user_id = ?",
                (application_id, request.user_id)
            )
        
        # Load templates
        templates_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'templates.json')
        with open(templates_path, 'r') as f:
            templates_data = json.load(f)
        
        # Find template
        template = None
        for t in templates_data['templates']:
            if t['type'] == template_type:
                template = t
                break
        
        if not template:
            return jsonify({"error": "Template not found"}), 404
        
        # Replace tokens
        subject = template['subject']
        body = template['body']
        
        replacements = {
            '{contact_name}': contact['name'] or 'there',
            '{company_name}': company['name'],
            '{user_name}': user['name'],
            '{dream_milestone}': dream_milestone,
            '{industry}': company['industry'] or 'your industry',
            '{job_title}': application['job_title'] if application else 'the position',
            '{applied_date}': application['applied_date'] if application else 'recently'
        }
        
        for token, value in replacements.items():
            subject = subject.replace(token, value)
            body = body.replace(token, value)
        
        return jsonify({
            "subject": subject,
            "body": body,
            "editing_tips": template.get('editing_tips', '')
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@outreach_bp.route('', methods=['POST'])
@require_auth
def create_outreach():
    """
    POST /api/v1/outreach
    
    Create outreach activity (protected)
    
    Request body:
        {
            "application_id": 1,  # OR company_id (exactly one required)
            "company_id": 1,
            "contact_id": 1,
            "channel": "email",
            "message": "...",
            "sent_date": "2025-01-15",
            "follow_up_date": "2025-01-22"  # optional
        }
    
    Returns:
        Created outreach object
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        application_id = data.get('application_id')
        company_id = data.get('company_id')
        contact_id = data.get('contact_id')
        channel = data.get('channel')
        message = data.get('message', '').strip()
        sent_date = data.get('sent_date')
        follow_up_date = data.get('follow_up_date')
        
        # Validate required fields
        if not contact_id:
            return jsonify({"error": "contact_id is required"}), 400
        if not channel:
            return jsonify({"error": "channel is required"}), 400
        if not message:
            return jsonify({"error": "message is required"}), 400
        if not sent_date:
            return jsonify({"error": "sent_date is required"}), 400
        
        # Validate XOR: exactly one of application_id or company_id
        if (application_id is None and company_id is None) or \
           (application_id is not None and company_id is not None):
            return jsonify({
                "error": "Must provide exactly ONE of application_id or company_id"
            }), 400
        
        # Validate channel
        if channel not in VALID_CHANNELS:
            return jsonify({
                "error": f"Invalid channel. Must be one of: {', '.join(VALID_CHANNELS)}"
            }), 400
        
        # Validate dates
        if not validate_date(sent_date):
            return jsonify({"error": "Invalid sent_date format. Use YYYY-MM-DD"}), 400
        
        if follow_up_date and not validate_date(follow_up_date):
            return jsonify({"error": "Invalid follow_up_date format. Use YYYY-MM-DD"}), 400
        
        # Validate message length
        if len(message) < 10:
            return jsonify({"error": "Message must be at least 10 characters"}), 400
        
        # Verify contact belongs to user
        contact = db.query_one(
            """
            SELECT c.id, comp.user_id
            FROM contacts c
            JOIN companies comp ON c.company_id = comp.id
            WHERE c.id = ?
            """,
            (contact_id,)
        )
        
        if not contact or contact['user_id'] != request.user_id:
            return jsonify({"error": "Contact not found"}), 404
        
        # Verify application or company belongs to user
        if application_id:
            app = db.query_one(
                "SELECT id FROM applications WHERE id = ? AND user_id = ?",
                (application_id, request.user_id)
            )
            if not app:
                return jsonify({"error": "Application not found"}), 404
        
        if company_id:
            comp = db.query_one(
                "SELECT id FROM companies WHERE id = ? AND user_id = ?",
                (company_id, request.user_id)
            )
            if not comp:
                return jsonify({"error": "Company not found"}), 404
        
        # Insert outreach
        db.execute(
            """
            INSERT INTO outreach_activities
            (user_id, application_id, company_id, contact_id, channel, 
             message_template, sent_date, follow_up_date, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Sent', datetime('now'))
            """,
            (request.user_id, application_id, company_id, contact_id, 
             channel, message, sent_date, follow_up_date)
        )
        db.commit()
        
        # Fetch created outreach
        outreach = db.query_one(
            """
            SELECT o.*, c.name AS contact_name, c.email AS contact_email
            FROM outreach_activities o
            LEFT JOIN contacts c ON o.contact_id = c.id
            WHERE o.user_id = ?
            ORDER BY o.id DESC
            LIMIT 1
            """,
            (request.user_id,)
        )
        
        # Update goal for current week
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        db.execute(
            """
            UPDATE goals
            SET outreach_current = outreach_current + 1,
                updated_at = date('now')
            WHERE user_id = ? AND week_start = ?
            """,
            (request.user_id, week_start.isoformat())
        )
        db.commit()
        
        # Update streak
        update_user_streak(request.user_id, points=10)
        
        # Create follow-up notification if follow_up_date provided
        if follow_up_date and application_id:
            # Calculate days until follow-up
            follow_date = date.fromisoformat(follow_up_date)
            days_ahead = (follow_date - date.today()).days
            if days_ahead > 0:
                create_follow_up_notification(request.user_id, application_id, days_ahead)
        
        return jsonify(outreach), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@outreach_bp.route('', methods=['GET'])
@require_auth
def get_outreach():
    """
    GET /api/v1/outreach
    
    Get outreach activities (protected)
    
    Query params:
        - application_id: Filter by application
        - company_id: Filter by company
    
    Returns:
        [{"id": 1, "channel": "email", ...}, ...]
    """
    try:
        application_id = request.args.get('application_id')
        company_id = request.args.get('company_id')
        
        if application_id:
            outreach_list = db.query(
                """
                SELECT o.*, c.name AS contact_name, c.email AS contact_email,
                       comp.name AS company_name
                FROM outreach_activities o
                LEFT JOIN contacts c ON o.contact_id = c.id
                LEFT JOIN companies comp ON o.company_id = comp.id
                WHERE o.user_id = ? AND o.application_id = ?
                ORDER BY o.sent_date DESC
                """,
                (request.user_id, application_id)
            )
        elif company_id:
            outreach_list = db.query(
                """
                SELECT o.*, c.name AS contact_name, c.email AS contact_email,
                       comp.name AS company_name
                FROM outreach_activities o
                LEFT JOIN contacts c ON o.contact_id = c.id
                LEFT JOIN companies comp ON o.company_id = comp.id
                WHERE o.user_id = ? AND o.company_id = ?
                ORDER BY o.sent_date DESC
                """,
                (request.user_id, company_id)
            )
        else:
            outreach_list = db.query(
                """
                SELECT o.*, c.name AS contact_name, c.email AS contact_email,
                       comp.name AS company_name
                FROM outreach_activities o
                LEFT JOIN contacts c ON o.contact_id = c.id
                LEFT JOIN companies comp ON o.company_id = comp.id OR o.application_id IN (
                    SELECT id FROM applications WHERE company_id = comp.id
                )
                WHERE o.user_id = ?
                ORDER BY o.sent_date DESC
                """,
                (request.user_id,)
            )
        
        return jsonify(outreach_list), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@outreach_bp.route('/<int:outreach_id>', methods=['PUT'])
@require_auth
def update_outreach(outreach_id):
    """
    PUT /api/v1/outreach/<id>
    
    Update outreach status (protected)
    
    Request body:
        {
            "status": "Responded"
        }
    
    Returns:
        Updated outreach object
    """
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({"error": "status is required"}), 400
        
        status = data['status']
        
        if status not in ['Sent', 'Responded', 'No Response']:
            return jsonify({"error": "Invalid status"}), 400
        
        # Verify outreach belongs to user
        outreach = db.query_one(
            "SELECT id FROM outreach_activities WHERE id = ? AND user_id = ?",
            (outreach_id, request.user_id)
        )
        
        if not outreach:
            return jsonify({"error": "Outreach not found"}), 404
        
        # Update status
        db.execute(
            "UPDATE outreach_activities SET status = ? WHERE id = ?",
            (status, outreach_id)
        )
        db.commit()
        
        updated = db.query_one(
            """
            SELECT o.*, c.name AS contact_name, c.email AS contact_email
            FROM outreach_activities o
            LEFT JOIN contacts c ON o.contact_id = c.id
            WHERE o.id = ?
            """,
            (outreach_id,)
        )
        
        return jsonify(updated), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500