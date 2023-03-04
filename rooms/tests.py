# from django.test import TestCase
from rest_framework.test import APITestCase
from . import models

# Create your tests here.
class TestAmenities(APITestCase):

    NAME = "Amenity Test"
    DESC = "Amenity Des"

    def setUp(self):
        models.Amenity.objects.create(name=self.NAME, description=self.DESC)

    def test_all_amenities(self):
        response = self.client.get("/api/v1/rooms/amenities/")
        data = response.json()

        # print(data)

        self.assertEqual(response.status_code, 200, "Status code isn't 200.")
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], self.NAME)
        self.assertEqual(data[0]["description"], self.DESC)
