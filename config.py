import os

from dotenv import load_dotenv


load_dotenv()


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-secret-key"
    )


    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///pixelforge.db"
    )


    if DATABASE_URL.startswith(
        "postgres://"
    ):

        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql://",
            1
        )


    SQLALCHEMY_DATABASE_URI = DATABASE_URL


    SQLALCHEMY_TRACK_MODIFICATIONS = False


    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )


    MAX_CONTENT_LENGTH = (
        10 * 1024 * 1024
    )


    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        "static/uploads"
    )