from functools import wraps
from flask import request, jsonify, current_app
import jwt

def require_auth(f):
    """
    Decorator to require authentication for a route.
    Validates JWT token from Authorization header and sets request.user_id
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        try:
            # Extract token (format: "Bearer <token>")
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            
            # Decode JWT token - USE THE SAME KEY AS generate_token
            secret_key = current_app.config.get("JWT_SECRET_KEY")
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Store user_id in request object for access in route
            request.user_id = payload['user_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except (KeyError, IndexError):
            return jsonify({'error': 'Invalid token format'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    """
    Decorator for optional authentication.
    If token is provided and valid, sets request.user_id
    If no token or invalid token, request.user_id will not be set
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
                secret_key = current_app.config.get("JWT_SECRET_KEY")
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                request.user_id = payload.get('user_id')
            except:
                pass  # Silently fail for optional auth
        
        return f(*args, **kwargs)
    
    return decorated_function