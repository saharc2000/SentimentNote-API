import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort

class Auth:
    def __init__(self, config, db_manager):
        self.config = config
        self.db_manager = db_manager

    def register_user(self, username, password):
        hashed_password = generate_password_hash(password)
        user_id = self.db_manager.add_user(username, hashed_password)
        return user_id

    def login_user(self, username, password):
        user = self.db_manager.get_user_by_name(username)
        if user and check_password_hash(user.password, password):
            return self.generate_jwt(user.id)
        return None

    def authenticate(self,token):
        if not token:
            abort(401, 'Missing authorization token')

        user_id = self.decode_jwt(token)
        if not user_id:
            abort(401, 'Invalid token')
        return user_id
    
    def generate_jwt(self, user_id):
        payload = {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(seconds=self.config.JWT_EXPIRATION_DELTA)
        }
        token = jwt.encode(payload, self.config.SECRET_KEY, algorithm='HS256')
        return token

    def decode_jwt(self, token):
        try:
            payload = jwt.decode(token, self.config.SECRET_KEY, algorithms=self.config.ALGORITHM)
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            abort(401, 'Token has expired. Please log in again.')
        except jwt.InvalidTokenError:
            abort (401, 'Invalid token. Please log in again.')

