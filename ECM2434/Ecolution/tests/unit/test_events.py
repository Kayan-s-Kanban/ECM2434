from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Event

class EventsTestCase(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password = 'password')

        # create a new event with a static date
        static_start_time = datetime(2025, 3, 15, 18, 0, 0)
        static_end_time = static_start_time + datetime.timedelta(hours = 2)  # Event lasts for 2 hours
        self.event = Event.objects.create(
            name = 'Test Event',
            description = 'Test Event Description',
            location = 'Test Event Location',
            start = static_start_time,
            end = static_end_time,
        )

    # As a user, I can view the Events page
    def test_view_events(self):
        response = self.client.get(reverse('events'))

        # check response status code is 200
        self.assertEqual(response.status_code, 200)

        # check that the event is in the response content
        self.assertContains(response, 'Test Event')
        self.assertContains(response, 'Test Event Description')
        self.assertContains(response, 'Test Event Location')

    # As a user, I can join Events
    def test_join_event(self):
        response = self.client.post(reverse('join_event', args=[self.event.id]))  # Change this URL pattern to match your app

        # user is redirected to the event detail page
        self.assertRedirects(response, reverse('get_event_tasks', args=[self.event.id]))

        # check user is now part of the event's attendees (assuming there's a ManyToMany relation with CustomUser)
        self.assertIn(self.user1, self.event.attendees.all()) # TODO: fix reference

    # As a user, I can leave Events
    def test_leave_event(self):
        # add user to event
        self.event.attendees.add(self.user1) # TODO: fix reference

        # user leaves event
        response = self.client.post(reverse('leave_event', args=[self.event.id]))  # Change this URL pattern to match your app

        # user is redirected to the event detail page
        self.assertRedirects(response, reverse('get_event_tasks', args=[self.event.id]))

        # check user is no longer an attendee of the event
        self.assertNotIn(self.user1, self.event.attendees.all())

    # As a user, I can see the location of the event
    def test_event_location(self):
        response = self.client.get(reverse('event_detail', args=[self.event.id]))  # Assuming 'event_detail' is the URL name

        # check location appears on page
        self.assertContains(response, 'Test Event Location')

    # As a user, I can see the start time and date of event
    def test_event_start_time(self):
        response = self.client.get(reverse('event_detail', args=[self.event.id]))  # Assuming 'event_detail' is the URL name

        # check the start time is in the response
        self.assertContains(response, '2025-03-15 18:00:00')

    # As a user, I can see the end time and date of event
    def test_event_end_time(self):
        response = self.client.get(reverse('event_detail', args=[self.event.id]))  # Assuming 'event_detail' is the URL name

        # check the end time is in the response
        self.assertContains(response, '2025-03-15 20:00:00')



