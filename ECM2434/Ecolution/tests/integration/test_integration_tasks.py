from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, UserTask, Task, Pet
from Ecolution.views import User

class TaskIntegrationTests(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # create a different user (using a unique username)
        self.other_user = CustomUser.objects.create_user(username='otheruser2', password='password')

        # create a test task (without a creator so it’s considered a predefined task)
        self.task = Task.objects.create(
            task_name="Buy groceries",
            description="Go to the store and buy food",
            points_given=100,
            xp_given=20
        )

        self.task1 = Task.objects.create(
            task_name="Task 1",
            description="Task description here",
            points_given=100,
            xp_given=20
        )

        # create a UserTask assigned to the user
        self.user_task = UserTask.objects.create(user=self.user1, task=self.task)
        self.other_user_task = UserTask.objects.create(user=self.other_user, task=self.task1)

        # create a pet for the user and assign it as displayed_pet
        self.pet = Pet.objects.create(user=self.user1, pet_name="TestPet", pet_level=1, pet_exp=40, pet_type="mushroom")
        self.user1.displayed_pet = self.pet
        self.user1.save()

    ## As a user, I can create my own tasks
    def test_user_creates_tasks(self):
        # login (if not already logged in)
        self.client.login(username='testuser', password='password')

        # new task data
        task_data = {
            'task_name': 'Go for a walk',
            'description': 'Take a walk through campus today.'
        }

        # use the add_task endpoint (adjusted to use reverse)
        response = self.client.post(reverse("add_task"), task_data)
        self.assertEqual(response.status_code, 200)

        # check task exists in the DB with the correct creator
        created_task = Task.objects.get(task_name='Go for a walk')
        self.assertEqual(created_task.creator, self.user1)

        # check that a UserTask linking the user and task exists
        self.assertTrue(UserTask.objects.filter(user=self.user1, task=created_task).exists())

    ## As a user, I can delete my user-created tasks
    def test_user_deletes_tasks(self):
        # use the delete_task endpoint
        delete_url = reverse('delete_task', args=[self.user_task.id])
        response = self.client.post(delete_url)

        # task should no longer appear in the user's UserTask list
        self.assertFalse(UserTask.objects.filter(user=self.user1, task=self.task).exists())

        # For deletion, we assume that the task (if user-created) is removed from UserTask only;
        # if your app deletes the Task entirely, you can check with:
        # self.assertRaises(Task.DoesNotExist, Task.objects.get, task_name='Buy groceries')

        # check the response code for successful deletion
        self.assertEqual(response.status_code, 200)

    ## As a user, I cannot view other users' created tasks
    def test_created_tasks_visibility(self):
        # create a second user and tasks for both users
        self.user2 = CustomUser.objects.create_user(username='another_user', password='password')
        task1 = Task.objects.create(creator=self.user1, task_name="Buy groceries", description="Go to the store and buy food")
        task2 = Task.objects.create(creator=self.user2, task_name="Complete homework", description="Finish math problems")

        # first user can only view their own task (task1)
        user1_tasks = Task.objects.filter(creator=self.user1)
        self.assertIn(task1, user1_tasks)
        self.assertNotIn(task2, user1_tasks)
        self.client.logout()

        # second user can only view their own task (task2)
        self.client.login(username='another_user', password='password')
        user2_tasks = Task.objects.filter(creator=self.user2)
        self.assertIn(task2, user2_tasks)
        self.assertNotIn(task1, user2_tasks)

    ## As a user, I can view my completed tasks -- UPDATE TEST
    def test_view_completed_tasks(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)

    ## As a user, I can view my current tasks on the tasks page -- UPDATE TEST
    def test_view_current_tasks(self):
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)

    ## As a user, I cannot create a custom task with the same name as another
    def test_existing_task_creation_prevention(self):
        Task.objects.create(task_name="Duplicate Task", description="Test Desc", creator=self.user1)

        response = self.client.post(reverse("add_task"), {
            "task_name": "Duplicate Task",
            "description": "Test Desc",
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["message"], "You already created a custom task with that title.")

    # As a user, I can create new tasks
    def test_new_task_creation(self):
        response = self.client.post(reverse("add_task"), {
            "task_name": "New Task",
            "description": "Task description",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertTrue(Task.objects.filter(task_name="New Task", creator=self.user1).exists())

    def test_user_task_creation(self):
        task = Task.objects.create(task_name="User Task", description="Test Desc", creator=self.user1)

        response = self.client.post(reverse("add_task"), {
            "task_id": task.task_id,  # changed from task.id to task.task_id
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserTask.objects.filter(user=self.user1, task=task).exists())

    def test_duplicate_user_task_error(self):
        """Test that adding the same task twice returns an error."""
        task = Task.objects.create(task_name="Duplicate User Task", description="Test Desc", creator=self.user1)
        UserTask.objects.create(user=self.user1, task=task)

        response = self.client.post(reverse("add_task"), {
            "task_id": task.task_id,  # use task.task_id
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["message"], "You have already completed this task today!")

    ## As a user, I can add a task and receive the correct response format
    def test_success_response_format(self):
        response = self.client.post(reverse("add_task"), {
            "task_name": "Success Task",
            "description": "Testing response format",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertIn("task_name", response.json())
        self.assertIn("description", response.json())

    # invalid request method (GET) does not create task
    def test_invalid_request_method(self):
        response = self.client.get(reverse("add_task"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")

    # deleted tasks are successfully removed from database
    def test_delete_task_success(self):
        response = self.client.post(reverse('delete_task', args=[self.user_task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, 'utf8'), {'status': 'success'})
        with self.assertRaises(UserTask.DoesNotExist):
            UserTask.objects.get(id=self.user_task.id)

    ## As a user, I cannot delete pre-defined tasks (or tasks not assigned to them)
    def test_delete_task_not_found(self):
        # Create a different user and assign a task to them
        other_user = CustomUser.objects.create_user(username='not_testuser', password='password')
        other_user_task = UserTask.objects.create(user=other_user, task=self.task)
        # attempt to delete the task with the incorrect user
        response = self.client.post(reverse('delete_task', args=[other_user_task.id]))
        # check it returns a 404 since the task isn't assigned to the current user
        self.assertEqual(response.status_code, 404)

    def test_delete_task_invalid_method(self):
        response = self.client.get(reverse('delete_task', args=[self.user_task.id]))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, 'utf8'), {'status': 'error'})

    ## As a user, I can complete tasks and earn points
    def test_complete_task_success(self):
        initial_points = self.user1.points
        task_id = self.user_task.task.task_id
        complete_task_url = reverse('complete_task', kwargs={'task_id': task_id})
        response = self.client.post(complete_task_url)
        expected_points = initial_points + self.task.points_given
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, 'utf8'),
                             {"status": "success", "points": expected_points})
        self.user_task.refresh_from_db()
        self.assertTrue(self.user_task.completed)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.points, expected_points)
        self.pet.refresh_from_db()
        # Assuming pet's XP increases by task.xp_given
        self.assertEqual(self.pet.pet_exp, 40 + self.task.xp_given)
        self.assertEqual(self.pet.pet_level, 1)

    ## As a user, completing a task that is already marked as completed does not change anything
    def test_complete_task_already_completed(self):
        self.user_task.completed = True
        self.user_task.save()
        initial_points = self.user1.points
        initial_xp = self.pet.pet_exp
        initial_level = self.pet.pet_level
        self.client.post(reverse('complete_task', args=[self.user_task.id]))
        self.user_task.refresh_from_db()
        self.assertTrue(self.user_task.completed)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.points, initial_points)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.pet_exp, initial_xp)
        self.assertEqual(self.pet.pet_level, initial_level)

    ## As a user, I cannot complete a task that hasn't been assigned to them
    def test_complete_task_not_assigned_to_user(self):
        response = self.client.post(reverse('complete_task', args=[self.other_user_task.id]))
        self.assertEqual(response.status_code, 404)

    def test_complete_task_invalid_method(self):
        response = self.client.get(reverse('complete_task', args=[self.other_user_task.id]))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, 'utf8'), {"status": "error"})

    def test_pet_level_up_on_task_completion(self):
        # Create a task that gives enough XP to level up the pet
        task2 = Task.objects.create(task_name="Complete Task for XP", description="Complete the task", points_given=10,
                                    xp_given=120, creator=self.user1)
        user_task1 = UserTask.objects.create(user=self.user1, task=task2)
        initial_points = self.user1.points
        complete_url = reverse('complete_task', args=[user_task1.id])
        response = self.client.post(complete_url)
        expected_points = initial_points + task2.points_given
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, 'utf8'),
                             {"status": "success", "points": expected_points})
        # refresh pet to check updated XP and level
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.pet_level, 2)
        # pet_exp should be (initial xp from pet + task xp) - 100, i.e., (40 + 120) - 100 = 60
        self.assertEqual(self.pet.pet_exp, 60)
        user_task1.refresh_from_db()
        self.assertTrue(user_task1.completed)

    ## As a user, I can view predefined and custom tasks
    def test_view_predefined_and_custom_tasks(self):
        self.client.login(username='testuser', password='password')
        predefined_task = Task.objects.create(task_name="Predefined Task", description="Admin task", predefined=True,
                                              creator=self.other_user)
        custom_task = Task.objects.create(task_name="Custom Task", description="User task", predefined=False,
                                          creator=self.user1)
        UserTask.objects.create(user=self.user1, task=predefined_task)
        UserTask.objects.create(user=self.user1, task=custom_task)
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Predefined Task")
        self.assertContains(response, "Custom Task")
        self.assertNotContains(response, "Task 1")  # Task created by another user

    ## As a user, I can view task points on the tasks page
    def test_view_task_points(self):
        task_with_points = Task.objects.create(
            task_name="Task with points",
            description="Test task",
            points_given=50,
            creator=self.user1
        )
        UserTask.objects.create(user=self.user1, task=task_with_points)
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)
        # Adjust assertion to check for "Points: 50" as rendered by your template
        self.assertContains(response, 'Points: 50')

    # As a user, I can complete tasks and earn points
    def test_user_completes_task_and_earns_points(self):
        user_points_before = self.user1.points
        task_id = self.task.task_id
        complete_task_url = reverse('complete_task', kwargs={'task_id': task_id})
        response = self.client.post(complete_task_url)
        self.assertEqual(response.status_code, 200)
        updated_user = CustomUser.objects.get(pk=self.user1.pk)
        self.assertEqual(updated_user.points, user_points_before + self.task.points_given)
        updated_user_task = UserTask.objects.get(user=self.user1, task=self.task)
        self.assertTrue(updated_user_task.completed)

    # As a user, I can complete tasks and earn xp
    def test_user_completes_task_and_pet_earns_xp(self):
        pet_xp_before = self.pet.pet_exp
        task_id = self.task.task_id
        complete_task_url = reverse('complete_task', kwargs={'task_id': task_id})
        response = self.client.post(complete_task_url)
        self.assertEqual(response.status_code, 200)
        updated_pet = Pet.objects.get(pk=self.pet.pk)
        self.assertEqual(updated_pet.pet_exp, pet_xp_before + self.task.xp_given)
        updated_user_task = UserTask.objects.get(user=self.user1, task=self.task)
        self.assertTrue(updated_user_task.completed)