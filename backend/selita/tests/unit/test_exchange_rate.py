"""
Unit tests for ExchangeRate model.
"""

from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from selita.models import ExchangeRate


class ExchangeRateModelTests(TestCase):
    """Tests for the ExchangeRate model."""
    
    def test_exchange_rate_creation(self):
        """Test creating an exchange rate with valid currency pairs."""
        rate = ExchangeRate.objects.create(
            from_currency='USD',
            to_currency='EUR',
            rate=Decimal('0.920000')
        )
        self.assertEqual(rate.from_currency, 'USD')
        self.assertEqual(rate.to_currency, 'EUR')
        self.assertEqual(rate.rate, Decimal('0.920000'))
        self.assertIsNotNone(rate.last_updated)
    
    def test_exchange_rate_all_currency_pairs(self):
        """Test creating exchange rates for all valid currency combinations."""
        ExchangeRate.objects.create(from_currency='EUR', to_currency='USD', rate=Decimal('1.086957'))
        ExchangeRate.objects.create(from_currency='EUR', to_currency='LEK', rate=Decimal('100.500000'))
        ExchangeRate.objects.create(from_currency='USD', to_currency='EUR', rate=Decimal('0.920000'))
        ExchangeRate.objects.create(from_currency='USD', to_currency='LEK', rate=Decimal('92.500000'))
        ExchangeRate.objects.create(from_currency='LEK', to_currency='EUR', rate=Decimal('0.009950'))
        ExchangeRate.objects.create(from_currency='LEK', to_currency='USD', rate=Decimal('0.010811'))
        
        self.assertEqual(ExchangeRate.objects.count(), 6)
    
    def test_exchange_rate_unique_constraint(self):
        """Test that duplicate currency pairs raise IntegrityError."""
        ExchangeRate.objects.create(from_currency='USD', to_currency='EUR', rate=Decimal('0.920000'))
        
        with self.assertRaises(IntegrityError):
            ExchangeRate.objects.create(from_currency='USD', to_currency='EUR', rate=Decimal('0.950000'))
    
    def test_exchange_rate_precision(self):
        """Test that rate supports 6 decimal places for precision."""
        rate = ExchangeRate.objects.create(from_currency='LEK', to_currency='EUR', rate=Decimal('0.009876'))
        rate.refresh_from_db()
        self.assertEqual(rate.rate, Decimal('0.009876'))
        
        rate2 = ExchangeRate.objects.create(from_currency='EUR', to_currency='LEK', rate=Decimal('101.234567'))
        rate2.refresh_from_db()
        self.assertEqual(str(rate2.rate)[:10], '101.234567')
    
    def test_exchange_rate_str(self):
        """Test exchange rate string representation."""
        rate = ExchangeRate.objects.create(from_currency='USD', to_currency='EUR', rate=Decimal('0.920000'))
        self.assertEqual(str(rate), 'USD → EUR: 0.920000')
    
    def test_exchange_rate_last_updated_auto(self):
        """Test that last_updated is automatically set."""
        rate = ExchangeRate.objects.create(from_currency='EUR', to_currency='USD', rate=Decimal('1.086957'))
        self.assertIsNotNone(rate.last_updated)
        
        old_updated = rate.last_updated
        rate.rate = Decimal('1.100000')
        rate.save()
        rate.refresh_from_db()
        self.assertGreaterEqual(rate.last_updated, old_updated)
    
    def test_exchange_rate_update(self):
        """Test updating an existing exchange rate."""
        rate = ExchangeRate.objects.create(from_currency='USD', to_currency='EUR', rate=Decimal('0.920000'))
        
        rate.rate = Decimal('0.930000')
        rate.save()
        rate.refresh_from_db()
        
        self.assertEqual(rate.rate, Decimal('0.930000'))
