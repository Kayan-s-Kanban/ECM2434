from django.test import TestCase
from django.urls import reverse
from Ecolution.models import Task, CustomUser, UserTask, Pet

class HomepageIntegrationTests(TestCase):
    def setUp(self):
        # create a user
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.user1.points = 10
        self.pet1 = Pet.objects.create(
            user=self.user1,
            pet_name='Gertrude',
            pet_level=1,
            pet_exp=0,
            pet_type='mushroom'
        )

        # create a second pet
        self.pet2 = Pet.objects.create(
            user=self.user1,
            pet_name='Ginny',
            pet_level=5,
            pet_exp=15,
            pet_type='acorn'
        )

        # create a third pet
        self.pet3 = Pet.objects.create(
            user=self.user1,
            pet_name='George',
            pet_level=10,
            pet_exp=25,
            pet_type='pot'
        )

        # Assign the pet to the user as their displayed pet
        self.user1.displayed_pet = self.pet1
        self.user1.save()

        self.client.login(username='testuser', password='password')

        # Create new task
        self.task1 = Task.objects.create(task_name="Buy groceries", description="Go to the store and buy food")
        self.task1.points = 50

    def test_homepage_view_pet_name(self):
        response = self.client.get(reverse('home'))
        # Assert that the pet name is displayed
        self.assertContains(response, 'Pet Name:')
        self.assertContains(response, self.pet1.pet_name)

    # As a user, I can view my current tasks
    def test_homepage_current_tasks(self):
        # user is on homepage
        response = self.client.get(reverse('home'))

        # check tasks appear on homepage
        self.assertContains(response, "Buy groceries")
        self.assertContains(response, "Go to the store and buy food")

    ## As a user, I can change my pet on the homepage without any unexpected redirects
    def test_cycle_pet_redirects_to_home(self):
        response = self.client.get(reverse("cycle_pet"))
        self.assertEqual(response.status_code, 302)  # Redirect expected
        self.assertEqual(response.url, reverse("home"))

    ## As a user, I can switch pets to update the displayed pet
    def test_cycle_pets_updates_displayed_pet(self):
        self.client.get(reverse("cycle_pet"))  # Cycle once
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.displayed_pet, self.pet2)

        self.client.get(reverse("cycle_pet"))  # Cycle again
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.displayed_pet, self.pet3)

        self.client.get(reverse("cycle_pet"))  # Cycle back to first pet
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.displayed_pet, self.pet1)

    ## As a user, I cannot switch pets if I only have one pet
    def test_cycle_pet_with_one_pet(self):
        Pet.objects.exclude(id=self.pet1.id).delete()  # Ensure only one pet remains

        initial_displayed_pet = self.user1.displayed_pet  # Save current displayed pet
        self.client.get(reverse("cycle_pet"))  # Try cycling

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.displayed_pet, initial_displayed_pet)  # Should remain unchanged
