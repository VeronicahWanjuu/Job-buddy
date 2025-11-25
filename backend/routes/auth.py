from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.models.user import User
from backend.models.streak import Streak
from backend.models.onboardingData import OnboardingData
from backend.utils.decorators import require_auth
from backend.utils.helpers import hash_password, verify_password, generate_token
from backend.utils.validators import validate_email
import re

auth_bp = Blueprint('auth', __name__)

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets strength requirements
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/v1/auth/register
    
    Register a new user
    
    Request body:
        {
            "email": "user@example.com",
            "password": "Password123!",
            "name": "John Doe"
        }
    
    Returns:
        {
            "user": {"id": 1, "email": "...", "name": "..."},
            "token": "jwt_token_here"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({"error": "Email, password, and name are required"}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        name = data['name'].strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Check if user already exists
        existing = db.query_one(
            "SELECT id FROM users WHERE LOWER(email) = LOWER(?)",
            (email,)
        )
        
        if existing:
            return jsonify({"error": "User with this email already exists"}), 400
        
        # Hash password
        hashed_pw = hash_password(password)
        
        # Insert user
        db.execute(
            """
            INSERT INTO users (email, password_hash, name, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (email, hashed_pw, name)
        )
        db.commit()
        
        # Fetch created user
        user = db.query_one(
            "SELECT id, email, name, created_at FROM users WHERE email = ?",
            (email,)
        )
        
        # Create initial streak row (trigger should handle this, but ensure it exists)
        streak_exists = db.query_one(
            "SELECT id FROM streaks WHERE user_id = ?",
            (user['id'],)
        )
        
        if not streak_exists:
            db.execute(
                """
                INSERT INTO streaks (user_id, current_streak, longest_streak, last_activity_date, total_points)
                VALUES (?, 0, 0, NULL, 0)
                """,
                (user['id'],)
            )
            db.commit()
        
        # Generate JWT token
        token = generate_token(user['id'])
        
        return jsonify({
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name']
            },
            "token": token
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/v1/auth/login
    
    Login user
    
    Request body:
        {
            "email": "user@example.com",
            "password": "Password123!"
        }
    
    Returns:
        {
            "user": {"id": 1, "email": "...", "name": "..."},
            "token": "jwt_token_here",
            "has_completed_onboarding": true/false
        }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Fetch user by email
        user = db.query_one(
            "SELECT id, email, name, password_hash FROM users WHERE LOWER(email) = LOWER(?)",
            (email,)
        )
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Update last_login
        db.execute(
            "UPDATE users SET last_login = datetime('now') WHERE id = ?",
            (user['id'],)
        )
        db.commit()
        
        # Check onboarding status
        onboarding = db.query_one(
            "SELECT id FROM onboarding_data WHERE user_id = ?",
            (user['id'],)
        )
        has_onboarding = onboarding is not None
        
        # Generate JWT token
        token = generate_token(user['id'])
        
        return jsonify({
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name']
            },
            "token": token,
            "has_completed_onboarding": has_onboarding
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """
    GET /api/v1/auth/profile
    
    Get current user profile (protected)
    
    Returns:
        {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe",
            "created_at": "2025-01-15T10:00:00",
            "is_active": true,
            "email_notifications_enabled": true
        }
    """
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

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """
    PUT /api/v1/auth/profile
    
    Update current user profile (protected)
    
    Request body:
        {
            "name": "New Name",
            "email": "newemail@example.com",
            "email_notifications_enabled": true
        }
    
    Returns:
        Updated user object
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Fetch current user
        user = db.query_one(
            "SELECT id, email FROM users WHERE id = ?",
            (request.user_id,)
        )
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Build update query dynamically
        updates = []
        params = []
        
        if 'name' in data and data['name']:
            updates.append("name = ?")
            params.append(data['name'].strip())
        
        if 'email' in data and data['email']:
            new_email = data['email'].strip().lower()
            if not validate_email(new_email):
                return jsonify({"error": "Invalid email format"}), 400
            
            # Check if email already taken by another user
            existing = db.query_one(
                "SELECT id FROM users WHERE LOWER(email) = LOWER(?) AND id != ?",
                (new_email, request.user_id)
            )
            if existing:
                return jsonify({"error": "Email already in use"}), 400
            
            updates.append("email = ?")
            params.append(new_email)
        
        if 'email_notifications_enabled' in data:
            updates.append("email_notifications_enabled = ?")
            params.append(1 if data['email_notifications_enabled'] else 0)
        
        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400
        
        # Execute update
        params.append(request.user_id)
        db.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
        db.commit()
        
        # Fetch updated user
        updated_user = db.query_one(
            """
            SELECT id, email, name, created_at, last_login, is_active, 
                   email_notifications_enabled, notification_preferences
            FROM users 
            WHERE id = ?
            """,
            (request.user_id,)
        )
        
        return jsonify(updated_user), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/profile', methods=['DELETE'])
@require_auth
def delete_profile():
    """
    DELETE /api/v1/auth/profile
    
    Delete current user account (protected)
    
    Returns:
        {"message": "Account deleted successfully"}
    """
    try:
        # Fetch user to ensure they exist
        user = db.query_one(
            "SELECT id FROM users WHERE id = ?",
            (request.user_id,)
        )
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Delete user (CASCADE will handle related records)
        db.execute(
            "DELETE FROM users WHERE id = ?",
            (request.user_id,)
        )
        db.commit()
        
        return jsonify({"message": "Account deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500