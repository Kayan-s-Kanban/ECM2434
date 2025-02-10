from django.test import TestCase
from django.urls import reverse
from .models import CustomUser

class LoginTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username = "Tester",
            password = "123456"
        )
        self.login_url = reverse('login')  # Ensure you have the correct URL name for login

    ## As a user, I can log in with correct user and password
    def test_login_valid_creds(self):
        # attempt to log in with correct credentials
        response = self.client.post(self.login_url, {
            'username': 'Tester',
            'password': '123456',
        })

        # check that the user is logged in and redirected to the intended page
        self.assertRedirects(response, '/ecolution/')
        # or check if the user is logged in using session or user info
        self.assertTrue('_auth_user_id' in self.client.session)

    ## As a user, I cannot log in with correct user but incorrect password
    def test_login_invalid_pwd(self):
        response = self.client.post(self.login_url, {
            'username': 'Tester',
            'password': '987654',
        })

        # check that the user is logged in and redirected to the intended page
        self.assertNotEqual(response, '/ecolution/')
        # or check if the user is logged in using session or user info
        self.assertNotIn('_auth_user_id' in self.client.session)

    ## As a user, I cannot log in with incorrect email and correct password
    def test_login_invalid_email(self):
        response = self.client.post(self.login_url, {
            'username': 'NotTester',
            'password': '123456',
        })

        # check that the user is NOT logged in and redirected to the intended page
        self.assertNotEqual(response, '/ecolution/')

        # or check if the user is logged in using session or user info
        self.assertNotIn('_auth_user_id' in self.client.session) 

class SignupTestCase(TestCase):
    def setUp(self):
        self.signup_url = reverse('signup') # TODO: ensure have correct signup URL
        self.login_url = reverse('login') # TODO: ensure have correct login URL

    ## As a user, I can sign up for an account with a valid email and password
    def test_signup_valid_creds(self):
        # TODO: test with valid data
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'password1': 'validpassword123',  # password1 (it should match password2)
            'password2': 'validpassword123',  # password2
        })

        # check if the user is redirected after successful signup
        self.assertRedirects(response, '/')  # TODO: adjust the redirect URL (e.g., home page or login page)

        # TODO: ensure the user is created
        user = CustomUser.objects.get(username='newuser')
        self.assertIsNotNone(user)  # TODO:(?) check that the user exists in the database

    ## As a user, I cannot sign up for an account with an invalid email and valid password
    def test_signup_invalid_email(self):
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

    ## As a user, I cannot sign-up for an account with a valid email but invalid password
    def test_signup_invalid_pwd(self):
        # TODO: test with valid, but different, passwords data
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'password1': 'validpassword123',  # password1 (it should match password2)
            'password2': 'validpassword456',  # password2
        })

        # check if the user is redirected after successful signup
        self.assertNotEqual(response, '/')  # TODO: adjust the redirect URL (e.g., home page or login page)

        # TODO: ensure the user is NOT created
        user = CustomUser.objects.get(username='newuser')
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
        self.assertTrue(CustomUser.objects.filter(username='testuser').exists())

        # user is successfully logged in
        login_data = {
            'username': 'testuser',
            'password': 'validpassword123',
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 302)  # expect redirect after login

        # check that user has been authenticated
        response = self.client.get(reverse('home'))  # TODO: replace 'home' with a logged-in page URL name
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')  # TODO: if applicable, verify username is shown on the page

class LogoutTestCase(TestCase):
    def setUp(self):
        # create test user
        self.user = CustomUser.objects.create_user(
            username = 'testuser',
            password = 'ComplexPass123!'
        )
        self.login_url = reverse('login')  # TODO: replace with your login view name
        self.logout_url = reverse('logout')  # TODO: replace with your logout view name

        # log in the test user
        self.client.login(username='testuser', password='validpassword123')

    ## As a user, I can log out of my account
    def test_logout(self):
        # check user is logged in before logging out
        response = self.client.get(reverse('home'))  # Replace 'home' with a protected page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')  # Optional: Check username on the page
        
        # check logout
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Expect redirect after logout
        
        # check user is logged out by attempting to access a protected page
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'testuser')  # username should no longer appear
        self.assertNotIn('_auth_user_id', self.client.session)  # Django's session key for logged-in users
    
