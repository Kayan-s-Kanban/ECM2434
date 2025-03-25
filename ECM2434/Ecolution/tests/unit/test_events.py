from datetime import time
from django.urls import reverse
from Ecolution.models import CustomUser, Event, UserEvent
from Ecolution.tests.base_test import BaseTestCase


class EventsUnitTests(BaseTestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # create a test event
        self.event = Event.objects.create(
            event_name='Test Event',
            description='Test Event Description',
            location='Test Event Location',
            date='2025-03-15',
            time=time(10, 0, 0),  # Use datetime.time object
        )

        # event url
        self.url_event = reverse('events')
        self.url_join_event = reverse('join_event')
        self.url_leave_event = reverse('leave_event')

    # As a user, I can create an event
    def test_event_creation(self):
        self.assertIsNotNone(self.event.event_id)

    # As a user, I can view the Events page
    def test_view_events(self):
        response = self.client.get(self.url_event)

        # check response status code is 200
        self.assertEqual(response.status_code, 200)

        # check that the event is in the response content
        self.assertContains(response, 'Test Event')
        self.assertContains(response, 'Test Event Description')
        self.assertContains(response, 'Test Event Location')

    # As a user, I can join Events
    def test_join_event(self):
        # user joins event
        response = self.client.post(self.url_join_event, {'event_id': self.event.event_id})

        # check request was successful. The view returns a JSON response with {"success": True}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

        # check UserEvent object has been created linking the user and the event
        self.assertTrue(UserEvent.objects.filter(user = self.user1, event = self.event).exists())

    # As a user, I can leave Events
    def test_leave_event(self):
        # user joins event
        self.client.post(self.url_join_event, {'event_id': self.event.event_id})

        # user leaves event
        response = self.client.post(self.url_leave_event, {'event_id': self.event.event_id})

        # Check if the user is no longer associated with the event
        user_event = UserEvent.objects.filter(user=self.user1, event=self.event)
        self.assertFalse(user_event.exists())

        # Check if the response is successful
        self.assertJSONEqual(str(response.content, encoding='utf8'), '{"success": true}')

    # As a user, I can see the location of the event
    def test_event_location(self):
        response = self.client.get(self.url_event)

        # check location appears on page
        self.assertContains(response, 'Test Event Location')

    # As a user, I can see the date of the event
    def test_event_date(self):
        response = self.client.get(self.url_event)

        # check date appears on page
        self.assertContains(response, 'March 15, 2025')


