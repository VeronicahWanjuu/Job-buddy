import os

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    
    # Database URL/path used by backend/database/db.py
    DATABASE_URL = os.getenv("DATABASE_URL", "backend/test_models.db")
    
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "backend/uploads/cvs")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_FILE_SIZE_MB", "5")) * 1024 * 1024
    
    ATS_SCORE_THRESHOLD = int(os.getenv("ATS_SCORE_THRESHOLD", "60"))

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False
    DATABASE_URL = os.getenv("DATABASE_URL", "backend/jobbuddy.db")

class TestingConfig(BaseConfig):
    TESTING = True
    DATABASE_URL = ":memory:"
    DEBUG = True

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}