from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, UserItem
from Ecolution.views import User


class SignupIntegrationTests(TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.shop_item = None

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
        response = self.client.post(self.signup_url, self.user_data)

        # check if the user is redirected after successful signup
        self.assertRedirects(response, '/ecolution/login/')

        # checks that the user is created
        user = CustomUser.objects.get(username = 'testuser')
        self.assertIsNotNone(user)  # checks that the user exists in the database

    ## As a user, I cannot sign up for an account with an invalid email and valid password
    def test_signup_invalid_email(self):
        response = self.client.post(self.signup_url, {
            'username': self.user_data['username'],
            'email': '',
            'password1': self.user_data['password1'],
            'password2': self.user_data['password2'],
        })

        # check if the user is redirected after successful signup
        self.assertNotEqual(response, '/login/')  # TODO: adjust the redirect URL (e.g., home page or login page)

        # check that the user is not created
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(username='newuser')

    ## As a user, I cannot sign up for an account with a valid email but invalid password
    def test_signup_invalid_pwd(self):
        # TODO: after validation implemented, update passwords to be invalid
        response = self.client.post(self.signup_url, {
            'username': self.user_data['username'],
            'email': self.user_data['email'],
            'password1': self.user_data['password1'],
            'password2': '',
        })

        # check if the user is redirected after successful signup
        self.assertNotEqual(response, '/')  # TODO: adjust the redirect URL (e.g., home page or login page)

        # check that the user is not created
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(username='newuser')

    ## As a user, I can sign up for an account and then login to that account
    def test_signup_redirect(self):
        # user is successfully signed up
        response = self.client.post(self.signup_url, self.user_data)
        # check if the user is redirected after successful signup
        self.assertRedirects(response, '/ecolution/login/')
        self.assertTrue(CustomUser.objects.filter(username = 'testuser').exists())

        # user is successfully logged in
        login_data = {
            'username': 'testuser',
            'password': 'password123',
        }

        response = self.client.post(self.login_url, login_data)

        # user should be redirected to homepage after login
        self.assertRedirects(response, '/ecolution/home/')

    ## As a user, I cannot sign up for an account with the password fields not matching
    def test_signup_different_passwords(self):
        response = self.client.post(self.signup_url, {
            'email': self.user_data['email'],
            'username': self.user_data['username'],
            'password1': '',  # password1 (it should match password2)
            'password2': self.user_data['password2'],  # password2
        })

        # check if the user is redirected after successful signup
        self.assertNotEqual(response, 'home')  # TODO: adjust the redirect URL (e.g., home page or login page)

        # check that the user is not created
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(username = 'newuser')

    ## As a user, I cannot sign up for an account with a username that already exists
    def test_signup_existing_username(self):
        response = self.client.post(reverse("signup_view"), {
            "email": "newemail@example.com",
            "username": "testuser",
            "password1": "newpassword123",
            "password2": "newpassword123",
            "pet_type": "dog",
            "pet_name": "Buddy"
        })

        # check the response renders the signup page again
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")

        # check the error message is in the response
        self.assertContains(response, "Username already taken!")

    def test_user_item_created_on_signup(self):
        response = self.client.post(reverse("signup_view"), {
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
        user_item_exists = UserItem.objects.filter(user=user, shopitem=self.shop_item).exists()
        self.assertTrue(user_item_exists, "UserItem should be created when a matching ShopItem exists.")

        # check signup was successful
        self.assertRedirects(response, reverse("login"))
