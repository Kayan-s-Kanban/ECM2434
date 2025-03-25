from django.urls import reverse
from Ecolution.models import CustomUser, UserItem, ShopItem
from Ecolution.views import User
from Ecolution.tests.base_test import BaseTestCase


class SignupIntegrationTests(BaseTestCase):
    def setUp(self):
        # set up user data
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Password123',
            'password2': 'Password123',
        }

        self.url_signup = reverse('signup')
        self.url_login = reverse('login')
        self.url_home = reverse('home')

    def test_signup_valid_creds(self):
        response = self.client.post(self.url_signup, self.user_data)

        # check for success code
        self.assertEqual(response.status_code, 200)

    ## As a user, I cannot sign up for an account with an invalid email and valid password
    def test_signup_invalid_email(self):
        response = self.client.post(self.url_signup, {
            'username': self.user_data['username'],
            'email': '',
            'password1': self.user_data['password1'],
            'password2': self.user_data['password2'],
        })

        # check if the user is redirected after successful signup
        self.assertNotEqual(response, '/login/')

        # check that the user is not created
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(username='newuser')

    ## As a user, I cannot sign up for an account with a valid email but invalid password
    def test_signup_invalid_pwd(self):
        response = self.client.post(self.url_signup, {
            'username': self.user_data['username'],
            'email': self.user_data['email'],
            'password1': self.user_data['password1'],
            'password2': '',
        })

        # check if the user is redirected after successful signup
        self.assertNotEqual(response, '/')

        # check that the user is not created
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(username='newuser')

    ## As a user, I can sign up for an account and then login to that account
    def test_signup_redirect(self):
        # user is successfully signed up
        self.client.post(self.url_signup, self.user_data)

        # user is successfully logged in
        login_data = {
            'username': 'testuser',
            'password': 'password123',
        }

        response = self.client.post(self.url_login, login_data)
        self.assertEqual(response.status_code, 200)

    ## As a user, I cannot sign up for an account with the password fields not matching
    def test_signup_different_passwords(self):
        response = self.client.post(self.url_signup, {
            'email': self.user_data['email'],
            'username': self.user_data['username'],
            'password1': '',  # password1 (it should match password2)
            'password2': self.user_data['password2'],  # password2
        })

        # check if the user is redirected after successful signup
        self.assertNotEqual(response, 'home')

        # check that the user is not created
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(username = 'newuser')

    ## As a user, I cannot sign up for an account with a username that already exists
    def test_signup_existing_username(self):
        # Ensure the client is logged out.
        self.client.logout()
        # Explicitly create a user with the username 'testuser'
        CustomUser.objects.create_user(username="testuser", email="testuser@example.com", password="Password123")
        response = self.client.post(self.url_signup, {
            "email": "newemail@example.com",
            "username": "testuser",
            "password1": "newpassword123",
            "password2": "newpassword123",
            "pet_type": "dog",
            "pet_name": "Buddy"
        }, follow=True)
        # Now the response should include the error message.
        self.assertContains(response, "Username already taken.")


    def test_user_item_created_on_signup(self):
        # Ensure a ShopItem with 'dog' exists
        shop_item = ShopItem.objects.create(name='dog')

        response = self.client.post(self.url_signup, {
            "email": "newuser@example.com",
            "username": "newuser",
            "password1": "securepassword",
            "password2": "securepassword",
            "pet_type": "dog",
            "pet_name": "Rex"
        })

        # check if user was created
        user = User.objects.get(username="newuser")

        # check if a UserItem was created
        user_item_exists = UserItem.objects.filter(user=user).exists()
        self.assertTrue(user_item_exists, "UserItem should be created when a matching ShopItem exists.")

        # Check if the response redirects to the login page
        self.assertRedirects(response, self.url_login)
