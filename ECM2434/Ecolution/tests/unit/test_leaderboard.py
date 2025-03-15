from django.test import TestCase
from django.urls import reverse
from django.db import connection
from Ecolution.models import CustomUser, Event, Pet

class TestLeaderboard(TestCase):
    def setUp(self):
        # create users and login new user
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.user2 = CustomUser.objects.create_user(username='user2', password='password')
        self.user3 = CustomUser.objects.create_user(username='user3', password='password')
        self.client.login(username='testuser', password='password')

        # create pets for users
        self.pet1 = Pet.objects.create(user=self.user1, pet_name='Test Pet', pet_exp = 11)
        self.pet2 = Pet.objects.create(user=self.user1, pet_name='Test Pet', pet_exp=17)
        self.pet3 = Pet.objects.create(user=self.user1, pet_name='Test Pet', pet_exp=13)

    # As a user, I can access the Leaderboard page
    def test_view_leaderboard(self):
        response = self.client.get(reverse('leaderboard'))
        self.assertEqual(response.status_code, 200)

    # As a user, I can see myself (via username) on the Leaderboard
    def test_leaderboard_view_self(self):
        # user navigates to leaderboard
        response = self.client.get(reverse('leaderboard'))

        # check user's name appears on leaderboard
        self.assertContains(response, 'testuser')

    # As a user, I can see the level of my pet on the card
    def test_leaderboard_view_pet_level(self):
        response = self.client.get(reverse('leaderboard')

        # check pet level appears
        self.assertContains(response, self.pet1.pet_exp)

    # As a user, I can see the name of my pet on the card
    def test_leaderboard_view_pet_name(self):
        response = self.client.get(reverse('leaderboard'))

        # check pet name appears
        self.assertContains(response, self.pet1.pet_name)

    # As a user, I can see other users cards
    def test_leaderboard_view_other_users(self):
        response = self.client.get(reverse('leaderboard'))

        # check other users and their pets appear
        self.assertContains(response, self.user2.username)
        self.assertContains(response, self.user3.username)
        self.assertContains(response, self.pet2.pet_name)
        self.assertContains(response, self.pet3.pet_name)
        self.assertContains(response, self.pet2.pet_exp)
        self.assertContains(response, self.pet3.pet_exp)
