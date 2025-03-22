from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, UserTask, Task, Pet
from Ecolution.views import User

class TaskIntegrationTests(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password='password')

        # create a different user
        self.other_user = CustomUser.objects.create_user(username='otheruser', password='password')

        # create a test task
        self.task = Task.objects.create(
            task_name = "Buy groceries",
            description = "Go to the store and buy food",
            points_given = 100
        )

        self.task1 = Task.objects.create(
            task_name = "Task 1",
            description = "Task description here",
            points_given = 100
        )

        # create a UserTask assigned to the user
        self.user_task = UserTask.objects.create(user=self.user1, task=self.task)
        self.other_user_task = UserTask.objects.create(user=self.other_user, task=self.task1)

        # create a pet for the user
        self.pet = Pet.objects.create(user=self.user1, pet_name="TestPet", pet_level=1, pet_exp=95, pet_type="mushroom")
        self.user1.displayed_pet = self.pet
        self.user1.save()

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
        # user deletes task
        delete_url = 'tasks/delete/<int:user_task_id>/'
        response = self.client.post(delete_url)

        # task no longer appears in the user's list
        self.assertFalse(UserTask.objects.filter(user = self.user1, task = self.task).exists())

        # task no longer appears in the database
        self.assertIsNone(Task.objects.get(task_name = 'Go for a walk'))

        # check the response code for successful deletion
        self.assertEqual(response.status_code, 200)

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

    ## As a user, I can view my completed tasks -- UPDATE TEST
    def test_view_completed_tasks(self):
        self.client.login(username = 'testuser', password = 'password')
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

    def test_new_task_creation(self):
        response = self.client.post(reverse("add_task"), {
            "task_name": "New Task",
            "description": "Task description",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertTrue(Task.objects.filter(task_name="New Task", creator=self.user1).exists())

    def test_user_task_creation(self):
        """Test that a UserTask is created successfully (Lines 145, 147)."""
        task = Task.objects.create(task_name="User Task", description="Test Desc", creator=self.user1)

        response = self.client.post(reverse("add_task"), {
            "task_id": task.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserTask.objects.filter(user=self.user1, task=task).exists())

    def test_duplicate_user_task_error(self):
        """Test that adding the same task twice returns an error (Lines 149-150)."""
        task = Task.objects.create(task_name="Duplicate User Task", description="Test Desc", creator=self.user1)
        UserTask.objects.create(user=self.user1, task=task)

        response = self.client.post(reverse("add_task"), {
            "task_id": task.id,
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["message"], "This task already exists!")

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

    def test_invalid_request_method(self):
        """Test that a non-POST request returns an error (Line 161)."""
        response = self.client.get(reverse("add_task"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")

    # deleted tasks are successfully removed from database
    def test_delete_task_success(self):
        # make a POST request to delete the task
        response = self.client.post(reverse('delete_task', args=[self.user_task.id]))

        # check the task is deleted and response is successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, 'utf8'), {'status': 'success'})

        # check task is actually deleted from the database
        with self.assertRaises(UserTask.DoesNotExist):
            UserTask.objects.get(id=self.user_task.id)

    ## As a user, I cannot delete pre-defined tasks
    def test_delete_task_task_not_found(self):
        # Create a different user and assign a task to them
        other_user = User.objects.create_user(username='otheruser', password='password')
        other_user_task = UserTask.objects.create(user=other_user, task=self.task)

        # attempt to delete the task with the incorrect user
        response = self.client.post(reverse('delete_task', args=[other_user_task.id]))

        # check it returns an error status
        self.assertEqual(response.status_code, 404)

    def test_delete_task_invalid_method(self):
        # make a GET request (invalid method for this view)
        response = self.client.get(reverse('delete_task', args=[self.user_task.id]))

        # check it returns an error
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, 'utf8'), {'status': 'error'})

    ## As a user, I can complete tasks and earn points
    def test_complete_task_success(self):
        response = self.client.post(reverse('complete_task', args=[self.user_task.id]))

        # check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, 'utf8'),
                             {"status": "success", "points": self.user1.points + self.task.points_given})

        # check that the task is marked as completed
        self.user_task.refresh_from_db()
        self.assertTrue(self.user_task.completed)

        # check if the user's points have increased
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.points, self.task.points_given)

        # check if the pet's XP has increased
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.pet_exp, self.task.xp_given)

        # check if the pet's level has not changed since the XP is less than 100
        self.assertEqual(self.pet.pet_level, 1)

    ## As a user, completing a task that is already marked as completed does not change anything
    def test_complete_task_already_completed(self):
        self.user_task.completed = True
        self.user_task.save()

        # check user + pet initial points + xp
        initial_points = self.user1.points
        initial_xp = self.pet.pet_exp
        initial_level = self.pet.pet_level

        self.client.post(reverse('complete_task', args=[self.user_task.id]))

        # check the task is still marked as completed
        self.user_task.refresh_from_db()
        self.assertTrue(self.user_task.completed)

        # check the user's points remain the same
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.points, initial_points)

        # check the pet's XP and level remain the same
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.pet_exp, initial_xp)
        self.assertEqual(self.pet.pet_level, initial_level)

    ## As a user, I cannot complete a task that hasn't been assigned to me
    def test_complete_task_not_assigned_to_user(self):
        # attempt to complete the other user's task
        response = self.client.post(reverse('complete_task', args=[self.other_user_task.id]))

        # check the response is an error
        self.assertEqual(response.status_code, 404)

    def test_complete_task_invalid_method(self):
        response = self.client.get(reverse('complete_task', args=[self.other_user_task.id]))

        # check the response status code is 404 for invalid method
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, 'utf8'), {"status": "error"})

    def test_pet_level_up_on_task_completion(self):
        # Setup
        task2 = Task.objects.create(task_name="Complete Task for XP", description="Complete the task", points_given=10,
                                   xp_given=120)
        self.user_task1 = UserTask.objects.create(user=self.user1, task=task2)

        # complete task
        response = self.client.post(reverse('complete_task', args=[self.user_task1.id]))

        # check task was successfully completed
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, 'utf8'),
                             {"status": "success", "points": self.user1.points + self.task.points_given})

        self.pet.save()

        # reload the pet from the database to check updated experience and level
        self.pet.refresh_from_db()

        # check that pet's level has increased by 1
        self.assertEqual(self.pet.pet_level, 2)  # pet level should be 2 after gaining more than 100 XP

        # check pet's experience has been reset to a value less than 100
        self.assertEqual(self.pet.pet_exp, 15)  # Pet's experience should be 15 after the reset (120 XP - 100)

        # check the task is marked as completed
        self.user_task.refresh_from_db()
        self.assertTrue(self.user_task.completed)

    ## As a user, I can view predefined and custom tasks
    def test_view_predefined_and_custom_tasks(self):
        self.client.login(username='testuser', password='password')

        # create predefined and custom tasks
        predefined_task = Task.objects.create(task_name="Predefined Task", description="Admin task", predefined=True,
                                              creator=self.other_user)
        custom_task = Task.objects.create(task_name="Custom Task", description="User task", predefined=False,
                                          creator=self.user1)

        # Assign tasks to UserTask
        UserTask.objects.create(user=self.user1, task=predefined_task)
        UserTask.objects.create(user=self.user1, task=custom_task)

        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)

        # Ensure both tasks are visible to the user
        self.assertContains(response, "Predefined Task")
        self.assertContains(response, "Custom Task")

        # Ensure that predefined tasks are shown, but custom tasks created by others are not.
        self.assertNotContains(response, "Task 1")  # Task created by another user

    ##
    def test_view_task_points(self):
        # Create a Task instance with points
        task_with_points = Task.objects.create(
            task_name="Task with points",
            description="Test task",
            points_given=50,
            creator=self.user1
        )

        # Create a UserTask instance to associate the task with the user
        UserTask.objects.create(user=self.user1, task=task_with_points)

        # Log in the user (replace with the appropriate login mechanism)
        self.client.login(username='testuser', password='password')

        # Get the page where tasks are listed
        response = self.client.get(reverse('tasks'))

        # Assert that the response is successful (status code 200)
        self.assertEqual(response.status_code, 200)

        # Assert that the page contains the task points
        self.assertContains(response, '<span class="points">50 points</span>')

