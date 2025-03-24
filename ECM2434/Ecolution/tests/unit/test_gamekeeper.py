import json

from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Task

class GameKeeperUnitTests(TestCase):
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

        # urls
        self.url_task_list = reverse("gamekeeper_tasks")
        self.url_create_task = reverse("add_gamekeeper_task")
        self.url_delete_task = reverse("delete_gamekeeper_task", args=[self.task.task_id])

    ## As a gamekeeper, I can access my task list
    def test_gamekeeper_can_view_tasks(self):
        # gamekeeper is directed to their task list
        response = self.client.get(self.url_task_list)
        self.assertEqual(response.status_code, 200)

        # check that the task list displayed is specifically the gamekeeper task list
        self.assertTemplateUsed(response, "gamekeeper_tasks.html")
        self.assertIn("tasks", response.context)
        self.assertIn("points", response.context)
        self.assertEqual(response.context["tasks"].count(), 1)

    ## As a user, I cannot access gamekeeper tasks
    def test_non_gamekeeper_cannot_view_tasks(self):
        # logout gamekeeper and login regular user
        self.client.logout()
        self.client.login(username="regular_user", password="password123")

        # user tries to access gamekeeper tasks page
        response = self.client.get(self.url_task_list)
        self.assertEqual(response.status_code, 403)  # should return "Forbidden"

    ## As a gamekeeper, I can create a new task
    def test_gamekeeper_can_create_task(self):
        new_task_data = {
            "task_name": "New Task",
            "description": "This is a new gamekeeper task",
            "points_given": 50,
            "xp_given": 50
        }

        # gamekeeper creates task through JSON request
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

        # non-gamekeeper user attempts to create new gamekeeper task
        response = self.client.post(self.url_create_task, json.dumps(new_task_data), content_type="application/json")

        # check that user is forbidden from creating new task, and that new task is NOT created
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Task.objects.filter(task_name="Hacker Task").exists())

    ## As a gamekeeper, I cannot create a task with invalid details
    def test_task_creation_fails_with_invalid_json(self):
        # gamekeeper attempts to create task with invalid JSON data
        response = self.client.post(self.url_create_task, "invalid json", content_type="application/json")

        # attempt is not successful
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"status": "error", "message": "Invalid JSON data."})

    ## As a gamekeeper, I can delete tasks I've created
    def test_gamekeeper_can_delete_task(self):
        # ensure gamekeeper is logged in
        self.client.login(username="gamekeeper", password="password123")

        # check task exists before deleting
        self.assertTrue(Task.objects.filter(task_id = self.task.task_id).exists())

        # gamekeeper deletes task
        response = self.client.post(self.url_delete_task)

        # check task is deleted
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(task_id = self.task.task_id).exists())

    ## As a user, I cannot delete a gamekeeper's task
    def test_non_gamekeeper_cannot_delete_task(self):
        # logout gamekeeper and login regular user
        self.client.logout()
        self.client.login(username="regular_user", password="password123")

        # check task exists before deleting
        self.assertTrue(Task.objects.filter(task_id=self.task.task_id).exists())

        # user attempts to delete task
        response = self.client.post(self.url_delete_task)

        # check task is not deleted and access is forbidden
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Task.objects.filter(task_id=self.task.task_id).exists())
        self.assertIn("Forbidden", response.content.decode())

    ## As a gamekeeper, I cannot delete a task I don't own
    def test_gamekeeper_cannot_delete_task_they_dont_own(self):
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

        # try to delete the task owned by the regular user
        self.client.login(username="gamekeeper", password="password123")

        response = self.client.post(delete_url_for_another_user_task)

        # check deletion was not successful
        self.assertEqual(response.status_code, 404)

        # check task still exists
        self.assertTrue(Task.objects.filter(task_id=another_user_task.task_id).exists())

    ## Invalid request for deleting task results in an error
    def test_invalid_request_method(self):
        # ensure gamekeeper is logged in
        self.client.login(username="gamekeeper", password="password123")

        # attempt to delete task using GET request instead of POST
        response = self.client.get(self.url_delete_task)

        # check that deletion was not successful
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Invalid request method.'})