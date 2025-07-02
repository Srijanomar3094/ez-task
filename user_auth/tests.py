from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json
from .models import Verification, Role
from unittest.mock import patch


class UserAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.registration_url = '/api/user_registration/'
        self.login_url = '/api/login_view/'
        self.logout_url = '/api/logout_view/'
        self.verify_url = '/api/verify/'
        
        self.test_user_data = {
            'email': 'test@example.com',
            'password': 'Test@1234',
            'role': 'Ops',
            'name': 'Test User'
        }

    def test_user_registration_without_verification(self):
        """Test that registration fails without email verification"""
        response = self.client.post(
            self.registration_url,
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('First verify your email', response.json()['message'])

    @patch('user_auth.views.get_connection')
    def test_email_verification_flow(self, mock_connection):
        """Test complete email verification process"""
        mock_connection.return_value = None
        
        data = {'email': 'test@example.com'}
        response = self.client.post(
            self.verify_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        verification = Verification.objects.filter(email='test@example.com').first()
        data = {'email': 'test@example.com', 'code': verification.code}
        response = self.client.post(
            self.verify_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Code verified', response.json()['message'])

    def test_user_registration_with_verification(self):
        """Test successful user registration after verification"""
        Verification.objects.create(
            email='test@example.com',
            code='1234',
            is_expired=True,
            is_verified=True
        )
        
        response = self.client.post(
            self.registration_url,
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Registration successful', response.json()['message'])
        
        user = User.objects.filter(email='test@example.com').first()
        self.assertIsNotNone(user)
        role = Role.objects.filter(user=user).first()
        self.assertEqual(role.role, 'Ops')

    def test_user_login_success(self):
        """Test successful user login"""
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='Test@1234'
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'Test@1234'
        }
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Login successful', response.json()['message'])

    def test_user_login_wrong_credentials(self):
        """Test login with incorrect credentials"""
        User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='Test@1234'
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('Incorrect credentials', response.json()['message'])

    def test_user_logout(self):
        """Test user logout functionality"""
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='Test@1234'
        )
        
        self.client.force_login(user)
        response = self.client.get(self.logout_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Logout successful', response.json()['message'])
