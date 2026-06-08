from rest_framework import status
from rest_framework.test import APITestCase

from erp.models import Client
from erp.tests.base import ErpTestCase


class ClientAPITests(APITestCase, ErpTestCase):

    def setUp(self):
        self.api_client = self.client
        self.api_client.force_authenticate(user=self.user)

    def test_list_clients(self):
        response = self.api_client.get("/erp/clients")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_retrieve_client(self):
        response = self.api_client.get(f"/erp/client/{self.client_obj.pk}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["firstname"], "Test")

    def test_create_client(self):
        data = {
            "firstname": "New",
            "lastname": "Client",
            "phone": "9876543210",
            "address": "789 New St",
            "city": "Durres",
        }
        response = self.api_client.post("/erp/add-client", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Client.objects.count(), 2)
