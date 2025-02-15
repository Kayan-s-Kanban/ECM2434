from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser

class SettingsTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username = 'testuser', password = 'password')  # create user
        self.client.login(username = 'testuser', password = 'password')  # login user

    ## As a user, I can change my password
    ## TODO: see todo's for test case
    def test_settings_change(self):
        # user navigates to settings successfully
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)

        # TODO: user can selecting reset pwd button (if exists)

        # TODO: user can enter new password into both fields

        # TODO: new password is saved

        # TODO: user can login to site with new pwd

    ## As a user, I can delete my account