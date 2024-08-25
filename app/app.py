from flask import Flask, request, jsonify, abort
from flasgger import Swagger, swag_from
from .config import Config, TestConfig
from .database import DatabaseManager  
from .auth import Auth  
from .logger import logger  
from .sentiment_service import SentimentService
import requests
from datetime import datetime

def create_app(test=False):
    app = Flask(__name__)
    swagger = Swagger(app)
    config = Config()
    if test:    
        config = TestConfig()
    db_manager = DatabaseManager(config)
    db_manager.init_db()
    auth = Auth(config, db_manager)
    sentiment_service = SentimentService(config.MEANINGCLOUD_API_KEY)

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
        logger.info(f'username: {username}, password: {password}')
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
        logger.info(f'user_id: {user_id}')
        if not user:
            abort(404, 'User not found')
        last_note = db_manager.get_last_note(user_id)
        response = {
            'id': user.id,
            'username': user.username,
        }
        if last_note:
            response.update({
                'id': last_note.id,
                'title': last_note.title,
                'body': last_note.body,
                'created_at': last_note.created_at,
                'score_tag': last_note.score_tag,
                'agreement': last_note.agreement,
                'subjectivity': last_note.subjectivity,
                'confidence': last_note.confidence
            })
        return jsonify(response)
    
    @app.route('/notes', methods=['POST'])
    @swag_from('swagger/create_note.yml')
    def create_note():
        token = request.headers.get('Authorization')
        user_id = auth.authenticate(token)
        data = request.get_json()
        title = data['title']
        body = data['body']
        logger.info(f'title: {title}, body: {body}')
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sentiment_data = sentiment_service.analyze(body)
        note_id = db_manager.add_note(user_id, title, body, created_at, **sentiment_data)
        return jsonify({
            'id': note_id,
            'title': title,
            'body': body,
            'created_at': created_at,
            **sentiment_data
        }), 201
    
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
            'score_tag': note.score_tag,
            'agreement': note.agreement,
            'subjectivity': note.subjectivity,
            'confidence': note.confidence
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
            'score_tag': note.score_tag,
            'agreement': note.agreement,
            'subjectivity': note.subjectivity,
            'confidence': note.confidence
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
        if(user_id == subscriber_id):
            abort(400, 'You cannot subscribe to yourself')
        user = db_manager.get_user_by_id(user_id)
        if not user:
            abort(404, 'User not found')
        subscription = db_manager.get_subscription(subscriber_id, user_id)
        if subscription:
            abort(400, 'You are already subscribed to this user')

        db_manager.add_subscription(subscriber_id, user_id)

        return jsonify({'message': 'Subscribed successfully'})
    
    return app, db_manager

if __name__ == '__main__':
    app, db_manager = create_app()
    app.run(host='0.0.0.0', port=3500, debug=True)
