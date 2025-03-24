from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Event

class EventsUnitTests(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password = 'password')

        # create a test event
        self.event = Event.objects.create(
            event_name='Test Event',
            description='Test Event Description',
            location='Test Event Location',
            date='2025-03-15',
            time='00:00:00',
        )

        # event url
        self.url_event = reverse('events')

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

    # ⚠️As a user, I can join Events
    def test_join_event(self):
        response = self.client.post(reverse('join_event'), args = [self.event.event_id])  # Change this URL pattern to match your app

        # user is redirected to the event detail page
        self.assertRedirects(response, reverse('get_event_tasks', args = [self.event.event_id]))

        # check user is now part of the event's attendees (assuming there's a ManyToMany relation with CustomUser)
        # self.assertIn(self.user1, self.event.attendees.all()) # TODO: fix reference

    # ⚠️ As a user, I can leave Events
    def test_leave_event(self):
        # event is added for user
        self.client.post(reverse('join_event'), args = [self.event.event_id])

        # event appears in user's events list
        response = self.client.post(reverse('events'))
        self.assertContains(response, 'Test Event')

        # user views event details
        self.client.post(reverse('events'), args=[self.event.event_id])

        # user can view "leave event" button ??? TODO:
        self.assertContains(self.client.post(reverse('events')), 'Leave Event')

        # user leaves event
        response = self.client.post(reverse('leave_event'), args=[self.event.event_id])

        # event no longer appears
        self.assertNotContains(self.client.post(reverse('events')), 'Leave Event')

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

    # ⚠️ As a user, I can see the start time of the event️
    def test_event_time(self):
        response = self.client.get(self.url_event)

        # user selects event

        # then check time appears on page
        self.assertContains(response, '00:00:00') # time will be colloquial (ex. 10 am)


