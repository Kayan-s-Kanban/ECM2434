from unittest import TestCase

from django.urls import reverse
from Ecolution.models import CustomUser
from Ecolution.models import UserTask
from Ecolution.models import Task

class TaskIntegrationTests(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # create a test task
        self.task = Task.objects.create(task_name="Buy groceries", description="Go to the store and buy food")
        self.task = Task.objects.create(task_name="Task 1", description="Task description here")

    ## As a user, I can create my own tasks
    ## TODO: update based on user created task functionality/flow
    def test_user_creates_tasks(self):
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
        self.assertEqual(UserTask.user, self.user)  # TODO: fix reference
        self.assertTrue(UserTask.objects.filter(user=self.user, task=task).exists())  # TODO: fix reference

    ## As a user, I can view task details
    def test_user_view_task(self):
        self.client.login(username = 'testuser', password = 'password')

    ## As a user, I can search for tasks
    ## TODO: update based on search functionality (if implemented)
    def test_task_search(self):
        self.client.login(username = 'testuser', password = 'password')

        # navigate to tasks page
        response = self.client.get('/tasks/search/') # TODO: ensure correct URL + search function exists

        # search for existing task "Buy groceries"
        response = self.client.get('/tasks/', {'q': 'Buy groceries'})

        # check responses
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buy groceries')
        self.assertNotContains(response, 'Task 1')

    ## As a user, I cannot view other users' created tasks
    def test_created_tasks_visibility(self):
        # create a second user
        self.user2 = CustomUser.objects.create_user(username='another_user', password='password')

        # create tasks for both users
        task1 = Task.objects.create(user=self.user1, task_name="Buy groceries", description="Go to the store and buy food")
        task2 = Task.objects.create(user=self.user2, task_name="Complete homework", description="Finish math problems")

        # first user can only view their own task (task1)
        user1_tasks = Task.objects.filter(user = self.user1)
        self.assertIn(task1, user1_tasks)
        self.assertNotIn(task2, user1_tasks)
        self.client.logout()

        # second user can only view their own task (task2)
        self.client.login(username='another_user', password='password')
        user2_tasks = Task.objects.filter(user = self.user2)
        self.assertIn(task2, user2_tasks)
        self.assertNotIn(task1, user2_tasks)

    ## As a user, I can view my completed tasks
    def test_view_completed_tasks(self):
        self.client.login(username = 'testuser', password = 'password')
        response = self.client.get('/tasks/complete/')
        self.assertEqual(response.status_code, 200)

    ## As a user, I can view my current tasks on the tasks page
    def test_view_current_tasks(self):
        self.client.login(username = 'testuser', password = 'password')
        response = self.client.get('/tasks/current/')
        self.assertEqual(response.status_code, 200)

    ## As a user, I can earn points from completing tasks
    # def test_task_earn_points(self):