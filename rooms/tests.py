# from django.test import TestCase
from rest_framework.test import APITestCase
from . import models

# Create your tests here.
class TestAmenities(APITestCase):

    NAME = "Amenity Test"
    DESC = "Amenity Des"
    URL = "/api/v1/rooms/amenities/"

    def setUp(self):
        models.Amenity.objects.create(name=self.NAME, description=self.DESC)

    def test_all_amenities(self):
        response = self.client.get(self.URL)
        data = response.json()

        # print(data)

        self.assertEqual(response.status_code, 200, "Status code isn't 200.")
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], self.NAME)
        self.assertEqual(data[0]["description"], self.DESC)

    def test_create_amenity(self):
        # TODO@Ando: authenticated 유저만 사용가능한지 테스트 하는 방법은?
        new_amenity_name = "New Amenity"
        new_amenity_description = "New Amenity desc."

        response = self.client.post(
            self.URL,
            data={
                "name": new_amenity_name,
                "description": new_amenity_description,
            },
        )
        data = response.json()

        # print(data)

        self.assertEqual(response.status_code, 200, "Not 200 status code")
        self.assertEqual(data["name"],new_amenity_name)
        self.assertEqual(data["description"],new_amenity_description)

        response = self.client.post(self.URL)
        data = response.json()

        # print(data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", data)
        
