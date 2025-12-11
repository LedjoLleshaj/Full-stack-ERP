"""
API tests for authentication endpoints.

Tests login, logout, registration, and token management.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthenticationAPITests(APITestCase):
    """Tests for authentication API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_success(self):
        """Test successful login."""
        url = reverse('login')  # Adjust URL name as needed
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        # Adjust assertions based on your actual response format
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn('token', response.data)  # If using token auth
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout(self):
        """Test logout endpoint."""
        # First login
        self.client.force_authenticate(user=self.user)
        
        url = reverse('logout')  # Adjust URL name as needed
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# TODO: Add more auth tests:
# - Registration tests
# - Password reset tests
# - Token refresh tests (if using JWT)
# - Permission tests
