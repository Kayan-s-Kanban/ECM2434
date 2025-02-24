from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser
from Ecolution.models import UserTask
from Ecolution.models import Task

class SettingsTestCase(TestCase):
    def setUp(self):
        # create user
        self.user = CustomUser.objects.create_user(username = 'testuser', password = 'password')

        # login user
        self.client.login(username = 'testuser', password = 'password')

        # user navigates to settings page
        response = self.client.get(reverse('settings'))

