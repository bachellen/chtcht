import unittest
from app import create_app
from flask import json

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True})
        self.client = self.app.test_client()

    def login(self):
        return self.client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })

    def logout(self, token):
        return self.client.post('/auth/logout', headers={
            'Authorization': f'Bearer {token}'
        })

    def test_user_registration(self):
        response = self.client.post('/auth/register', json={
            'email': 'newone@example.com',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully', response.json['message'])
    
    def test_login_logout(self):
        login_response = self.login()
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json['token']
        
        logout_response = self.logout(token)
        self.assertEqual(logout_response.status_code, 200)
        self.assertIn('Logged out successfully', logout_response.json['message'])

    def test_access_secured_endpoint(self):
        login_response = self.login()
        token = login_response.json['token']
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = self.client.get('/message/subscribe', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        self.logout(token)

if __name__ == '__main__':
    unittest.main()
