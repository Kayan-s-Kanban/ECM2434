from django.test import TestCase
from django.urls import reverse
from Ecolution.models import Task, CustomUser, UserTask, Pet

class HomepageIntegrationTests(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.user1.points = 10
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
        self.task1.points = 50

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

    ## As a user, I can earn points from completing tasks
    def test_homepage_points_increase(self):
        # user is on homepage
        response = self.client.get(reverse('home'))

        # make note of user's current points
        user_points_current = self.user1.points
        print(f"User Points Before Task: {user_points_current}")  # Debug: print user's points before task completion

        # user is on tasks page
        response = self.client.get(reverse('tasks'))

        # user adds task to their list
        user_tasks = UserTask.objects.create(user=self.user1, task=self.task1)
        print(f"Task Added: {user_tasks}")  # Debug: print the task that was added

        # check task is now in user's list
        self.assertTrue(UserTask.objects.filter(user=self.user1).exists())
        self.assertTrue(Task.objects.filter(task_name="Buy groceries").exists())

        # simulate clicking "Complete" button (assuming it's a POST request to mark task completed)
        response = self.client.post('complete_task')  # POST request to mark task as completed
        print(f"Task Marked Completed: {response.status_code}")  # Debug: print status code after completing the task

        # user returns to homepage
        response = self.client.get(reverse('home'))

        # check XP has now increased accordingly
        user_points_new = self.user1.points
        print(f"User Points After Task: {user_points_new}")  # Debug: print user's points after task completion

        # assert points have increased
        self.assertTrue(user_points_new > user_points_current,
                        f"Expected points to be greater after completing the task. Before: {user_points_current}, After: {user_points_new}")
