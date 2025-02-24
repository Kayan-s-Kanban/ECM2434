from django.test import TestCase
from django.urls import reverse
from Ecolution.models import Task, CustomUser, UserTask, Pet

class HomepageIntegrationTests(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password = 'password')

        # create user's pet
        self.pet1 = Pet.objects.create(
            user=self.user1,
            pet_name = "TestPet",
            pet_level = 1,
            pet_exp = 0,  # pet starts with 0 XP
            pet_type = "mushroom"
        )

        # log user in
        self.client.login(username ='testuser', password = 'password')
        response = self.client.get(reverse('home'))

        # create new task
        self.task1 = Task.objects.create(task_name = "Buy groceries", description = "Go to the store and buy food")

    # As a user, I can view my pet name
    def test_homepage_view_pet_name(self):
        response = self.client.get(reverse('home'))

        # check pet name appears
        self.assertContains(response, 'TestPet')

    # As a user, I can view my current tasks
    def test_homepage_current_tasks(self):
        # user is on homepage
        response = self.client.get(reverse('home'))

        # check tasks appear on homepage
        self.assertContains(response, "Buy groceries")
        self.assertContains(response, "Go to the store and buy food")

    # As a user, I can see my points increase after completing a task
    def test_homepage_xp_increase(self):
            # user is on homepage
            response = self.client.get(reverse('home'))

            # make note of user's current XP
            user_xp_current = self.pet1.pet_exp

            # user is on tasks page
            response = self.client.get(reverse('tasks'))

            # user selects task, and selects "Task Completed"
            # add task to user's list
            user_tasks = UserTask.objects.create(user=self.user1, task=self.task1)

            # check task is now in user's list
            self.assertTrue(UserTask.objects.filter(user=self.user1).exists())

            # check task exists in db
            self.assertTrue(Task.objects.filter(task_name="Buy groceries").exists())

            # user marks task as complete
            user_tasks.completed = True
            user_tasks.save()

            # user returns to homepage
            response = self.client.get(reverse('home'))

            # check XP has now increased accordingly
            user_xp_new = self.pet1.pet_exp
            self.assertTrue(user_xp_current < user_xp_new)

    # As a user, I can see my points decrease after removing a completed task
    def test_homepage_xp_decrease(self):
        # user is on homepage
        self.client.get(reverse('home'))

        # make note of user's current XP
        user_xp_current = self.pet1.pet_exp

        # user is on tasks page
        self.client.get(reverse('tasks'))

        # user selects task, and selects "Task Completed"
        # add task to user's list
        user_tasks = UserTask.objects.create(user=self.user1, task=self.task1)

        # check task is now in user's list
        self.assertTrue(UserTask.objects.filter(user=self.user1).exists())

        # check task exists in db
        self.assertTrue(Task.objects.filter(task_name="Buy groceries").exists())

        # user marks task as complete
        user_tasks.completed = True
        user_tasks.save()

        # user returns to homepage
        response = self.client.get(reverse('home'))

        # check XP has now increased accordingly
        user_xp_new_1 = self.pet1.pet_exp
        self.assertTrue(user_xp_current < user_xp_new_1)

        # user removes completed task
        user_tasks.delete()

        # check task is no longer in user's list
        self.assertFalse(UserTask.objects.filter(user = self.user1, task = self.task1).exists())

        # user returns to homepage
        response = self.client.get(reverse('home'))

        # check XP has now increased accordingly
        user_xp_new_2 = self.pet1.pet_exp
        self.assertTrue(user_xp_new_1 < user_xp_new_2)