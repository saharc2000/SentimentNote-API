from flask import Flask, request, jsonify, abort
from flasgger import Swagger, swag_from
from flask_swagger_ui import get_swaggerui_blueprint
from .config import Config  # Use relative import
from .database import DatabaseManager  # Use relative import
from .auth import Auth  # Use relative import
from .logger import logger  # Use relative import
import requests
from datetime import datetime

def create_app():
    app = Flask(__name__)
    swagger = Swagger(app)
    config = Config()
    db_manager = DatabaseManager(config)
    db_manager.init_db()
    auth = Auth(config, db_manager)
    

# app = Flask(__name__)
# swagger = Swagger(app)
# config = Config()
# db_manager = DatabaseManager(config)
# db_manager.init_db()
# auth = Auth(config, db_manager)

    def analyze_sentiment(text):
        url = 'https://api.meaningcloud.com/sentiment-2.1'
        params = {
            'key': config.MEANINGCLOUD_API_KEY,
            'txt': text,
            'lang': 'en',
            'model': 'general'
        }
        response = requests.get(url, params=params)
        logger.info(f'response: {response.json()}')
        return response.json()['score_tag']


    # User registration
    @app.route('/auth/register', methods=['POST'])
    @swag_from('swagger/register.yml')
    def register():
        data = request.get_json()
        username = data['username']
        password = data['password']
        logger.info(f'username: {username}, password: {password}')
        user = db_manager.get_user_by_name(username)
        if user:
            abort(400, 'Username already exists')

        user_id = auth.register_user(username, password)
        token = auth.generate_jwt(user_id)
        logger.info(f'token: {token}')
        return jsonify({'token': token, 'message': 'User registered successfully'}), 201

    # User login
    @app.route('/auth/login', methods=['POST'])
    @swag_from('swagger/login.yml')
    def login_user():
        data = request.get_json()
        username = data['username']
        password = data['password']
        token = auth.login_user(username, password)
        if not token:
            abort(401, 'Invalid username or password')

        return jsonify({'token': token})

    @app.route('/auth/profile', methods=['GET'])
    @swag_from('swagger\proflie.yml')
    def get_user_profile():
        token = request.headers.get('Authorization')
        user_id = auth.authenticate(token)
        user = db_manager.get_user_by_id(user_id)
        if not user:
            abort(404, 'User not found')

        return jsonify({'username': user.username, 'message': 'User logged in successfully'})

    @app.route('/notes', methods=['POST'])
    @swag_from('swagger/create_note.yml')
    def create_note():
        token = request.headers.get('Authorization')
        user_id = auth.authenticate(token)
        data = request.get_json()
        title = data['title']
        body = data['body']
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sentiment = analyze_sentiment(body)

        note_id = db_manager.add_note(user_id, title, body, created_at, sentiment)

        return jsonify({'id': note_id, 'title': title, 'body': body, 'created_at': created_at, 'sentiment': sentiment}), 201

    @app.route('/notes', methods=['GET'])
    @swag_from('swagger/get_notes.yml')
    def get_notes():
        token = request.headers.get('Authorization')
        user_id = auth.authenticate(token)
        notes = db_manager.get_notes(user_id)
        subscriptions = (db_manager.get_user_subscriptions(user_id))
        for sub in subscriptions:
            notes += db_manager.get_notes(sub.subscribed_user_id)
        return jsonify([{
            'id': note.id,
            'title': note.title,
            'body': note.body,
            'created_at': note.created_at,
            'sentiment': note.sentiment
        } for note in notes])

    @app.route('/notes/<int:note_id>', methods=['GET'])
    @swag_from('swagger/get_note_by_id.yml')
    def get_note(note_id):
        token = request.headers.get('Authorization')
        user_id = auth.authenticate(token)
        note = db_manager.get_note(note_id)

        if not note:
            abort(404, 'Note not found')
        subscription = db_manager.get_user_subscriptions(user_id)
        if note.user_id != user_id and all(sub.subscribed_user_id != note.user_id for sub in subscription):
            abort(403, 'You are not authorized to access this note')

        return jsonify({
            'id': note.id,
            'title': note.title,
            'body': note.body,
            'created_at': note.created_at,
            'sentiment': note.sentiment
        })

    @app.route('/users', methods=['GET'])
    @swag_from('swagger/users.yml')
    def get_users():
        token = request.headers.get('Authorization')
        auth.authenticate(token)
        users = db_manager.get_all_users()
        return jsonify([{'id': user.id, 'username': user.username} for user in users])

    @app.route('/subscribe/<int:user_id>', methods=['POST'])
    @swag_from('swagger/subscribe.yml')
    def subscribe_to_user(user_id):
        token = request.headers.get('Authorization')
        subscriber_id = auth.authenticate(token)
        subscription = db_manager.get_subscription(subscriber_id, user_id)
        if subscription:
            abort(400, 'You are already subscribed to this user')

        db_manager.add_subscription(subscriber_id, user_id)

        return jsonify({'message': 'Subscribed successfully'})
    
    return app, db_manager

if __name__ == '__main__':
    app, db_manager = create_app()
    app.run(host='0.0.0.0', port=3500, debug=True)
