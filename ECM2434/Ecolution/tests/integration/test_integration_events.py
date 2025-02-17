from django.test import TestCase
from Ecolution.models import CustomUser

class EventsTestCase(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password = 'password')

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
    ## As a user, I can view events on the map
    ## As a user, I can complete events
