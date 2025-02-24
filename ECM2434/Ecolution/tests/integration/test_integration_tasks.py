from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, UserTask, Task

class TaskIntegrationTests(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password='password')

        # create a test task
        self.task = Task.objects.create(task_name = "Buy groceries", description = "Go to the store and buy food")
        self.task = Task.objects.create(task_name = "Task 1", description = "Task description here")

    ## As a user, I can create my own tasks
    def test_user_creates_tasks(self):
        # login
        self.client.login(username = 'testuser', password = 'password')

        # new task data
        task_data = {
            'task_name': 'Go for a walk',
            'description': 'Take a walk through campus today.'
        }

        # user request to create new task
        response = self.client.post('/tasks/create/', task_data)  # TODO: ensure correct create task endpoint

        # check task exists in the DB
        self.assertIsNotNone(Task.objects.get(task_name = 'Go for a walk'))

        # check task exists in user's list
        self.assertEqual(UserTask.user, self.user1)  # TODO: fix reference
        self.assertTrue(UserTask.objects.filter(creator = self.user1, task_name = 'Go for a walk').exists())  # TODO: fix reference

    ## As a user, I can delete my user-created tasks
    def test_user_deletes_tasks(self):
        # login
        self.client.login(username='testuser', password='password')

        # new task data
        task_data = {
            'task_name': 'Go for a walk',
            'description': 'Take a walk through campus today.'
        }

        # user request to create new task
        response = self.client.post('/tasks/create/', task_data)  # TODO: ensure correct create task endpoint

        # check task has been created
        self.assertEqual(response.status_code, 201)  # TODO: ensure correct status code

        # check task exists in the DB
        task = Task.objects.get(task_name='Go for a walk')

        # check task exists in user's list
        user_task = UserTask.objects.get(user = self.user, task = task)
        self.assertTrue(UserTask.objects.filter(user = self.user, task = task).exists())

        # user deletes task
        delete_url = f'/tasks/{task.id}/delete/'  # TODO: ensure correct delete URL format
        response = self.client.post(delete_url)

        # task no longer appears in the user's list
        self.assertFalse(UserTask.objects.filter(user = self.user, task = task).exists())

        # task no longer appears in the database
        self.assertIsNone(Task.objects.get(task_name = 'Go for a walk'))

        # check the response code for successful deletion
        self.assertEqual(response.status_code, 200)  # TODO: ensure correct success status code for deletion

    ## As a user, I cannot view other users' created tasks
    def test_created_tasks_visibility(self):
        # create a second user
        self.user2 = CustomUser.objects.create_user(username = 'another_user', password = 'password')

        # create tasks for both users
        task1 = Task.objects.create(creator = self.user1, task_name = "Buy groceries", description = "Go to the store and buy food")
        task2 = Task.objects.create(creator = self.user2, task_name = "Complete homework", description = "Finish math problems")

        # first user can only view their own task (task1)
        user1_tasks = Task.objects.filter(creator = self.user1)
        self.assertIn(task1, user1_tasks)
        self.assertNotIn(task2, user1_tasks)
        self.client.logout()

        # second user can only view their own task (task2)
        self.client.login(username = 'another_user', password = 'password')
        user2_tasks = Task.objects.filter(creator = self.user2)
        self.assertIn(task2, user2_tasks)
        self.assertNotIn(task1, user2_tasks)

    ## As a user, I can view my completed tasks
    def test_view_completed_tasks(self):
        self.client.login(username = 'testuser', password = 'password')
        response = self.client.get('/tasks/complete/')
        self.assertEqual(response.status_code, 200)

    ## As a user, I can view my current tasks on the tasks page
    def test_view_current_tasks(self):
        response = self.client.get('/tasks/current/')
        self.assertEqual(response.status_code, 200)