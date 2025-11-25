from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.utils.decorators import require_auth

companies_bp = Blueprint('companies', __name__)

@companies_bp.route('', methods=['GET'])
@require_auth
def get_companies():
    """
    GET /api/v1/companies
    Query: ?industry=Technology
    """
    try:
        industry = request.args.get('industry')

        if industry:
            companies = db.query(
                """
                SELECT * FROM companies
                WHERE user_id = ? AND industry = ?
                ORDER BY created_at DESC
                """,
                (request.user_id, industry)
            )
        else:
            companies = db.query(
                """
                SELECT * FROM companies
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (request.user_id,)
            )

        return jsonify(companies), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@companies_bp.route('', methods=['POST'])
@require_auth
def create_company():
    """
    POST /api/v1/companies
    Create company
    """
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({"error": "Company name is required"}), 400

        name = data['name'].strip()
        website = data.get('website', '').strip() or None
        location = data.get('location', '').strip() or None
        industry = data.get('industry', '').strip() or None
        notes = data.get('notes', '').strip() or None

        if len(name) < 2:
            return jsonify({"error": "Company name must be at least 2 characters"}), 400

        # Prevent duplicate names
        existing = db.query_one(
            """
            SELECT id FROM companies
            WHERE user_id = ? AND LOWER(name) = LOWER(?)
            """,
            (request.user_id, name)
        )
        if existing:
            return jsonify({"error": "Company with this name already exists"}), 400

        db.execute(
            """
            INSERT INTO companies (user_id, name, website, location, industry, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, date('now'))
            """,
            (request.user_id, name, website, location, industry, notes)
        )
        db.commit()

        company = db.query_one(
            """
            SELECT * FROM companies
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (request.user_id,)
        )

        return jsonify(company), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@companies_bp.route('/<int:company_id>', methods=['GET'])
@require_auth
def get_company(company_id):
    """
    GET /api/v1/companies/<id>
    Returns company + applications + contacts
    """
    try:
        company = db.query_one(
            "SELECT * FROM companies WHERE id = ? AND user_id = ?",
            (company_id, request.user_id)
        )

        if not company:
            return jsonify({"error": "Company not found"}), 404

        applications = db.query(
            """
            SELECT id, job_title, status, applied_date, created_at
            FROM applications
            WHERE company_id = ? AND user_id = ?
            ORDER BY created_at DESC
            """,
            (company_id, request.user_id)
        )

        contacts = db.query(
            """
            SELECT * FROM contacts
            WHERE company_id = ?
            ORDER BY name ASC
            """,
            (company_id,)
        )

        return jsonify({
            "company": company,
            "applications": applications,
            "contacts": contacts
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@companies_bp.route('/<int:company_id>', methods=['PUT'])
@require_auth
def update_company(company_id):
    """
    Update company fields
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        company = db.query_one(
            "SELECT * FROM companies WHERE id = ? AND user_id = ?",
            (company_id, request.user_id)
        )

        if not company:
            return jsonify({"error": "Company not found"}), 404

        updates = []
        params = []

        if 'name' in data and data['name']:
            name = data['name'].strip()
            if len(name) < 2:
                return jsonify({"error": "Company name must be at least 2 characters"}), 400

            existing = db.query_one(
                """
                SELECT id FROM companies
                WHERE user_id = ? AND LOWER(name) = LOWER(?) AND id != ?
                """,
                (request.user_id, name, company_id)
            )
            if existing:
                return jsonify({"error": "Company with this name already exists"}), 400

            updates.append("name = ?")
            params.append(name)

        if 'website' in data:
            updates.append("website = ?")
            params.append(data['website'].strip() or None)

        if 'location' in data:
            updates.append("location = ?")
            params.append(data['location'].strip() or None)

        if 'industry' in data:
            updates.append("industry = ?")
            params.append(data['industry'].strip() or None)

        if 'notes' in data:
            updates.append("notes = ?")
            params.append(data['notes'].strip() or None)

        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(company_id)

        db.execute(
            f"UPDATE companies SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
        db.commit()

        updated_company = db.query_one(
            "SELECT * FROM companies WHERE id = ?",
            (company_id,)
        )

        return jsonify(updated_company), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@companies_bp.route('/<int:company_id>', methods=['DELETE'])
@require_auth
def delete_company(company_id):
    """
    Delete company (cascade removes contacts + applications)
    """
    try:
        company = db.query_one(
            "SELECT id FROM companies WHERE id = ? AND user_id = ?",
            (company_id, request.user_id)
        )

        if not company:
            return jsonify({"error": "Company not found"}), 404

        db.execute("DELETE FROM companies WHERE id = ?", (company_id,))
        db.commit()

        return jsonify({"message": "Company deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
