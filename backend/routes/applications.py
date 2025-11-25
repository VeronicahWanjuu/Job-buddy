from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.utils.decorators import require_auth
from backend.services.streak_service import update_user_streak
from backend.services.notification_service import (
    create_follow_up_notification,
    create_motivation_notification
)
from datetime import date, timedelta
import random

applications_bp = Blueprint('applications', __name__)

VALID_STATUSES = ['Planned', 'Applied', 'Interview', 'Offer', 'Rejected']

REJECTION_MESSAGES = [
    "Every 'no' brings you closer to your 'yes'. This rejection is just one step in your journey. Keep going! 💪",
    "Remember: companies reject candidates for many reasons that have nothing to do with your skills. Stay confident! 🌟",
    "The right opportunity is still out there. This just wasn't the right match. Keep pushing forward! 🚀",
    "Rejection is redirection. Sometimes the universe is protecting you from opportunities that aren't meant for you. ✨",
    "You've overcome challenges before, and you'll overcome this too. Use this as motivation to come back stronger! 💪"
]


# ============================================================
# GET ALL APPLICATIONS
# ============================================================
@applications_bp.route('', methods=['GET'])
@require_auth
def get_applications():
    try:
        apps = db.query(
            """
            SELECT a.*, c.name AS company_name, c.website AS company_website,
                   c.location AS company_location, c.industry AS company_industry
            FROM applications a
            JOIN companies c ON a.company_id = c.id
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC
            """,
            (request.user_id,)
        )

        grouped = {status: [] for status in VALID_STATUSES}
        for app in apps:
            if app['status'] in grouped:
                grouped[app['status']].append(app)

        return jsonify({
            "applications": apps,
            "grouped_by_status": grouped
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# CREATE APPLICATION
# ============================================================
@applications_bp.route('', methods=['POST'])
@require_auth
def create_application():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        if not data.get('company_id'):
            return jsonify({"error": "company_id is required"}), 400
        if not data.get('job_title'):
            return jsonify({"error": "job_title is required"}), 400
        if not data.get('status'):
            return jsonify({"error": "status is required"}), 400

        company_id = data['company_id']
        job_title = data['job_title'].strip()
        job_url = data.get('job_url', '').strip() or None
        status = data['status']
        notes = data.get('notes', '').strip() or None

        if status not in VALID_STATUSES:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"}), 400

        company = db.query_one(
            "SELECT id FROM companies WHERE id = ? AND user_id = ?",
            (company_id, request.user_id)
        )
        if not company:
            return jsonify({"error": "Company not found or doesn't belong to you"}), 400

        applied_date = date.today().isoformat() if status == 'Applied' else None

        db.execute(
            """
            INSERT INTO applications
            (user_id, company_id, job_title, job_url, status, notes, applied_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (request.user_id, company_id, job_title, job_url, status, notes, applied_date)
        )
        db.commit()

        app_row = db.query_one(
            """
            SELECT a.*, c.name AS company_name, c.website AS company_website
            FROM applications a
            JOIN companies c ON a.company_id = c.id
            WHERE a.user_id = ?
            ORDER BY a.id DESC
            LIMIT 1
            """,
            (request.user_id,)
        )

        if status == 'Applied':
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

            db.execute(
                """
                UPDATE goals
                SET applications_current = applications_current + 1,
                    updated_at = date('now')
                WHERE user_id = ? AND week_start = ?
                """,
                (request.user_id, week_start.isoformat())
            )
            db.commit()

            create_follow_up_notification(request.user_id, app_row['id'], days_ahead=7)
            update_user_streak(request.user_id, points=10)

        return jsonify(app_row), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# GET SINGLE APPLICATION
# ============================================================
@applications_bp.route('/<int:app_id>', methods=['GET'])
@require_auth
def get_application(app_id):
    try:
        app_row = db.query_one(
            """
            SELECT a.*, c.name AS company_name, c.website AS company_website,
                   c.location AS company_location, c.industry AS company_industry
            FROM applications a
            JOIN companies c ON a.company_id = c.id
            WHERE a.id = ? AND a.user_id = ?
            """,
            (app_id, request.user_id)
        )

        if not app_row:
            return jsonify({"error": "Application not found"}), 404

        outreach = db.query(
            """
            SELECT o.*, c.name AS contact_name, c.email AS contact_email
            FROM outreach_activities o
            LEFT JOIN contacts c ON o.contact_id = c.id
            WHERE o.application_id = ? AND o.user_id = ?
            ORDER BY o.sent_date DESC
            """,
            (app_id, request.user_id)
        )

        analyses = db.query(
            """
            SELECT id, ats_score, created_at, cv_filename
            FROM cv_analyses
            WHERE application_id = ? AND user_id = ?
            ORDER BY created_at DESC
            """,
            (app_id, request.user_id)
        )

        return jsonify({
            "application": app_row,
            "outreach": outreach,
            "cv_analyses": analyses,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# UPDATE APPLICATION
# ============================================================
@applications_bp.route('/<int:app_id>', methods=['PUT'])
@require_auth
def update_application(app_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        app_row = db.query_one(
            "SELECT * FROM applications WHERE id = ? AND user_id = ?",
            (app_id, request.user_id)
        )
        if not app_row:
            return jsonify({"error": "Application not found"}), 404

        previous_status = app_row['status']

        updates = []
        params = []

        if 'job_title' in data and data['job_title']:
            updates.append("job_title = ?")
            params.append(data['job_title'].strip())

        if 'job_url' in data:
            updates.append("job_url = ?")
            params.append(data['job_url'].strip() or None)

        if 'notes' in data:
            updates.append("notes = ?")
            params.append(data['notes'].strip() or None)

        if 'status' in data:
            new_status = data['status']
            if new_status not in VALID_STATUSES:
                return jsonify({"error": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"}), 400
            updates.append("status = ?")
            params.append(new_status)

        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(app_id)
        db.execute(
            f"UPDATE applications SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
        db.commit()

        if 'status' in data:
            new_status = data['status']

            if new_status == 'Applied' and previous_status != 'Applied':
                db.execute(
                    "UPDATE applications SET applied_date = ? WHERE id = ?",
                    (date.today().isoformat(), app_id)
                )
                db.commit()

                today = date.today()
                week_start = today - timedelta(days=today.weekday())

                db.execute(
                    """
                    UPDATE goals
                    SET applications_current = applications_current + 1,
                        updated_at = date('now')
                    WHERE user_id = ? AND week_start = ?
                    """,
                    (request.user_id, week_start.isoformat())
                )
                db.commit()

                create_follow_up_notification(request.user_id, app_id, days_ahead=7)
                update_user_streak(request.user_id, points=10)

            elif new_status == 'Rejected':
                message = random.choice(REJECTION_MESSAGES)
                create_motivation_notification(request.user_id, message)

        updated_app = db.query_one(
            """
            SELECT a.*, c.name AS company_name, c.website AS company_website
            FROM applications a
            JOIN companies c ON a.company_id = c.id
            WHERE a.id = ? AND a.user_id = ?
            """,
            (app_id, request.user_id)
        )

        return jsonify(updated_app), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# DELETE APPLICATION
# ============================================================
@applications_bp.route('/<int:app_id>', methods=['DELETE'])
@require_auth
def delete_application(app_id):
    try:
        app_row = db.query_one(
            "SELECT id FROM applications WHERE id = ? AND user_id = ?",
            (app_id, request.user_id)
        )

        if not app_row:
            return jsonify({"error": "Application not found"}), 404

        db.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        db.commit()

        return jsonify({"message": "Application deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
