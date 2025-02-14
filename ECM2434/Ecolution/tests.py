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
        self.login_url = reverse('login')  # ensure you have the correct URL name for login
        self.signup_url = reverse('signup') # ensure have correct URL name for signup

    ## As a user, I can log in with correct user and password
    def test_login_valid_creds(self):
        # attempt to log in with correct credentials
        response = self.client.post(self.login_url, {
            'username': 'Tester',
            'password': '123456',
        })

        # check that the user is logged in and redirected to the intended page
        self.assertRedirects(response, '/home/')
        # or check if the user is logged in using session or user info
        self.assertTrue('_auth_user_id', self.client.session)

    ## As a user, I cannot log in with correct user but incorrect password
    def test_login_invalid_pwd(self):
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'email': 'user@example.com',
            'password1': 'ivalidpassword',
            'password2': 'validpassword123',
        })

        # check that the user is not logged in and redirected to the intended page
        self.assertNotEqual(response, '/ecolution/')
        # or check if the user is logged in using session or user info
        self.assertNotIn('_auth_user_id', self.client.session)

    ## As a user, I cannot log in with incorrect email and correct password
    def test_login_invalid_email(self):
        response = self.client.post(self.signup_url, {
            'username': 'NotTester',
            'email': 'userexample.com',
            'password1': 'validpassword123',
            'password2': 'validpassword123',
        })

        # check that the user is NOT logged in and redirected to the intended page
        self.assertNotEqual(response, '/ecolution/')

        # or check if the user is logged in using session or user info
        self.assertNotIn('_auth_user_id', self.client.session)

class SignupTestCase(TestCase):
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
    ## inputs arent right
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
        user = CustomUser.objects.get(username = 'newuser')
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

        self.assertNotEqual(response, '/ecolution/') # check that user is not logged in, stays on signup
        # or check if the user is logged in using session or user info
        self.assertNotIn('_auth_user_id', self.client.session)

class LogoutTestCase(TestCase):
    def setUp(self):
        # create test user
        self.user = CustomUser.objects.create_user(
            username = 'testuser',
            password = 'ComplexPass123!'
        )
        self.login_url = reverse('login')  # TODO: replace with your login view name
        # self.logout_url = reverse('logout')  # TODO: replace with your logout view name

        # log in the test user
        self.client.login(username='testuser', password='validpassword123')

    ## As a user, I can log out of my account
    def test_logout(self):
        # check user is logged in before logging out
        response = self.client.get(reverse('home'))  # Replace 'home' with a protected page
        self.assertEqual(response.status_code, 200)
        
        # check logout
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)  # expect redirect after logout
        
        # check user is logged out by attempting to access a protected page
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'testuser')  # username should no longer appear
        self.assertNotIn('_auth_user_id', self.client.session)  # Django's session key for logged-in users

#class TasksTestCase(TestCase):
    # As a user, I can add tasks to my list
    # As a user, I can remove tasks from my list
    # As a user, I can complete tasks
    # As a user, I can edit tasks (?)
    # As a user, I can earn points from completing tasks
    # As a user, I can view task details
    # As a user, I can search for tasks

#class SettingsTestCase(TestCase):
    # As a user, I can reset my password
    # As a user, I can change my password
    # As a user, I can delete my account
    # As a user, I can change my name
    # As a user, I can change my pet's name

#class HomepageTestCase(TestCase):
    # As a user, I can view my pet
    # As a user, I can view my current tasks
    # As a user, I can open and close the menu
    # As a user, I can navigate to other pages
    # As a user, I can view my XP
    # As a user, I can remove a current task from my list
    # As a user, I can see my points increase after completing a task
    # As a user, I can see my points decrease after removing a completed task

#class AdminTestCase(TestCase):
    # As an admin, I can add content
    # As an admin, I can remove content
    # As an admin, I can edit content
    # As an admin, I can remove(?) users
    # As an admin, I can add(?) users
    
#class MapTestCase(TestCase):
    # As a user, I can view the map
    # As a user, I can interact with the map