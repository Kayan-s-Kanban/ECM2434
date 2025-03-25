from django.urls import reverse
from Ecolution.models import CustomUser
from Ecolution.tests.base_test import BaseTestCase

class LoginIntegrationTests(BaseTestCase):
    def setUp(self):
        # create a test user
        self.user = CustomUser.objects.create_user(
            username = "Tester",
            password = "123456"
        )

        # urls
        self.url_home = reverse('home')
        self.url_login = reverse('login')
        self.url_signup = reverse('signup')

    ## As a user, I can log in with correct user and password
    def test_login_valid_creds(self):

        # attempt to log in with correct credentials
        response = self.client.post(self.url_login, {
            'username': 'Tester',
            'password': '123456',
        })

        # check that the user is logged in and redirected to the intended page
        self.assertRedirects(response, self.url_home)

    ## As a user, I cannot log in with correct user but incorrect password
    def test_login_invalid_pwd(self):
        response = self.client.post(self.url_login, {
            'username': 'Tester',
            'password': '987654',
        })

        # check that the user is not logged in and redirected to the intended page
        self.assertNotEqual(response, self.url_home)

    ## As a user, I cannot log in with incorrect user and correct password
    def test_login_invalid_user(self):
        response = self.client.post(self.url_login, {
            'username': 'NotTester',
            'password': '123456',
        })

        # check that the user is not logged in and redirected to the intended page
        self.assertNotEqual(response, self.url_home)