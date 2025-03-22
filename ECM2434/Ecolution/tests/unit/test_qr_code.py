from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Event, UserEvent, Pet
from django.utils import timezone
from uuid import uuid4


class QRValidationTests(TestCase):

    def setUp(self):
        # Create a CustomUser to log in
        self.user = CustomUser.objects.create_user(username="testuser", password="password")

        # Create an event with a unique token
        self.event = Event.objects.create(
            event_name="Test Event",
            description="Test description",
            location="Test location",
            date=timezone.now().date(),
            time=timezone.now().time(),
            unique_token=uuid4()
        )

        # Create a UserEvent linking the user to the event
        self.user_event = UserEvent.objects.create(user=self.user, event=self.event, validated=False)

        # Create a Pet for the user to have a displayed pet (Optional based on the view functionality)
        self.pet = Pet.objects.create(user=self.user, pet_name="Test Pet", pet_level=1)
        self.user.displayed_pet = self.pet
        self.user.save()

        # Login the user
        self.client.login(username="testuser", password="password")

    def test_validate_qr_successfully_validates_user_event(self):
        # Ensure the user_event is not validated yet
        self.assertFalse(self.user_event.validated)

        # Trigger the validation view
        url = reverse('validate_qr', kwargs={'token': str(self.event.unique_token)})
        response = self.client.get(url)

        # Reload the UserEvent from the database to check if it was validated
        self.user_event.refresh_from_db()

        # Ensure the event is now validated
        self.assertTrue(self.user_event.validated)
        self.assertRedirects(response, reverse('events'))

    def test_validate_qr_redirects_if_event_not_found(self):
        # Test the case where an invalid token is provided
        invalid_token = uuid4()
        url = reverse('validate_qr', kwargs={'token': str(invalid_token)})
        response = self.client.get(url)

        # Ensure the response is a 404 because the event doesn't exist
        self.assertEqual(response.status_code, 404)

    def test_validate_qr_redirects_if_user_event_not_found(self):
        # Create an event with a valid token but no associated UserEvent for the logged-in user
        another_event = Event.objects.create(
            event_name="Another Event",
            description="Another description",
            location="Another location",
            date=timezone.now().date(),
            time=timezone.now().time(),
            unique_token=uuid4()
        )
        url = reverse('validate_qr', kwargs={'token': str(another_event.unique_token)})
        response = self.client.get(url)

        # Ensure the response is a 404 because the user is not linked to this event
        self.assertEqual(response.status_code, 404)

    def test_user_event_is_not_validated_again_if_already_validated(self):
        # Mark the user_event as validated
        self.user_event.validated = True
        self.user_event.save()

        # Trigger the validation view again
        url = reverse('validate_qr', kwargs={'token': str(self.event.unique_token)})
        response = self.client.get(url)

        # Ensure the validation does not change since it's already validated
        self.user_event.refresh_from_db()
        self.assertTrue(self.user_event.validated)

        # Ensure the response is a redirect to the events page
        self.assertRedirects(response, reverse('events'))

