"""
Unit tests for Supplier model.
"""

from django.test import TestCase
from selita.models import Supplier


class SupplierModelTests(TestCase):
    """Tests for the Supplier model."""
    
    def test_supplier_creation(self):
        """Test creating a supplier with all fields."""
        supplier = Supplier.objects.create(
            firstname='Fish',
            lastname='Supplier',
            phone='+355 69 123 4567',
            email='supplier@fish.com',
            address='123 Harbor Street, Durres'
        )
        self.assertEqual(supplier.firstname, 'Fish')
        self.assertEqual(supplier.lastname, 'Supplier')
        self.assertEqual(supplier.phone, '+355 69 123 4567')
        self.assertEqual(supplier.email, 'supplier@fish.com')
        self.assertEqual(supplier.address, '123 Harbor Street, Durres')
    
    def test_supplier_optional_fields(self):
        """Test that phone and email are optional."""
        supplier = Supplier.objects.create(
            firstname='Local',
            lastname='Fisher',
            address='Pier 5, Vlora'
        )
        self.assertIsNone(supplier.phone)
        self.assertIsNone(supplier.email)
        self.assertEqual(supplier.firstname, 'Local')
    
    def test_supplier_str(self):
        """Test supplier string representation."""
        supplier = Supplier.objects.create(
            firstname='Marco',
            lastname='Pescatore',
            address='Via Roma 10, Bari'
        )
        self.assertEqual(str(supplier), 'Marco Pescatore')
    
    def test_supplier_ordering(self):
        """Test suppliers are ordered by lastname, firstname."""
        Supplier.objects.create(firstname='Zach', lastname='Adams', address='Address 1')
        Supplier.objects.create(firstname='Anna', lastname='Adams', address='Address 2')
        Supplier.objects.create(firstname='Bob', lastname='Brown', address='Address 3')
        
        suppliers = list(Supplier.objects.all())
        self.assertEqual(suppliers[0].firstname, 'Anna')
        self.assertEqual(suppliers[1].firstname, 'Zach')
        self.assertEqual(suppliers[2].lastname, 'Brown')
    
    def test_supplier_update(self):
        """Test updating a supplier's fields."""
        supplier = Supplier.objects.create(
            firstname='Old',
            lastname='Name',
            address='Old Address'
        )
        
        supplier.firstname = 'New'
        supplier.phone = '+355 69 999 9999'
        supplier.email = 'new@supplier.com'
        supplier.save()
        supplier.refresh_from_db()
        
        self.assertEqual(supplier.firstname, 'New')
        self.assertEqual(supplier.phone, '+355 69 999 9999')
        self.assertEqual(supplier.email, 'new@supplier.com')
