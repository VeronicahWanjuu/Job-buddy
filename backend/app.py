import os
import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from backend.config import config_by_name
from backend.database.db import db

load_dotenv()

def create_app():
    """Application factory pattern"""
    env = os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name[env])
    
    # Connect database
    db_path = app.config.get("DATABASE_URL", "jobbuddy.db")
    
    # Only connect if not already connected (for testing)
    if db.connection is None:
        db.connect(db_path)
    
    # CORS - Allow multiple origins for production
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    allowed_origins = [
        frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    
    # Add production frontend URL if exists
    if "render.com" in frontend_url:
        allowed_origins.append(frontend_url)
    
    CORS(
        app,
        origins=allowed_origins,
        supports_credentials=True,
    )
    
    # Ensure upload folder exists
    upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    
    # Register Blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.onboarding import onboarding_bp
    from backend.routes.applications import applications_bp
    from backend.routes.companies import companies_bp
    from backend.routes.contacts import contacts_bp
    from backend.routes.outreach import outreach_bp
    from backend.routes.goals import goals_bp
    from backend.routes.cv_matcher import cv_matcher_bp
    from backend.routes.resources import resources_bp
    from backend.routes.coaches import coaches_bp
    from backend.routes.notifications import notifications_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(onboarding_bp, url_prefix="/api/v1/onboarding")
    app.register_blueprint(applications_bp, url_prefix="/api/v1/applications")
    app.register_blueprint(companies_bp, url_prefix="/api/v1/companies")
    app.register_blueprint(contacts_bp, url_prefix="/api/v1/contacts")
    app.register_blueprint(outreach_bp, url_prefix="/api/v1/outreach")
    app.register_blueprint(goals_bp, url_prefix="/api/v1/goals")
    app.register_blueprint(cv_matcher_bp, url_prefix="/api/v1/cv")
    app.register_blueprint(resources_bp, url_prefix="/api/v1/resources")
    app.register_blueprint(coaches_bp, url_prefix="/api/v1/coaches")
    app.register_blueprint(notifications_bp, url_prefix="/api/v1/notifications")
    
    @app.route("/health")
    def health():
        return {"status": "healthy"}
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Route not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

# Create app instance for gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)