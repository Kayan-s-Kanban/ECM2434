from django.test import TestCase
from django.urls import reverse

from Ecolution.models import CustomUser

class EventsTestCase(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password = 'password')

        # log user in
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('home'))

    ## As a user, I can view the Events page
    def test_view_events(self):
        self.client.login(username = 'testuser', password = 'password')
        response = self.client.get('/events/')

        # check user is redirected to "events" page
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/events/')

    ## As a user, I can search for events
    ## As a user, I can view event details
    ## As a user, I can add events to my list
    ## As a user, I can remove events from my list
    ## As a user, I can view event location
    ## As a user, I can complete events by completing all sub-tasks

    ## As a user, I can open and close the menu
    def test_events_menu(self):
        # user selects menu button
        response = self.client.post(reverse('events'), {'show menu': True}, follow=True)  # TODO: check syntax

        # menu opens up
        self.assertContains(response, 'menu')
