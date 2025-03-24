from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Pet


class LeaderboardUnitTests(TestCase):
    def setUp(self):
        # create users and login first user
        self.user1 = CustomUser.objects.create_user(username='user1', password='password')
        self.user2 = CustomUser.objects.create_user(username='user2', password='password')
        self.user3 = CustomUser.objects.create_user(username='user3', password='password')
        self.user4 = CustomUser.objects.create_user(username='user4', password='password')
        self.user5 = CustomUser.objects.create_user(username='user5', password='password')
        self.client.login(username='user1', password='password')

        # create pets for users
        self.pet1 = Pet.objects.create(user=self.user1, pet_name='Test Pet', pet_level=11)
        self.pet2 = Pet.objects.create(user=self.user2, pet_name='Test Pet 2', pet_level=17)
        self.pet3 = Pet.objects.create(user=self.user3, pet_name='Test Pet 3', pet_level=13)
        self.pet4 = Pet.objects.create(user=self.user4, pet_name='Test Pet 4', pet_level=20)
        self.pet5 = Pet.objects.create(user=self.user5, pet_name='Test Pet 5', pet_level=25)

        # urls
        self.url_leaderboard = reverse('leaderboard')

    # As a user, I can view the leaderboard
    def test_view_leaderboard(self):
        response = self.client.get(self.url_leaderboard)
        self.assertEqual(response.status_code, 200)

    # As a user, I can view the top 3 users, and their respective ranks and pet levels
    def test_leaderboard_display_top_three(self):
        response = self.client.get(self.url_leaderboard)

        # make sure top three users' names and levels are displayed
        self.assertContains(response, '1 👑 - Level 25')  # Top user
        self.assertContains(response, 'user5')  # Top user name
        self.assertContains(response, '2 - Level 20')  # 2nd place
        self.assertContains(response, 'user4')  # 2nd place name
        self.assertContains(response, '3 - Level 17')  # 3rd place
        self.assertContains(response, 'user2')  # 3rd place name

    # As a user, I can view other top users in order, alongside their usernames, and level
    def test_leaderboard_display_remaining_users(self):
        response = self.client.get(self.url_leaderboard)

        # make sure 4th and 5th place users' names and levels are displayed
        self.assertContains(response, 'Level 13')  # 4th place pet level
        self.assertContains(response, 'user3')  # 4th place user
        self.assertContains(response, 'Level 11')  # 5th place pet level
        self.assertContains(response, 'user1')  # 5th place user

    # As a user, I can view the users on the leaderboard in order from highest to lowest level
    def test_leaderboard_order(self):
        response = self.client.get(self.url_leaderboard)

        # check leaderboard users are ordered by pet level
        self.assertContains(response, 'Level 25')  # highest pet level
        self.assertContains(response, 'Level 20')
        self.assertContains(response, 'Level 17')
        self.assertContains(response, 'Level 13')
        self.assertContains(response, 'Level 11')  # lowest pet level

    # As a user, I can view other users' pets on the leaderboard
    def test_leaderboard_pet_display(self):
        response = self.client.get(self.url_leaderboard)

        # check if images for user pets are displayed
        self.assertContains(response, f"src=\"{self.pet5.computed_image_url}\"")
        self.assertContains(response, f"src=\"{self.pet4.computed_image_url}\"")
        self.assertContains(response, f"src=\"{self.pet2.computed_image_url}\"")
        self.assertContains(response, f"src=\"{self.pet3.computed_image_url}\"")
        self.assertContains(response, f"src=\"{self.pet1.computed_image_url}\"")

