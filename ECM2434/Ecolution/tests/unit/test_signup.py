from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from Ecolution.models import Pet, CustomUser


class SignupUnitTests(TestCase):
    def setUp(self):
        # valid user data for form entry
        self.valid_user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "Test@12345",
            "password2": "Test@12345",
            "pet_name": "Buddy",
            "pet_type": "Dog",
        }

        # urls
        self.url_signup = reverse("signup")
        self.url_login = reverse("login")

    # As a user, I can sign up for an account with valid details <-- integration test?
    def test_signup_successful(self):
        # user signs up for an account
        response = self.client.post(self.url_signup, self.valid_user_data, follow = True)

        # check user is successfully redirected to login page
        self.assertRedirects(response, self.url_login)

        # check that user has been created
        self.assertTrue(CustomUser.objects.filter(username = "testuser").exists())
        user = CustomUser.objects.get(username = "testuser")

        # check that user pet has been assigned
        self.assertTrue(Pet.objects.filter(user=user).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Account created! You can now log in.", [msg.message for msg in messages])

    # As a user, I cannot sign up for an account with an invalid email
    def test_signup_invalid_email(self):
        # replace email from setUp() with invalid email
        data = self.valid_user_data.copy()
        data["email"] = "invalid-email"

        response = self.client.post(self.url_signup, data, follow = True)

        # check user is not created
        self.assertFalse(CustomUser.objects.filter(username="testuser").exists())

        # check user receives message regarding invalid email
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Please enter a valid email address.", [msg.message for msg in messages])

    # As a user, I cannot signup for an account with a username that already exists
    def test_signup_username_already_taken(self):
        CustomUser.objects.create_user(username="testuser", email="testuser@example.com", password="password123")

        response = self.client.post(self.url_signup, self.valid_user_data, follow=True)

        # check that duplicate user wasn't created
        self.assertEqual(CustomUser.objects.filter(username="testuser").count(), 1)

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Username already taken.", [msg.message for msg in messages])

    ## As a user, I cannot signup for an account with two different passwords
    def test_signup_password_mismatch(self):
        # replace second password from setUp() with a non-matching password
        data = self.valid_user_data.copy()
        data["password2"] = "DifferentPassword"

        response = self.client.post(self.url_signup, data, follow=True)
        self.assertFalse(CustomUser.objects.filter(username="testuser").exists())  # check user isn't created

    ## As a user, I am assigned the pet I chose during sign-up
    def test_pet_association_on_signup(self):
        # signup user for an account
        self.client.post(self.url_signup, self.valid_user_data, follow=True)
        user = CustomUser.objects.get(username="testuser")

        # check that pet name and type matches form details
        pet = Pet.objects.filter(user=user).first()
        self.assertIsNotNone(pet)  # pet should be created
        self.assertEqual(pet.pet_name, "Buddy")
        self.assertEqual(pet.pet_type, "Dog")

