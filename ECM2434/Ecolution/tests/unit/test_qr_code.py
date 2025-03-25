from uuid import uuid4
from Ecolution.models import CustomUser, Event, UserEvent, Pet
from Ecolution.tests.base_test import BaseTestCase
from django.utils import timezone
from django.urls import reverse


class QRUnitTests(BaseTestCase):
    def setUp(self):
        # create a user
        self.user = CustomUser.objects.create_user(username="testuser", password="password")

        # create event with unique QR token
        self.event = Event.objects.create(
            event_name="Test Event",
            description="Test description",
            location="Test location",
            date=timezone.now().date(),
            time=timezone.now().time(),
            unique_token=uuid4()
        )

        # create UserEvent (links user to event)
        self.user_event = UserEvent.objects.create(user=self.user, event=self.event, validated=False)

        # create pet
        self.pet = Pet.objects.create(user=self.user, pet_name="Test Pet", pet_level=1)
        self.user.displayed_pet = self.pet
        self.user.save()

        # login user
        self.client.login(username="testuser", password="password")

        # urls
        self.url_qr = reverse('validate_qr', kwargs={'token': str(self.event.unique_token)})
        self.url_events = reverse('events')

    ## As a user, I can successfully validate an event by scanning the associated QR code
    def test_qr_successfully_validates_user_event(self):
        # check user event hasn't been validated yet
        self.assertFalse(self.user_event.validated)

        # go to validation page
        response = self.client.get(self.url_qr)

        # reload userEvent from the db
        self.user_event.refresh_from_db()

        # check event is now validated
        self.assertTrue(self.user_event.validated)
        self.assertRedirects(response, self.url_events)

    ## As a user, I cannot validate an event by scanning an invalid QR code
    def test_qr_not_validate_if_event_not_found(self):
        # create invalid QR code token
        invalid_token = uuid4()

        # user attempts to validate event
        url = reverse('validate_qr', kwargs={'token': str(invalid_token)})
        response = self.client.get(url)

        # check response results in error due to QR code not being linked to an event
        self.assertEqual(response.status_code, 404)

    ## As a user, I cannot validate an event I have not joined
    def test_qr_not_validate_user_not_joined_event(self):
        # create another event that user has NOT joined
        another_event = Event.objects.create(
            event_name="Another Event",
            description="Another description",
            location="Another location",
            date=timezone.now().date(),
            time=timezone.now().time(),
            unique_token=uuid4()
        )

        # user attempts to validate event they have not joined with (valid) associated QR code
        url = reverse('validate_qr', kwargs={'token': str(another_event.unique_token)})
        response = self.client.get(url)

        # check response is a 404 because the user is not linked to this event
        self.assertEqual(response.status_code, 404)

    ## As a user, I cannot validate an event I have already validated
    def test_user_event_is_not_validated_again_if_already_validated(self):
        # user event is marked as already validated
        self.user_event.validated = True
        self.user_event.save()

        # user attempts to validate event again using associated QR code
        url = reverse('validate_qr', kwargs={'token': str(self.event.unique_token)})
        response = self.client.get(url)

        # check validation value does not change since it's already validated
        self.user_event.refresh_from_db()
        self.assertTrue(self.user_event.validated)

        # check response is a redirect to the events page
        self.assertRedirects(response, self.url_events)

