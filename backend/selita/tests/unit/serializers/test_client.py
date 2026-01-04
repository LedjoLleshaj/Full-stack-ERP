"""
Unit tests for ClientSerializer.
"""
from django.test import TestCase
from selita.serializers import ClientSerializer
from selita.models import Client


class ClientSerializerTests(TestCase):
    """Tests for ClientSerializer."""
    
    def test_client_serialization(self):
        """Test serializing a client instance."""
        client = Client.objects.create(
            firstname='John', lastname='Doe',
            phone='+355 69 111 2222',
            email='john@example.com',
            address='123 Main St', city='Tirana'
        )
        serializer = ClientSerializer(instance=client)
        data = serializer.data
        
        self.assertEqual(data['firstname'], 'John')
        self.assertEqual(data['lastname'], 'Doe')
        self.assertEqual(data['phone'], '+355 69 111 2222')
        self.assertIn('id', data)
    
    def test_client_deserialization_valid(self):
        """Test deserializing valid client data."""
        data = {
            'firstname': 'Jane',
            'lastname': 'Smith',
            'phone': '+355 69 333 4444',
            'address': '456 Oak Ave',
            'city': 'Durres'
        }
        serializer = ClientSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        client = serializer.save()
        self.assertEqual(client.firstname, 'Jane')
        self.assertEqual(client.city, 'Durres')
    
    def test_client_deserialization_missing_required(self):
        """Test deserialization with missing required fields."""
        data = {'firstname': 'John'}
        serializer = ClientSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('lastname', serializer.errors)
        self.assertIn('phone', serializer.errors)
