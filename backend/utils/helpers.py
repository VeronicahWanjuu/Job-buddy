import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import current_app

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password
        hashed: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def generate_token(user_id: int) -> str:
    """
    Generate JWT token for user
    
    Args:
        user_id: User ID to encode in token
        
    Returns:
        JWT token string
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(
        payload, 
        current_app.config["JWT_SECRET_KEY"], 
        algorithm="HS256"
    )