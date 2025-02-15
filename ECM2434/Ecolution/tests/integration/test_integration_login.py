from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser

class LoginIntegrationTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username = "Tester",
            password = "123456"
        )
        self.login_url = reverse('login')  # ensure you have the correct URL name for login
        self.signup_url = reverse('signup')  # ensure have correct URL name for signup

    ## As a user, I can log in with correct user and password
    def test_login_valid_creds(self):
        # attempt to log in with correct credentials
        response = self.client.post(self.login_url, {
            'username': 'Tester',
            'password': '123456',
        })

        # check that the user is logged in and redirected to the intended page
        self.assertRedirects(response, '/ecolution/home/')
        # or check if the user is logged in using session or user info
        self.assertTrue('_auth_user_id', self.client.session)

    ## As a user, I cannot log in with correct user but incorrect password
    def test_login_invalid_pwd(self):
        response = self.client.post(self.login_url, {
            'username': 'Tester',
            'password': '987654',
        })

        # check that the user is not logged in and redirected to the intended page
        self.assertNotEqual(response, '/ecolution/home/')
        # or check if the user is logged in using session or user info
        self.assertNotIn('_auth_user_id', self.client.session)

    ## As a user, I cannot log in with incorrect user and correct password
    def test_login_invalid_user(self):
        response = self.client.post(self.login_url, {
            'username': 'NotTester',
            'password': '123456',
        })

        # check that the user is not logged in and redirected to the intended page
        self.assertNotEqual(response, '/ecolution/home/')
        # or check if the user is logged in using session or user info
        self.assertNotIn('_auth_user_id', self.client.session)

    ## As a user, I can reset my password
    # TODO: see todo's for test case
    # def test_login_reset_password(self):
    # TODO: user selects reset password link and redirected to reset pwd page

    # TODO: user enters new password

    # TODO: user's password is reset and can login with new password