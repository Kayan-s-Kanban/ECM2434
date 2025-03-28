from datetime import timedelta
from django.utils import timezone
from unittest.mock import patch
from django.urls import reverse
from Ecolution.models import Event, Pet, UserEvent, Task, UserTask
from Ecolution.views import User
from Ecolution.tests.base_test import BaseTestCase


class EventsIntegrationTests(BaseTestCase):
    def setUp(self):
        # create user
        self.user1 = User.objects.create_user(username="testuser", password="password", is_gamekeeper=True)

        # login user
        self.client.login(username="testuser", password="password")

        # create event
        self.event = Event.objects.create(
            event_name="Test Event",
            description="An event",
        )

        # create tasks for event
        self.task1 = Task.objects.create(
            task_name="Task 1",
            description="Description for task 1",
            points_given=10,
            xp_given=20,
            event=self.event
        )

        self.task2 = Task.objects.create(
            task_name="Task 2",
            description="Description for task 2",
            points_given=15,
            xp_given=25,
            event=self.event
        )

        # create UserEvent relationship
        self.user_event = UserEvent.objects.create(user=self.user1, event=self.event)

        # create user pet
        self.pet1 = Pet.objects.create(user=self.user1, pet_exp=50, pet_level=1)

        # assign the pet as the user's displayed pet
        self.user1.displayed_pet = self.pet1
        self.user1.save()

        # urls
        self.url_leave = reverse('leave_event')
        self.url_create = reverse('create_event')
        self.url = reverse('events')
        self.url_complete = reverse("complete_event")
        self.url_get_tasks = reverse('get_event_tasks', args=[self.event.event_id])

    # As a user, I can earn points from completing event tasks
    def test_earn_points_xp_from_event(self):
        # check xp at start
        initial_xp = self.pet1.pet_exp

        # make sure that one 1 event object exists
        self.assertEqual(Event.objects.count(), 1)
        created_event = Event.objects.first()  # get the first (and only) event created
        self.assertEqual(created_event.event_name, 'Test Event')  # check event name matches

        # set event as validated by user
        self.user_event.validated = True
        self.user_event.save()

        # Create a completed UserTask for each task associated with the event
        UserTask.objects.create(user=self.user1, task=self.task1, completed=True, date=timezone.now().date())
        UserTask.objects.create(user=self.user1, task=self.task2, completed=True, date=timezone.now().date())

        # user completes event
        self.client.post(reverse('complete_event'), {'event_id': self.event.event_id})

        # reload user + pet data after event completion
        self.user1.refresh_from_db()
        self.pet1.refresh_from_db()

        # reload pet data after event completion
        self.pet1.refresh_from_db()

        # check pet's xp has increased
        self.assertEqual(self.pet1.pet_exp, initial_xp + self.event.total_xp)

        # check user's points has increased
        self.assertEqual(self.user1.points, 25)

    ## As a user, I can leave an event
    def test_leave_event_success(self):
        self.client.login(username="testuser", password="password")

        # user leaves event
        response = self.client.post(self.url_leave, {"event_id": self.event.event_id})

        # check user has successfully left event
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"success": True})

        # check the UserEvent is deleted after the user leaves the event
        self.assertFalse(UserEvent.objects.filter(user=self.user1, event=self.event).exists())

    ## As a user, I cannot complete an event that does not exist in the database
    def test_leave_event_event_does_not_exist(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(self.url_leave, {"event_id": 99999})

        # check that an error message is returned
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"success": False, "message": "No Event matches the given query."})

    ## As a user, I cannot complete an event that does not exist
    def test_invalid_event_id(self):
        self.client.login(username='testuser', password='password')

        data = {"event_id": 9900067576463342567897}
        response = self.client.post(self.url_complete, data)

        # check that event does not exist
        self.assertEqual(response.status_code, 200)

    def test_leave_event_invalid_method(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url_leave)

        # check error message is returned
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"success": False, "message": "Invalid request"})

    def test_leave_event_exception_handling(self):
        # simulate an exception during the filter query
        with patch('Ecolution.views.UserEvent.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Unexpected error")

            self.client.login(username="testuser", password="password")
            response = self.client.post(self.url_leave, {"event_id": self.event.event_id})

            # check error message is returned
            self.assertJSONEqual(str(response.content, encoding='utf8'),
                                 {"success": False, "message": "Unexpected error"})

    ## As an admin, I can successfully create a new event
    def test_create_event_success(self):
        data = {
            "event_name": "Test Event",
            "description": "A test event",
            "location": "Test Location",
            "date": (timezone.now() + timedelta(days=1)).date(),  # Ensure future date
            "time": "12:00:00",  # Use a valid time format
        }
        # check event has been successfully created
        response = self.client.post(self.url_create, data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data.get("status"), "success")

    ## As an admin, I cannot create an event with missing fields
    def test_create_event_missing_fields(self):
        data = {
            "event_name": "Test Event",  # Missing 'date' and 'time'
            "description": "A test event",
            "location": "Test Location",
        }

        response = self.client.post(self.url_create, data)

        # check the response is an error with the appropriate database integrity error message
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data["status"], "error")
        self.assertTrue("Database Integrity Error" in response_data["message"])

    ## As an admin, I cannot create an event that violates the database integrity rules
    def test_create_event_database_integrity_error(self):
        invalid_data = {
            "event_name": "Test Event",
        }

        response = self.client.post(self.url_create, invalid_data)

        # check that request is recognized as "bad"
        self.assertEqual(response.status_code, 400)

        # check error message contains the specific database integrity error
        response_data = response.json()
        expected_error_message = "NOT NULL constraint failed: Ecolution_event.description"
        self.assertIn(expected_error_message, response_data.get("message"))

    def test_create_event_invalid_method(self):
        response = self.client.get(self.url_create)

        # check response returns an error for invalid method
        self.assertEqual(response.status_code, 400)

    def test_complete_event_success(self):
        # make sure the user_event is validated
        self.user_event.validated = True
        self.user_event.save()

        data = {"event_id": self.event.event_id}
        response = self.client.post(self.url_complete, data)

        # check the response
        self.assertJSONEqual(str(response.content, encoding="utf8"), {"success": True})

    ## As a user, I cannot complete an event without validation
    def test_event_not_validated(self):
        # mark event as not validated
        self.user_event.validated = False
        self.user_event.save()

        data = {"event_id": self.event.event_id}

        # send a valid request
        response = self.client.post(self.url_complete, data)

        self.assertJSONEqual(str(response.content, encoding="utf8"),
                             {"success": False, "message": "Event not validated. Please ask the event organiser for the QR code and go to the QR code scanner page."})
        self.assertFalse(self.user_event.validated)

    ## As a user, I can complete a validated event
    def test_event_validated_completed(self):
        self.user_event.validated = True
        self.user_event.save()

        data = {"event_id": self.event.event_id}
        response = self.client.post(self.url_complete, data)

        # check user has been able to successfully complete event
        self.assertJSONEqual(str(response.content, encoding="utf8"), {"success": True})

    ## As a user, I cannot complete an event I have not joined
    def test_user_event_not_found(self):
        # delete the UserEvent to simulate the user not being part of the event
        self.user_event.delete()

        # user completes event
        data = {"event_id": self.event.event_id}
        response = self.client.post(self.url_complete, data)

        # check response code is 200
        self.assertEqual(response.status_code, 200)

        # check message indicating the absence of UserEvent
        self.assertIn("No UserEvent matches the given query.", response.json().get("message", ""))

    # As a user, I can view the tasks for an event I have joined
    def test_get_event_tasks_success(self):
        # log in as the user
        self.client.login(username='testuser', password='password')

        # send GET request to fetch the tasks for the event
        response = self.client.get(self.url_get_tasks)
        self.assertEqual(response.status_code, 200)

        # check if response contains the tasks data
        response_data = response.json()
        self.assertIn('tasks', response_data)
        self.assertEqual(len(response_data['tasks']), 2)

        # check that tasks data matches the expected structure
        self.assertEqual(response_data['tasks'][0]['task_name'], "Task 1")
        self.assertEqual(response_data['tasks'][1]['task_name'], "Task 2")
        self.assertEqual(response_data['tasks'][0]['points_given'], 10)
        self.assertEqual(response_data['tasks'][1]['xp_given'], 25)

