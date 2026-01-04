"""
Unit tests for UserSerializer.
"""
from django.test import TestCase
from selita.serializers import UserSerializer
from selita.models import Users


class UserSerializerTests(TestCase):
    """Tests for UserSerializer."""
    
    def test_user_serialization(self):
        """Test serializing a user instance."""
        user = Users.objects.create(
            username='testuser', password='hashed123',
            email='test@example.com',
            firstname='Test', lastname='User', role='admin'
        )
        serializer = UserSerializer(instance=user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['role'], 'admin')
