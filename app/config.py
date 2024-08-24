import os

class Config:
    SECRET_KEY = '9d0f82b9ac1f2dc0feedd9c60d7e1aa8abb29a145da532cda3f10b184a956638'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///notes.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_DELTA = 30 * 60  # 30 minutes in seconds
    MEANINGCLOUD_API_KEY = '4cc70ff3143c73553f0d1ea072f2ac16'
    ALGORITHM = "HS256"

