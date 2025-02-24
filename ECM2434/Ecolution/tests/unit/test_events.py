from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser


class EventsTestCase(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password = 'password')

    # As a user, I can view the Events page
    def test_view_events(self):
        response = self.client.get('/events/')

        # ensure the response status code is 200
        self.assertEqual(response.status_code, 200)

