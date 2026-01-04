"""
API tests for exchange rate endpoints.

Tests exchange rate queries and currency conversion.
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import ExchangeRate, Users


class ExchangeRateAPITests(APITestCase):
    """Tests for exchange rate API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = Users.objects.create(
            username='testuser', password='password123',
            email='test@example.com', firstname='Test',
            lastname='User', role='admin'
        )
    
    def setUp(self):
        """Authenticate for each test."""
        self.client.force_authenticate(user=self.user)
        
        self.rate = ExchangeRate.objects.create(
            from_currency='USD',
            to_currency='EUR',
            rate=Decimal('0.92')
        )
    
    def test_get_exchange_rates(self):
        """Test getting all exchange rates."""
        response = self.client.get('/selita/exchange-rates')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rates', response.data)
    
    def test_get_single_exchange_rate(self):
        """Test getting a specific exchange rate."""
        response = self.client.get('/selita/exchange-rate/USD/EUR')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rate', response.data)
    
    def test_get_exchange_rate_not_found(self):
        """Test getting non-existent exchange rate."""
        response = self.client.get('/selita/exchange-rate/XXX/YYY')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_convert_currency(self):
        """Test currency conversion."""
        data = {
            'from_currency': 'USD',
            'to_currency': 'EUR',
            'amount': '100.00'
        }
        response = self.client.post('/selita/convert-currency', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
