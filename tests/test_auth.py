import sys
import os
import unittest
from flask import json

# # Adjust the path to include the app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app

class AppTestCase(unittest.TestCase):
    
    def setUp(self):
        # Create the app using the test configuration
        self.app, self.db_manager = create_app()
        self.client = self.app.test_client()
        # self.app_context = self.app.app_context()
        # self.app_context.push()
        # self.db_manager = self.app.db_manager
        # self.auth = self.app.auth

        # # Initialize database
        # self.db_manager.__init__(Config())
        # self.db_manager.init_db()

        # # Create a test user and get a token
        # self.token = self._register_and_login_user()

    def tearDown(self):
        self.db_manager.drop_db()
    #     self.app_context.pop()

    def test_register_user(self):
        response = self.client.post('/auth/register', json={
            'username': 'user1',
            'password': '1245'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', json.loads(response.data))



    def test_login_user(self):
        self.client.post('/auth/register', json={
            'username': 'user2',
            'password': '12345'
        })
        response = self.client.post('/auth/login', json={
            'username': 'user2',
            'password': '12345'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(data['message'], 'User logged in successfully')
        self.assertIn('token', data)

    def test_profile_retrieval(self):
        # Register and log in a user
        response = self.client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        access_token =  response.get_json().get('token')

        # Retrieve profile
        response = self.client.get('/auth/profile', headers={
            'Authorization': access_token
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], 'testuser')

if __name__ == '__main__':
    unittest.main()
