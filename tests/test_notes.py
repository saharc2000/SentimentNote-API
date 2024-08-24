import sys
import os
import unittest
from flask import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.app import create_app


class AppTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app, self.db_manager = create_app()
        self.client = self.app.test_client()

    def tearDown(self):
        self.db_manager.drop_db()

    def test_create_note(self):
        response = self.client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        access_token =  response.get_json().get('token')

        # Retrieve profile
        response = self.client.post('/notes', headers={
            'Authorization': access_token
        }, json={
            'title': 'Test Note',
            'body': 'This is a test note'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)

    def test_get_note(self):
        response = self.client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        access_token =  response.get_json().get('token')

        # Retrieve profile
        response = self.client.get('/notes', headers={
            'Authorization': access_token
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)


    # def test_get_note_by_id(self):

    # def test_users(self):

    # def test_subscribe(self):

if __name__ == '__main__':
    unittest.main()
