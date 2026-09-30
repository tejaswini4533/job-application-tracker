import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
UPLOAD_FOLDER = os.path.join(INSTANCE_DIR, "resumes")
DATABASE_PATH = os.path.join(INSTANCE_DIR, "job_tracker.db")

# Make sure required folders exist
os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-change-in-production"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    UPLOAD_FOLDER = UPLOAD_FOLDER

    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + DATABASE_PATH.replace("\\", "/")
    )


class ProductionConfig(Config):
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        ""
    ).replace("postgres://", "postgresql://")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}