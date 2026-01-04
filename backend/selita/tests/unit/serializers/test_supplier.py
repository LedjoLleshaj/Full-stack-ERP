"""
Unit tests for SupplierSerializer.
"""
from django.test import TestCase
from selita.serializers import SupplierSerializer
from selita.models import Supplier


class SupplierSerializerTests(TestCase):
    """Tests for SupplierSerializer."""
    
    def test_supplier_serialization(self):
        """Test serializing a supplier instance."""
        supplier = Supplier.objects.create(
            firstname='Fish', lastname='Co',
            phone='+355 69 555 6666',
            address='Harbor 1'
        )
        serializer = SupplierSerializer(instance=supplier)
        data = serializer.data
        
        self.assertEqual(data['firstname'], 'Fish')
        self.assertEqual(data['lastname'], 'Co')
    
    def test_supplier_deserialization_valid(self):
        """Test deserializing valid supplier data."""
        data = {
            'firstname': 'Sea',
            'lastname': 'Foods',
            'address': 'Pier 5'
        }
        serializer = SupplierSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        supplier = serializer.save()
        self.assertEqual(supplier.firstname, 'Sea')
