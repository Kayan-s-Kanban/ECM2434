import json

from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Task

class GameKeeperTestCase(TestCase):
    def setUp(self):
        # create a gamekeeper user
        self.gamekeeper = CustomUser.objects.create_user(username="gamekeeper", password="password123", is_gamekeeper=True)
        self.client.login(username="gamekeeper", password="password123")

        # create a non-gamekeeper user
        self.user = CustomUser.objects.create_user(username="regular_user", password="password123", is_gamekeeper=False)

        # create task assigned to gamekeeper
        self.task = Task.objects.create(
            task_name="Test Task",
            description="A test task",
            points_given=30,
            xp_given=30,
            predefined=True,
            creator=self.gamekeeper
        )

        self.url_task_list = reverse("gamekeeper_tasks")
        self.url_create_task = reverse("add_gamekeeper_task")
        self.url_delete_task = reverse("delete_gamekeeper_task", args=[self.task.task_id])

    ## As a gamekeeper, I can access my task list
    def test_gamekeeper_can_view_tasks(self):
        response = self.client.get(self.url_task_list)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gamekeeper_tasks.html")
        self.assertIn("tasks", response.context)
        self.assertIn("points", response.context)
        self.assertEqual(response.context["tasks"].count(), 1)

    ## As a user, I cannot access gamekeeper tasks
    def test_non_gamekeeper_cannot_view_tasks(self):
        self.client.logout()
        self.client.login(username="regular_user", password="password123")
        response = self.client.get(self.url_task_list)
        self.assertEqual(response.status_code, 403)  # Should return Forbidden

    ## As a gamekeeper, I can create a new task
    def test_gamekeeper_can_create_task(self):
        new_task_data = {
            "task_name": "New Task",
            "description": "This is a new gamekeeper task",
            "points_given": 50,
            "xp_given": 50
        }

        response = self.client.post(self.url_create_task, json.dumps(new_task_data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Task.objects.filter(task_name="New Task").exists())

    ## As a user, I cannot create a new gamekeeper task
    def test_non_gamekeeper_cannot_create_task(self):
        self.client.logout()
        self.client.login(username="regular_user", password="password123")

        new_task_data = {
            "task_name": "Hacker Task",
            "description": "This should not be created",
            "points_given": 10,
            "xp_given": 10
        }

        response = self.client.post(self.url_create_task, json.dumps(new_task_data), content_type="application/json")
        self.assertEqual(response.status_code, 403)  # Forbidden
        self.assertFalse(Task.objects.filter(task_name="Hacker Task").exists())

    ## As a gamekeeper, I cannot create a task with invalid details
    def test_task_creation_fails_with_invalid_json(self):
        response = self.client.post(self.url_create_task, "invalid json", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"status": "error", "message": "Invalid JSON data."})

    def test_task_creation_fails_with_invalid_method(self):
        response = self.client.get(self.url_create_task)
        self.assertEqual(response.status_code, 405)

    def test_gamekeeper_can_delete_task(self):
        """Test that a GameKeeper can delete a task."""
        self.client.login(username="gamekeeper", password="password123")

        response = self.client.post(self.url_delete_task)

        # Check that the task is deleted
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})
        self.assertFalse(Task.objects.filter(task_id=self.task.task_id).exists())

    def test_non_gamekeeper_cannot_delete_task(self):
        """Test that a non-GameKeeper user cannot delete a task."""
        self.client.login(username="regular_user", password="password123")

        response = self.client.post(self.url_delete_task)

        # Check that the task is not deleted and access is forbidden
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')  # Ensure it's HTML response
        self.assertIn("Forbidden", response.content.decode())

    def test_gamekeeper_cannot_delete_task_they_dont_own(self):
        """Test that a GameKeeper cannot delete a task they don't own."""
        # create task for another user
        another_user_task = Task.objects.create(
            task_name="Another Task",
            description="A task owned by another user",
            points_given=30,
            xp_given=30,
            predefined=True,
            creator=self.user
        )
        delete_url_for_another_user_task = reverse("delete_gamekeeper_task", args=[another_user_task.task_id])

        # Try to delete the task owned by the regular user
        self.client.login(username="gamekeeper", password="password123")

        response = self.client.post(delete_url_for_another_user_task)

        # check deletion was not successful
        self.assertEqual(response.status_code, 404)

    def test_invalid_request_method(self):
        """Test that a non-POST request results in an error."""
        self.client.login(username="gamekeeper", password="password123")

        response = self.client.get(self.url_delete_task)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/json')  # Ensure it's JSON response
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Invalid request method.'})