from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Event, Pet

class EventsTestCase(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password = 'password')

        # create a Pet related to the user
        self.pet1 = Pet.objects.create(user = self.user1, pet_name ='Test Pet', pet_exp = 0)

        # create a test event
        self.event = Event.objects.create(
            event_name = 'Test Event',
            description = 'Test Event Description',
            location = 'Test Event Location',
            date = '2025-03-15',
            event_id = 1
        )

    # As a user, I can earn points from completing events
    def test_earn_points_from_event(self):
        # check points at start
        initial_points = self.user1.points

        # user completes event
        self.client.post(reverse('complete_event'))  # TODO: check URL

        # reload user data after event completion
        self.user1.refresh_from_db()

        # check user points have increased
        self.assertTrue(self.user1.points > initial_points)

    # As a user, I can earn XP from completing events
    def test_earn_xp_from_event(self):
        # check xp at start
        initial_xp = self.pet1.pet_exp

        # user completes event
        self.client.post(reverse('complete_event'))  # TODO: check URL

        # reload pet data after event completion
        self.pet1.refresh_from_db()

        # check pet's xp has increased
        self.assertTrue(self.pet1.pet_exp > initial_xp)
