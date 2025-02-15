from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser
from Ecolution.models import UserTask
from Ecolution.models import Task

class SignupIntegrationTests(TestCase):
    def setUp(self):
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')  # ensure you have the correct URL name for login
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
        }

    ## As a user, I can sign up for an account with a valid user and password
    def test_signup_valid_creds(self):
        # TODO: test with valid data
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'password1': 'validpassword123',
            'password2': 'validpassword123',
        })

        # check if the user is redirected after successful signup
        self.assertRedirects(response, '/login/')  # TODO: adjust the redirect URL (e.g., home page or login page)

        # TODO: ensure the user is created
        user = CustomUser.objects.get(username='newuser')
        self.assertIsNotNone(user)  # TODO:(?) check that the user exists in the database

    ## As a user, I cannot sign up for an account with an invalid email and valid password
    def test_signup_invalid_email(self):
        # TODO: test with invalid email/user data
        response = self.client.post(self.signup_url, {
            'username': 'invalid_user',
            'email': 'invalidemailexample.com',
            'password1': 'validpassword123',
            'password2': 'validpassword123',
        })

        # check if the user is redirected after successful signup
        self.assertNotEqual(response, '/')  # TODO: adjust the redirect URL (e.g., home page or login page)

        # TODO: ensure the user is NOT created
        user = CustomUser.objects.get(username='newuser')
        self.assertIsNone(user)  # TODO:(?) check that the user does not exist in the database

    ## As a user, I cannot sign up for an account with a valid email but invalid password
    def test_signup_invalid_pwd(self):
        # TODO: test with valid, but different, passwords data
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'email': 'user@example.com',
            'password1': 'validpassword123',
            'password2': 'invalidpwd',
        })

        # check if the user is redirected after successful signup
        self.assertNotEqual(response, '/')  # TODO: adjust the redirect URL (e.g., home page or login page)

        # TODO: ensure the user is NOT created
        user = CustomUser.objects.get(username = 'newuser')
        self.assertIsNone(user)  # TODO:(?) check that the user does not exist in the database

        ## As a user, I cannot sign-up for an account with password fields not matching
        # TODO: test with invalid email/user data
        response = self.client.post(self.signup_url, {
            'username': 'invalid_user_or_email',
            'password1': 'validpassword123',  # password1 (it should match password2)
            'password2': 'validpassword123',  # password2
        })

        # check if the user is redirected after successful signup
        self.assertNotEqual(response, '/')  # TODO: adjust the redirect URL (e.g., home page or login page)

        # TODO: ensure the user is NOT created
        user = CustomUser.objects.get(username='newuser')
        self.assertIsNone(user)  # TODO:(?) check that the user does not exist in the database

    ## As a user, I can sign up for an account and then login to that account
    def test_signup_redirect(self):
        # user is successfully signed up
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, 302)  # expect redirect after sign-up
        self.assertTrue(CustomUser.objects.filter(username = 'testuser').exists())

        # user is successfully logged in
        login_data = {
            'username': 'testuser',
            'password': 'validpassword123',
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 200)  # expect redirect after login

        # check that user has been authenticated
        response = self.client.get(reverse('home'))  # TODO: replace 'home' with a logged-in page URL name
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'testuser')  # TODO: if applicable, verify username is shown on the page

    ## As a user, I cannot signup for an account with the password fields not matching
    def test_signup_different_passwords(self):
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'email': 'user@example.com',
            'password1': 'differentpassword123',
            'password2': 'validpassword123',
        })

        self.assertNotEqual(response, '/ecolution/')  # check that user is not logged in, stays on signup
        # or check if the user is logged in using session or user info
        self.assertNotIn('_auth_user_id', self.client.session)
