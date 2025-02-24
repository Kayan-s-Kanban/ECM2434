from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser


class EventsTestCase(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    # As a user, I can view the Events page
    def test_view_events(self):
        response = self.client.get('/events/')

        # Ensure the response status code is 200
        self.assertEqual(response.status_code, 200)

    # As a user, I can open and close the menu
    def test_events_menu(self):
        # simulate toggling the menu
        response = self.client.post(reverse('events'), {'show menu': True}, follow=True)

        # check if 'menu' appears in the response
        self.assertContains(response, 'menu')

        # simulate closing the menu
        response = self.client.post(reverse('events'), {'show menu': False}, follow=True)

        # check if 'menu' disappears
        self.assertNotContains(response, 'menu')
