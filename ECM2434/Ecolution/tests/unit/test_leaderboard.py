from django.test import TestCase
from django.urls import reverse
from django.db import connection
from Ecolution.models import CustomUser, Event, Pet

class TestLeaderboard(TestCase):
    def setUp(self):

    # As a user, I can access the Leaderboard page

    # As a user, I can see myself on the Leaderboard

    # As a user, I can see my username on the card

    # As a user, I can see the level of my pet on the card

    # As a user, I can see the name of my pet on the card

    # As a user, I can see other users cards