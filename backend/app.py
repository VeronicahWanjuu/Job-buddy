"""
JobBuddy Flask Application
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from config import config_by_name

load_dotenv()

def create_app():
    env = os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name[env])

    # Init SQLAlchemy
    db.init_app(app)

    # CORS
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    CORS(
        app,
        origins=[
            frontend_url,
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ],
        supports_credentials=True,
    )

    # Register blueprints
    from routes.auth import auth_bp
    from routes.onboarding import onboarding_bp
    from routes.applications import applications_bp
    from routes.companies import companies_bp
    from routes.contacts import contacts_bp
    from routes.outreach import outreach_bp
    from routes.goals import goals_bp
    from routes.cv import cv_bp
    from routes.resources import resources_bp
    from routes.coaches import coaches_bp
    from routes.notifications import notifications_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(onboarding_bp, url_prefix="/api/v1/onboarding")
    app.register_blueprint(applications_bp, url_prefix="/api/v1/applications")
    app.register_blueprint(companies_bp, url_prefix="/api/v1/companies")
    app.register_blueprint(contacts_bp, url_prefix="/api/v1/contacts")
    app.register_blueprint(outreach_bp, url_prefix="/api/v1/outreach")
    app.register_blueprint(goals_bp, url_prefix="/api/v1/goals")
    app.register_blueprint(cv_bp, url_prefix="/api/v1/cv")
    app.register_blueprint(resources_bp, url_prefix="/api/v1/resources")
    app.register_blueprint(coaches_bp, url_prefix="/api/v1/coaches")
    app.register_blueprint(notifications_bp, url_prefix="/api/v1/notifications")

    @app.route("/health")
    def health():
        return {"status": "healthy"}

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Route not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)