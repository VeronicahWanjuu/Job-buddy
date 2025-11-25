from functools import wraps
from flask import request, jsonify, current_app
import jwt

def require_auth(f):
    """
    Decorator to protect routes with JWT authentication
    
    Extracts user_id from JWT token and attaches to request.user_id
    Returns 401 if token is missing, expired, or invalid
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return jsonify({"error": "No token provided"}), 401
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.replace("Bearer ", "")
            
            # Decode and verify token
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )
            
            # Attach user_id to request context
            request.user_id = payload["user_id"]
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function