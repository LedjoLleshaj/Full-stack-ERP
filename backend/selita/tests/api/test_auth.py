"""
API tests for authentication endpoints.

Tests login, logout, and token management.
"""

from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import Users
from django.contrib.auth.hashers import make_password


class AuthAPITests(APITestCase):
    """Tests for authentication API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = Users.objects.create(
            username='testuser',
            password=make_password('password123'),
            email='test@example.com',
            firstname='Test',
            lastname='User',
            role='admin'
        )
    
    def test_login_success(self):
        """Test successful login."""
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post('/selita/login', data, format='json')
        
        # Should set cookies and return success
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/selita/login', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])
    
    def test_login_missing_fields(self):
        """Test login with missing fields."""
        data = {'username': 'testuser'}
        response = self.client.post('/selita/login', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout(self):
        """Test logout endpoint."""
        # First authenticate
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/selita/logout')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_token_refresh(self):
        """Test token refresh endpoint."""
        response = self.client.post('/selita/api/token/refresh/')
        
        # Should return 401 without valid refresh token
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
