from django.test import TestCase
from django.urls import reverse

from Ecolution.models import Task, CustomUser, UserTask


class HomepageTestCase(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # log user in
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('home'))

        # create new task
        self.task1 = Task.objects.create(task_name="Buy groceries", description="Go to the store and buy food")

        # add task to user's list
        user_tasks = UserTask.objects.create(user=self.user1, task=self.task1)

        # check task is now in user's list
        self.assertTrue(UserTask.objects.filter(user=self.user1).exists())

        # check task exists in db
        self.assertTrue(Task.objects.filter(task_name="Buy groceries").exists())

    # As a user, I can view my pet
    def test_homepage_view_pet(self):
        response = self.client.get(reverse('home'))

        # check pet name appears
        self.assertContains(response, 'Pet Name')

        # TODO: check pet image appears

    # As a user, I can view my current tasks
    def test_homepage_current_tasks(self):
        # user is on homepage
        response = self.client.get(reverse('home'))

        # check tasks appear on homepage
        self.assertContains(response, "Buy groceries")
        self.assertContains(response, "Go to the store and buy food")

    # As a user, I can open and close the menu
    def test_homepage_menu(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('home'))

        # user selects menu button
        response = self.client.post(reverse('home'), {'show menu': True}, follow=True)  # TODO: check syntax

        # menu opens up
        self.assertContains(response, 'menu')

    # As a user, I can view my XP
    def test_homepage_xp(self):
        response = self.client.get(reverse('home'))
        # check XP bar appears on user page (even if 0 xp)
        self.assertContains(response, 'xp')

    # As a user, I can see my points increase after completing a task
    def test_homepage_xp_increase(self):
        # user is on homepage
        response = self.client.get(reverse('home'))

        # TODO: make note of user's current XP

        # user is on tasks page
        response = self.client.get(reverse('tasks'))

        # TODO: user selects task, and selects "Task Completed"

        # user returns to homepage
        response = self.client.get(reverse('home'))

        # TODO: check XP has now increased accordingly

    # As a user, I can see my points decrease after removing a completed task
    def test_homepage_xp_decrease(self):
        # user is on homepage
        response = self.client.get(reverse('home'))

        # TODO: make note of user's current XP

        # user is on tasks page
        response = self.client.get(reverse('tasks'))

        # TODO: user selects task, and deselects "Task Completed"/removes task?

        # user returns to homepage
        response = self.client.get(reverse('home'))

        # TODO: check XP has now decreased accordingly