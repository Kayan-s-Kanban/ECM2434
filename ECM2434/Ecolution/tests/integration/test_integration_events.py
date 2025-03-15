from django.test import TestCase
from django.urls import reverse
from django.db import connection
from Ecolution.models import CustomUser, Event, Pet

class EventsTestCase(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.client.login(username = 'testuser', password = 'password')
        self.pet1 = Pet.objects.create(user = self.user1, pet_name = 'Test Pet', pet_exp = 10)

    # As a user, I can earn points from completing events
    def test_earn_points_from_event(self):
        # create test event
        self.event1 = Event.objects.create(event_name = 'Test Event')

        user_from_db = CustomUser.objects.get(username = 'testuser')
        print("DB Check - Points:", user_from_db.points)

        # ensure the event was created and saved
        self.assertEqual(Event.objects.count(), 1)
        created_event = Event.objects.first()
        self.assertEqual(created_event.event_name, 'Test Event')

        print("Event exists")

        # refresh user data before checking points
        self.user1.refresh_from_db()
        initial_points = self.user1.points
        print("Initial Points:", initial_points)

        user_from_db = CustomUser.objects.get(username='testuser')
        print("DB Check - Points:", user_from_db.points)

        # user completes event
        response = self.client.post('events/complete/', {'event_id': self.event1.event_id})

        # reload user data after event completion
        connection.close()
        self.user1.refresh_from_db()
        print("Final Points:", self.user1.points)

        user_from_db = CustomUser.objects.get(username = 'testuser')
        print("DB Check - Points:", user_from_db.points)

        # check user points have increased
        self.assertGreater(self.user1.points, initial_points)

        # ensure the response was successful (status code 200)
        self.assertEqual(response.status_code, 200)

    # As a user, I can earn XP from completing events
    def test_earn_xp_from_event(self):
        # check xp at start
        initial_xp = self.pet1.pet_exp

        print("Initial XP:", initial_xp)

        # create test event
        self.event1 = Event.objects.create(
            event_name='Test Event'
        )

        # Ensure the event was created and saved
        self.assertEqual(Event.objects.count(), 1)  # Check that 1 event exists in the database
        created_event = Event.objects.first()  # Get the first (and only) event created
        self.assertEqual(created_event.event_name, 'Test Event')  # Ensure the event name matches

        print("Event exists")

        # user completes event
        self.client.post(reverse('complete_event'), {'event': self.event1})

        # reload user + pet data after event completion
        self.user1.refresh_from_db()
        self.pet1.refresh_from_db()
        self.event1.refresh_from_db()

        print("Final XP:", self.pet1.pet_exp)

        # reload pet data after event completion
        self.pet1.refresh_from_db()

        # check pet's xp has increased
        self.assertTrue(self.pet1.pet_exp > initial_xp)

    def test_updating_user_points(self):
        """Test that updating a user's points works correctly"""
        self.user1.points += 5
        self.user1.save()

        updated_user = CustomUser.objects.get(username = 'testuser')
        self.assertEqual(updated_user.points, 5)

        self.user1.points += 10
        self.user1.save()

        updated_user = CustomUser.objects.get(username='testuser')
        self.assertEqual(updated_user.points, 15)

    # As a user, I can scan a valid QR code

    # As a user, I can scan a valid QR code and be redirected to the associated event

    # As a user, I can mark tasks off as complete
