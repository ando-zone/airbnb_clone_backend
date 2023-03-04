# from django.test import TestCase
from rest_framework.test import APITestCase

# Create your tests here.
class TestAmenities(APITestCase):
    def test_two_plus_two(self):
        self.assertEqual(2 + 2, 5, "wrong")
