from django.test import TestCase
from django.urls import reverse
from django.db import connection
from Ecolution.models import CustomUser, Event, Pet

class ShopIntegrationTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    # As a user, I can purchase an item multiple times after a cooldown period

    # As a user, I can purchase an item, and the points are removed from my account