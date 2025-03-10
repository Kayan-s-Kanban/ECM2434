from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Event, Pet

class EventsTestCase(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password = 'password')

        # create a Pet related to the user
        self.pet1 = Pet.objects.create(user = self.user1, name = 'Test Pet', xp = 0)

        # create a test event
        self.event = Event.objects.create(
            name = 'Test Event',
            description = 'Test Event Description',
            location = 'Test Event Location',
            start = '2025-03-15 18:00:00',
            end = '2025-03-15 20:00:00'
        )

    # As a user, I can earn points from completing events
    def test_earn_points_from_event(self):
        # check points at start
        initial_points = self.user1.points

        # user completes event
        response = self.client.post(reverse('complete_event', args=[self.event.id]))  # Adjust this to match your URL

        # reload user data after event completion
        self.user1.refresh_from_db()

        # check user points have increased
        self.assertGreater(self.user1.points, initial_points)

    # As a user, I can earn XP from completing events
    def test_earn_xp_from_event(self):
        # check xp at start
        initial_xp = self.pet1.xp

        # user completes event
        response = self.client.post(reverse('complete_event', args=[self.event.id]))  # Adjust this to match your URL

        # reload pet data after event completion
        self.pet1.refresh_from_db()

        # check pet's xp has increased
        self.assertGreater(self.pet1.xp, initial_xp)
