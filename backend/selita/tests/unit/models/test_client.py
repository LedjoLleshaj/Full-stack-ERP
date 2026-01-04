"""
Unit tests for Client model.
"""

from django.test import TestCase
from django.db import IntegrityError
from selita.models import Client


class ClientModelTests(TestCase):
    """Tests for the Client model."""
    
    def test_client_creation(self):
        """Test creating a client with all fields."""
        client = Client.objects.create(
            firstname='John',
            lastname='Doe',
            email='john@example.com',
            phone='+355 69 111 2222',
            address='123 Main St',
            city='Tirana'
        )
        self.assertEqual(client.firstname, 'John')
        self.assertEqual(client.lastname, 'Doe')
        self.assertEqual(client.email, 'john@example.com')
        self.assertEqual(client.phone, '+355 69 111 2222')
        self.assertEqual(client.city, 'Tirana')
    
    def test_client_unique_phone(self):
        """Test that phone must be unique."""
        Client.objects.create(
            firstname='First',
            lastname='Client',
            phone='+355 69 111 1111',
            address='Address 1',
            city='City 1'
        )
        
        with self.assertRaises(IntegrityError):
            Client.objects.create(
                firstname='Second',
                lastname='Client',
                phone='+355 69 111 1111',
                address='Address 2',
                city='City 2'
            )
    
    def test_client_unique_email(self):
        """Test that email must be unique when provided."""
        Client.objects.create(
            firstname='First',
            lastname='Client',
            email='same@email.com',
            phone='+355 69 111 1111',
            address='Address 1',
            city='City 1'
        )
        
        with self.assertRaises(IntegrityError):
            Client.objects.create(
                firstname='Second',
                lastname='Client',
                email='same@email.com',
                phone='+355 69 222 2222',
                address='Address 2',
                city='City 2'
            )
    
    def test_client_optional_email(self):
        """Test that email is optional."""
        client = Client.objects.create(
            firstname='No',
            lastname='Email',
            phone='+355 69 333 3333',
            address='Some Address',
            city='Durres'
        )
        self.assertIsNone(client.email)
    
    def test_client_str(self):
        """Test client string representation."""
        client = Client.objects.create(
            firstname='Maria',
            lastname='Koçi',
            phone='+355 69 444 4444',
            address='Rruga e Durresit',
            city='Tirana'
        )
        self.assertEqual(str(client), 'Maria Koçi')
    
    def test_client_ordering(self):
        """Test clients are ordered by lastname, firstname."""
        Client.objects.create(firstname='Zack', lastname='Adams', phone='+355 69 001', address='A1', city='City')
        Client.objects.create(firstname='Anna', lastname='Adams', phone='+355 69 002', address='A2', city='City')
        Client.objects.create(firstname='Bob', lastname='Brown', phone='+355 69 003', address='A3', city='City')
        
        clients = list(Client.objects.all())
        self.assertEqual(clients[0].firstname, 'Anna')
        self.assertEqual(clients[1].firstname, 'Zack')
        self.assertEqual(clients[2].lastname, 'Brown')
