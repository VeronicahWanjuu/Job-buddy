from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.utils.decorators import require_auth
from backend.utils.helpers import hash_password, verify_password, generate_token
from backend.utils.validators import validate_email
import re

auth_bp = Blueprint('auth', __name__)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, ""
    

# ----------------------------------------------------
# REGISTER
# ----------------------------------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if not data or not data.get("email") or not data.get("password") or not data.get("name"):
            return jsonify({"error": "Email, password, and name are required"}), 400

        email = data["email"].strip().lower()
        password = data["password"]
        name = data["name"].strip()

        # Validate email format
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password
        valid, msg = validate_password_strength(password)
        if not valid:
            return jsonify({"error": msg}), 400

        # Check duplicate user
        exists = db.query_one(
            "SELECT id FROM users WHERE LOWER(email) = LOWER(?)",
            (email,)
        )
        if exists:
            return jsonify({"error": "User with this email already exists"}), 400

        # Hash password
        hashed_pw = hash_password(password)

        # Insert user (DATABASE TRIGGER will auto-create streak)
        db.execute(
            """
            INSERT INTO users (email, password_hash, name, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (email, hashed_pw, name)
        )
        db.commit()

        # Fetch new user
        user = db.query_one(
            "SELECT id, email, name, created_at FROM users WHERE email = ?",
            (email,)
        )

        if not user:
            return jsonify({"error": "User creation failed"}), 500

        # Generate token
        token = generate_token(user["id"])

        return jsonify({
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"]
            },
            "token": token
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# LOGIN
# ----------------------------------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password are required"}), 400

        email = data["email"].strip().lower()
        password = data["password"]

        # Fetch user
        user = db.query_one(
            "SELECT id, email, name, password_hash FROM users WHERE LOWER(email) = LOWER(?)",
            (email,)
        )

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        # Verify password
        if not verify_password(password, user["password_hash"]):
            return jsonify({"error": "Invalid email or password"}), 401

        # Update last login
        db.execute(
            "UPDATE users SET last_login = datetime('now') WHERE id = ?",
            (user["id"],)
        )
        db.commit()

        # Check onboarding status
        onboarding_done = db.query_one(
            "SELECT id FROM onboarding_data WHERE user_id = ?",
            (user["id"],)
        ) is not None

        # Generate token
        token = generate_token(user["id"])

        return jsonify({
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"]
            },
            "token": token,
            "has_completed_onboarding": onboarding_done
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# GET PROFILE
# ----------------------------------------------------
@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    try:
        user = db.query_one(
            """
            SELECT id, email, name, created_at, last_login, is_active,
                   email_notifications_enabled, notification_preferences
            FROM users
            WHERE id = ?
            """,
            (request.user_id,)
        )

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(user), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# UPDATE PROFILE
# ----------------------------------------------------
@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        user = db.query_one(
            "SELECT id, email FROM users WHERE id = ?",
            (request.user_id,)
        )

        if not user:
            return jsonify({"error": "User not found"}), 404

        updates = []
        params = []

        if "name" in data and data["name"]:
            updates.append("name = ?")
            params.append(data["name"].strip())

        if "email" in data and data["email"]:
            new_email = data["email"].strip().lower()

            if not validate_email(new_email):
                return jsonify({"error": "Invalid email format"}), 400

            # Check if email taken
            exists = db.query_one(
                "SELECT id FROM users WHERE LOWER(email) = LOWER(?) AND id != ?",
                (new_email, request.user_id)
            )
            if exists:
                return jsonify({"error": "Email already in use"}), 400

            updates.append("email = ?")
            params.append(new_email)

        if "email_notifications_enabled" in data:
            updates.append("email_notifications_enabled = ?")
            params.append(1 if data["email_notifications_enabled"] else 0)

        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(request.user_id)

        db.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
        db.commit()

        updated = db.query_one(
            """
            SELECT id, email, name, created_at, last_login, is_active,
                   email_notifications_enabled, notification_preferences
            FROM users WHERE id = ?
            """,
            (request.user_id,)
        )

        return jsonify(updated), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# DELETE PROFILE
# ----------------------------------------------------
@auth_bp.route('/profile', methods=['DELETE'])
@require_auth
def delete_profile():
    try:
        user = db.query_one(
            "SELECT id FROM users WHERE id = ?",
            (request.user_id,)
        )

        if not user:
            return jsonify({"error": "User not found"}), 404

        db.execute(
            "DELETE FROM users WHERE id = ?",
            (request.user_id,)
        )
        db.commit()

        return jsonify({"message": "Account deleted successfully"}), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500