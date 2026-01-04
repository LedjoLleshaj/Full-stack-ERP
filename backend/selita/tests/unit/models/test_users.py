"""
Unit tests for Users model.
"""

from django.test import TestCase
from selita.models import Users


class UsersModelTests(TestCase):
    """Tests for the Users model."""
    
    def test_user_creation(self):
        """Test creating a user with all required fields."""
        user = Users.objects.create(
            username='testuser',
            password='hashedpassword123',
            email='test@example.com',
            firstname='John',
            lastname='Doe',
            role='admin'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.firstname, 'John')
        self.assertEqual(user.lastname, 'Doe')
        self.assertEqual(user.role, 'admin')
    
    def test_user_str(self):
        """Test user string representation returns username."""
        user = Users.objects.create(
            username='johndoe',
            password='password123',
            email='john@example.com',
            firstname='John',
            lastname='Doe',
            role='user'
        )
        self.assertEqual(str(user), 'johndoe')
    
    def test_user_is_authenticated_property(self):
        """Test that is_authenticated property always returns True."""
        user = Users.objects.create(
            username='authuser',
            password='password123',
            email='auth@example.com',
            firstname='Auth',
            lastname='User',
            role='user'
        )
        self.assertTrue(user.is_authenticated)
    
    def test_user_ordering(self):
        """Test that users are ordered by -id (newest first)."""
        user1 = Users.objects.create(
            username='user1',
            password='pass1',
            email='user1@example.com',
            firstname='First',
            lastname='User',
            role='user'
        )
        user2 = Users.objects.create(
            username='user2',
            password='pass2',
            email='user2@example.com',
            firstname='Second',
            lastname='User',
            role='user'
        )
        users = list(Users.objects.all())
        self.assertEqual(users[0].username, 'user2')
        self.assertEqual(users[1].username, 'user1')
    
    def test_user_update(self):
        """Test updating a user's fields."""
        user = Users.objects.create(
            username='updateuser',
            password='oldpass',
            email='old@example.com',
            firstname='Old',
            lastname='Name',
            role='user'
        )
        
        user.email = 'new@example.com'
        user.firstname = 'New'
        user.role = 'admin'
        user.save()
        user.refresh_from_db()
        
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.firstname, 'New')
        self.assertEqual(user.role, 'admin')
