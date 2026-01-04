"""
API tests for reports endpoints.

Tests dashboard stats, sales reports, and analytics.
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import (
    Users, Client, Product, Transaction, Sales, Account, Inventory
)


class ReportsAPITests(APITestCase):
    """Tests for reports API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = Users.objects.create(
            username='testuser', password='password123',
            email='test@example.com', firstname='Test',
            lastname='User', role='admin'
        )
        cls.db_client = Client.objects.create(
            firstname='John', lastname='Doe',
            phone='+355 69 111 2222',
            address='123 Main St', city='Tirana'
        )
        cls.product = Product.objects.create(
            name='Fresh Salmon', category='Fish',
            price=Decimal('15.00'), description='Atlantic salmon'
        )
        cls.account = Account.objects.create(
            account_name='Cash EUR', account_type='CASH',
            currency='EUR', current_balance=Decimal('1000.00')
        )
    
    def setUp(self):
        """Authenticate for each test."""
        self.client.force_authenticate(user=self.user)
        
        # Create inventory
        Inventory.objects.create(prod=self.product, quantity=100)
        
        # Create sample transaction and sale
        self.transaction = Transaction.objects.create(
            transaction_type='SALE',
            client=self.db_client,
            total_amount=Decimal('150.00'),
            currency='EUR',
            status='COMPLETED'
        )
        Sales.objects.create(
            transaction=self.transaction,
            prod=self.product,
            prod_price=Decimal('15.00'),
            user=self.user,
            quantity=10
        )
    
    def test_get_dashboard_stats(self):
        """Test getting dashboard statistics."""
        response = self.client.get('/selita/dashboard-stats')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('revenue_today', response.data)
    
    def test_get_daily_profit(self):
        """Test getting daily profit data."""
        response = self.client.get('/selita/daily-profit')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_paid_vs_unpaid(self):
        """Test getting paid vs unpaid stats."""
        response = self.client.get('/selita/paid-vs-unpaid')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_top_products(self):
        """Test getting top products."""
        response = self.client.get('/selita/top-products')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_profit_by_category(self):
        """Test getting profit by category."""
        response = self.client.get('/selita/profit-by-category')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_top_clients(self):
        """Test getting top clients."""
        response = self.client.get('/selita/top-clients')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_sales_report(self):
        """Test getting sales report."""
        response = self.client.get('/selita/report/sales/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_sales_report_with_date_filter(self):
        """Test getting sales report with date filter."""
        response = self.client.get('/selita/report/sales/?start_date=2024-01-01&end_date=2024-12-31')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
