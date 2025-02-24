from django.test import TestCase
from Ecolution.models import CustomUser
from Ecolution.models import UserTask
from Ecolution.models import Task

class TasksUnitTests(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password = 'password')

        # create a test task
        self.task1 = Task.objects.create(task_name = "Buy groceries", description = "Go to the store and buy food")
        self.task2 = Task.objects.create(task_name = "Task 2", description = "Task description here")

    ## As a user, I can add (pre-defined) tasks to my list
    def test_user_adds_tasks(self):
        # add task to user list
        user_tasks = UserTask.objects.create(user = self.user1, task = self.task1)

        # check task is now in user's list
        self.assertTrue(UserTask.objects.filter(user = self.user1).exists())

    ## As a user, I can remove tasks from my list
    def test_user_removes_tasks(self):
        # add task to user list
        user_task = UserTask.objects.create(user = self.user1, task = self.task1)

        # check task is now in user's list
        self.assertTrue(UserTask.objects.filter(user = self.user1).exists())

        # remove task from list
        user_task.delete()

        # check task is no longer in user's list
        self.assertFalse(UserTask.objects.filter(user = self.user1, task = self.task1).exists())

    ## As a user, I can complete tasks
    def test_user_completes_tasks(self):
        # add task to user list
        user_tasks = UserTask.objects.create(user = self.user1, task = self.task1)

        # check task is now in user's current tasks list
        self.assertTrue(UserTask.objects.filter(user = self.user1).exists())
        self.assertTrue(UserTask.objects.filter(task = self.task1, completed = False).exists())

        # user marks task as "complete"
        user_tasks.completed = True
        user_tasks.save()

        # task no longer appears in current tasks list
        self.assertFalse(UserTask.objects.filter(task = self.task1, completed = False).exists())

        # task now appears in completed tasks list
        self.assertTrue(UserTask.objects.filter(task = self.task1, completed = True).exists())

    ## As a user, I can earn points from completing tasks
    def test_user_earns_points(self):

