import unittest
from flask import json
from app import create_app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        # Setup app with a secret key and testing mode
        self.app = create_app({
            'TESTING': True,
        })
        self.client = self.app.test_client()

    def login_user(self):
        # Mock logging in a user and getting a token
        response = self.client.post('/auth/login', json={
            'email': 'test@test.com',
            'password': 'test123456'
        })
        return response.json.get('token')

    def logout(self, token):
        return self.client.post('/auth/logout', headers={
            'Authorization': f'Bearer {token}'
        })

    def test_publish_message_successfully(self):
        # Log in and get a token
        token = self.login_user()

        # Test message publishing
        response = self.client.post('/messages/publish', headers={
            'Authorization': f'Bearer {token}'
        }, json={
            'receiver_id': 'kcA4QLnAfvcBnaxExxlmKqw1KIu2',
            'message': 'Hello, World'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('Message published successfully', json.loads(response.data)['message'])
        self.logout(token)

    def test_publish_message_with_incomplete_data(self):
        # Log in and get a token
        token = self.login_user()

        # Testing message publishing with missing fields
        response = self.client.post('/messages/publish', headers={
            'Authorization': f'Bearer {token}'
        }, json={
            'receiver_id': 'kcA4QLnAfvcBnaxExxlmKqw1KIu2',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required data', response.json['error'])

    def test_user_online_status(self):
        # Log in and get a token
        token = self.login_user()

        # Simulate user going online
        response = self.client.post('/users/online', headers={
            'Authorization': f'Bearer {token}'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('User is now online',json.loads(response.data)['message'])

        # Simulate user going offline
        response = self.client.post('/users/offline', headers={
            'Authorization': f'Bearer {token}'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('User is now offline', json.loads(response.data)['message'])

        self.logout(token)

if __name__ == '__main__':
    unittest.main()
