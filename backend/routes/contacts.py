from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.utils.decorators import require_auth
from backend.utils.validators import validate_email

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('', methods=['GET'])
@require_auth
def get_contacts():
    """
    GET /api/v1/contacts?company_id=X
    """
    try:
        company_id = request.args.get('company_id')
        if not company_id:
            return jsonify({"error": "company_id query parameter is required"}), 400

        company = db.query_one(
            "SELECT id FROM companies WHERE id = ? AND user_id = ?",
            (company_id, request.user_id)
        )

        if not company:
            return jsonify({"error": "Company not found"}), 404

        contacts = db.query(
            """
            SELECT * FROM contacts
            WHERE company_id = ?
            ORDER BY name ASC
            """,
            (company_id,)
        )

        return jsonify(contacts), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contacts_bp.route('', methods=['POST'])
@require_auth
def create_contact():
    """
    Create a new contact for a company
    """
    try:
        data = request.get_json()

        if not data or not data.get('company_id') or not data.get('name'):
            return jsonify({"error": "company_id and name are required"}), 400

        company_id = data['company_id']
        name = data['name'].strip()
        role = data.get('role', '').strip() or None
        email = data.get('email', '').strip() or None
        linkedin_url = data.get('linkedin_url', '').strip() or None
        notes = data.get('notes', '').strip() or None

        company = db.query_one(
            "SELECT id FROM companies WHERE id = ? AND user_id = ?",
            (company_id, request.user_id)
        )
        if not company:
            return jsonify({"error": "Company not found"}), 404

        if email and not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        if email:
            existing = db.query_one(
                """
                SELECT id FROM contacts
                WHERE company_id = ? AND LOWER(email) = LOWER(?)
                """,
                (company_id, email)
            )
            if existing:
                return jsonify({"error": "Contact with this email already exists for this company"}), 400

        db.execute(
            """
            INSERT INTO contacts (company_id, name, role, email, linkedin_url, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, date('now'))
            """,
            (company_id, name, role, email, linkedin_url, notes)
        )
        db.commit()

        contact = db.query_one(
            """
            SELECT * FROM contacts
            WHERE company_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (company_id,)
        )

        return jsonify(contact), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contacts_bp.route('/<int:contact_id>', methods=['PUT'])
@require_auth
def update_contact(contact_id):
    """
    Update a contact
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        contact = db.query_one(
            """
            SELECT c.*, comp.user_id
            FROM contacts c
            JOIN companies comp ON c.company_id = comp.id
            WHERE c.id = ?
            """,
            (contact_id,)
        )

        if not contact:
            return jsonify({"error": "Contact not found"}), 404

        if contact['user_id'] != request.user_id:
            return jsonify({"error": "Unauthorized"}), 403

        updates = []
        params = []

        if 'name' in data and data['name']:
            updates.append("name = ?")
            params.append(data['name'].strip())

        if 'role' in data:
            updates.append("role = ?")
            params.append(data['role'].strip() or None)

        if 'email' in data:
            email = data['email'].strip() or None
            if email and not validate_email(email):
                return jsonify({"error": "Invalid email format"}), 400

            if email:
                existing = db.query_one(
                    """
                    SELECT id FROM contacts
                    WHERE company_id = ? AND LOWER(email) = LOWER(?) AND id != ?
                    """,
                    (contact['company_id'], email, contact_id)
                )
                if existing:
                    return jsonify({"error": "Contact with this email already exists"}), 400

            updates.append("email = ?")
            params.append(email)

        if 'linkedin_url' in data:
            updates.append("linkedin_url = ?")
            params.append(data['linkedin_url'].strip() or None)

        if 'notes' in data:
            updates.append("notes = ?")
            params.append(data['notes'].strip() or None)

        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(contact_id)

        db.execute(
            f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
        db.commit()

        updated_contact = db.query_one(
            "SELECT * FROM contacts WHERE id = ?",
            (contact_id,)
        )

        return jsonify(updated_contact), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
@require_auth
def delete_contact(contact_id):
    """
    Delete a contact
    """
    try:
        contact = db.query_one(
            """
            SELECT c.id, comp.user_id
            FROM contacts c
            JOIN companies comp ON c.company_id = comp.id
            WHERE c.id = ?
            """,
            (contact_id,)
        )

        if not contact:
            return jsonify({"error": "Contact not found"}), 404

        if contact['user_id'] != request.user_id:
            return jsonify({"error": "Unauthorized"}), 403

        db.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        db.commit()

        return jsonify({"message": "Contact deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
