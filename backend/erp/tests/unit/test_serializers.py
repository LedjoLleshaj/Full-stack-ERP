from erp.serializers import ClientSerializer, ProductSerializer
from erp.tests.base import ErpTestCase


class ClientSerializerTests(ErpTestCase):

    def test_client_serialization(self):
        serializer = ClientSerializer(instance=self.client_obj)
        data = serializer.data

        self.assertEqual(data["firstname"], "Test")
        self.assertEqual(data["lastname"], "Client")
        self.assertIn("id", data)

    def test_client_deserialization(self):
        data = {
            "firstname": "New",
            "lastname": "Client",
            "phone": "5551234567",
            "address": "123 St",
            "city": "Tirana",
        }
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        client = serializer.save()
        self.assertEqual(client.firstname, "New")


class ProductSerializerTests(ErpTestCase):

    def test_product_serialization(self):
        serializer = ProductSerializer(instance=self.product)
        data = serializer.data

        self.assertEqual(data["name"], "Test Product")
        self.assertEqual(float(data["price"]), 15.00)
        self.assertIn("category", data)
