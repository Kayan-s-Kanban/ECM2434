from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser
from Ecolution.models import UserTask
from Ecolution.models import Task

class SettingsTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username = 'testuser', password = 'password') # create user
        self.client.login(username = 'testuser', password = 'password') # login user

    ## As a user, I can change my username
    def test_settings_change_username(self):
        self.client.login(username = 'testuser', password = 'password')
        response = self.client.get(reverse('settings'))

        # user enters new username
        # TODO: enter correct username change url
        # self.client.post(reverse(/username_url/), 'notatestuser')

    ## As a user, I can change my pet's name
    def test_settings_change_petname(self):
        self.client.login(username = 'testuser', password = 'password')
        response = self.client.get(reverse('settings'))

        # TODO: user enters new petname


    ## As a user, I can reset my points (?)
    def test_settings_reset_points(self):
        self.client.login(username = 'testuser', password = 'password')
        response = self.client.get(reverse('settings'))

        # TODO: user selects "reset points" button (?)