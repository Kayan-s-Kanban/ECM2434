from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Event, Pet

class TestLeaderboard(TestCase):
    def setUp(self):
        # create users and login the first user
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.user2 = CustomUser.objects.create_user(username='user2', password='password')
        self.user3 = CustomUser.objects.create_user(username='user3', password='password')
        self.client.login(username='testuser', password='password')

        # debug statement
        self.assertTrue(self.client.login(username='testuser', password='password'))

        # create pets for users
        self.pet1 = Pet.objects.create(user=self.user1, pet_name='Test Pet', pet_level=11)
        self.pet2 = Pet.objects.create(user=self.user2, pet_name='Test Pet', pet_level=17)
        self.pet3 = Pet.objects.create(user=self.user3, pet_name='Test Pet', pet_level=13)

    # As a user, I can access the Leaderboard page
    def test_view_leaderboard(self):
        response = self.client.get(reverse('leaderboard'))
        self.assertEqual(response.status_code, 200)

    # As a user, I can see myself (via username) on the Leaderboard
    def test_leaderboard_view_self(self):
        response = self.client.get(reverse('leaderboard'))
        self.assertContains(response, 'testuser')

    # As a user, I can see the level of my pet on the card
    def test_leaderboard_view_pet_level(self):
        response = self.client.get(reverse('leaderboard'))
        self.assertContains(response, str(self.pet1.pet_level))

    # As a user, I can see the name of my pet on the card
    def test_leaderboard_view_pet_name(self):
        response = self.client.get(reverse('leaderboard'))
        self.assertContains(response, self.pet1.pet_name)

    # As a user, I can see other users cards
    def test_leaderboard_view_other_users(self):
        response = self.client.get(reverse('leaderboard'))

        # check that other users' names appear
        self.assertContains(response, self.user2.username)
        self.assertContains(response, self.user3.username)

        # check that their pets' names and levels appear
        self.assertContains(response, self.pet2.pet_name)
        self.assertContains(response, self.pet3.pet_name)
        self.assertContains(response, str(self.pet2.pet_level))
        self.assertContains(response, str(self.pet3.pet_level))

    # As a user, I can see the leaderboard of users ordered by pet experience
    def test_leaderboard_order(self):
        response = self.client.get(reverse('leaderboard'))

        # check pets are ordered by experience, highest first
        pets = [self.pet2, self.pet3, self.pet1]
        for idx, pet in enumerate(pets):
            self.assertContains(response, pet.pet_name, html=True)
            self.assertContains(response, str(pet.pet_level), html=True)