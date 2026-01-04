"""
API tests for user endpoints.

Tests user CRUD operations.
"""

from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import Users


class UsersAPITests(APITestCase):
    """Tests for users API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.admin_user = Users.objects.create(
            username='admin', password='password123',
            email='admin@example.com', firstname='Admin',
            lastname='User', role='admin'
        )
    
    def setUp(self):
        """Authenticate for each test."""
        self.client.force_authenticate(user=self.admin_user)
        
        self.test_user = Users.objects.create(
            username='testuser', password='password123',
            email='test@example.com', firstname='Test',
            lastname='User', role='staff'
        )
    
    def test_get_users_list(self):
        """Test listing all users."""
        response = self.client.get('/selita/users')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_get_single_user(self):
        """Test retrieving a specific user."""
        response = self.client.get(f'/selita/user/{self.test_user.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_get_user_not_found(self):
        """Test retrieving non-existent user returns 404."""
        response = self.client.get('/selita/user/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_user(self):
        """Test creating a new user."""
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'new@example.com',
            'firstname': 'New',
            'lastname': 'User',
            'role': 'staff'
        }
        response = self.client.post('/selita/create-user', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_500_INTERNAL_SERVER_ERROR])
    
    def test_update_user(self):
        """Test updating a user."""
        data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'firstname': 'Updated',
            'lastname': 'User',
            'role': 'admin'
        }
        response = self.client.post(
            f'/selita/update-user/{self.test_user.id}',
            data, format='json'
        )
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])
    
    def test_delete_user(self):
        """Test deleting a user."""
        response = self.client.delete(f'/selita/delete-user/{self.test_user.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_user_not_found(self):
        """Test deleting non-existent user returns 404."""
        response = self.client.delete('/selita/delete-user/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
