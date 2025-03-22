from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Pet


class TestLeaderboard(TestCase):
    def setUp(self):
        # Create users and login
        self.user1 = CustomUser.objects.create_user(username='user1', password='password')
        self.user2 = CustomUser.objects.create_user(username='user2', password='password')
        self.user3 = CustomUser.objects.create_user(username='user3', password='password')
        self.user4 = CustomUser.objects.create_user(username='user4', password='password')
        self.user5 = CustomUser.objects.create_user(username='user5', password='password')
        self.client.login(username='user1', password='password')

        # Create pets for users
        self.pet1 = Pet.objects.create(user=self.user1, pet_name='Test Pet', pet_level=11)
        self.pet2 = Pet.objects.create(user=self.user2, pet_name='Test Pet 2', pet_level=17)
        self.pet3 = Pet.objects.create(user=self.user3, pet_name='Test Pet 3', pet_level=13)
        self.pet4 = Pet.objects.create(user=self.user4, pet_name='Test Pet 4', pet_level=20)
        self.pet5 = Pet.objects.create(user=self.user5, pet_name='Test Pet 5', pet_level=25)

    def test_view_leaderboard(self):
        response = self.client.get(reverse('leaderboard'))
        self.assertEqual(response.status_code, 200)

    def test_leaderboard_display_top_three(self):
        response = self.client.get(reverse('leaderboard'))

        # Ensure the top three users' names and levels are displayed
        self.assertContains(response, '1 👑 - Level 25')  # Top user
        self.assertContains(response, 'user5')  # Top user name
        self.assertContains(response, '2 - Level 20')  # 2nd place
        self.assertContains(response, 'user4')  # 2nd place name
        self.assertContains(response, '3 - Level 17')  # 3rd place
        self.assertContains(response, 'user2')  # 3rd place name

    def test_leaderboard_display_remaining_entries(self):
        response = self.client.get(reverse('leaderboard'))

        # Ensure 4th and 5th place users' names and levels are displayed
        self.assertContains(response, 'Level 13')  # 4th place pet level
        self.assertContains(response, 'user3')  # 4th place user
        self.assertContains(response, 'Level 11')  # 5th place pet level
        self.assertContains(response, 'user1')  # 5th place user

    def test_leaderboard_order(self):
        response = self.client.get(reverse('leaderboard'))

        # Ensure that the leaderboard entries are ordered by pet level
        self.assertContains(response, 'Level 25')  # Highest pet level
        self.assertContains(response, 'Level 20')
        self.assertContains(response, 'Level 17')
        self.assertContains(response, 'Level 13')
        self.assertContains(response, 'Level 11')  # Lowest pet level

    def test_leaderboard_image_display(self):
        response = self.client.get(reverse('leaderboard'))

        # Check if images for the pets are being displayed (based on computed image URL)
        self.assertContains(response, f"src=\"{self.pet5.computed_image_url}\"")
        self.assertContains(response, f"src=\"{self.pet4.computed_image_url}\"")
        self.assertContains(response, f"src=\"{self.pet2.computed_image_url}\"")
        self.assertContains(response, f"src=\"{self.pet3.computed_image_url}\"")
        self.assertContains(response, f"src=\"{self.pet1.computed_image_url}\"")

