# config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "this_is_a_secret_key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "your_jwt_secret_key"
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Token expiration time (1 hour)
