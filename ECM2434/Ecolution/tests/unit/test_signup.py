from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from Ecolution.models import Pet, CustomUser


class SignupTestCase(TestCase):
    def setUp(self):
        """Set up the test client and user data before each test."""
        self.signup_url = reverse("signup")
        self.valid_user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "Test@12345",
            "password2": "Test@12345",
            "pet_name": "Buddy",
            "pet_type": "Dog",
        }

    def test_signup_successful(self):
        """Test if a user can sign up successfully with valid details."""
        response = self.client.post(self.signup_url, self.valid_user_data, follow=True)

        self.assertEqual(response.status_code, 200)  # Should redirect successfully
        self.assertTrue(CustomUser.objects.filter(username="testuser").exists())  # User created
        user = CustomUser.objects.get(username="testuser")

        self.assertTrue(Pet.objects.filter(user=user).exists())  # Pet assigned
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Account created! You can now log in.", [msg.message for msg in messages])

    def test_signup_invalid_email(self):
        """Test signup with an invalid email format."""
        data = self.valid_user_data.copy()
        data["email"] = "invalid-email"

        response = self.client.post(self.signup_url, data, follow=True)
        self.assertFalse(CustomUser.objects.filter(username="testuser").exists())  # Ensure user isn't created

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Please enter a valid email address.", [msg.message for msg in messages])

    def test_signup_username_already_taken(self):
        """Test if signup fails when the username already exists."""
        CustomUser.objects.create_user(username="testuser", email="testuser@example.com", password="password123")

        response = self.client.post(self.signup_url, self.valid_user_data, follow=True)
        self.assertEqual(CustomUser.objects.filter(username="testuser").count(), 1)  # Ensure duplicate user isn't created

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Username already taken!", [msg.message for msg in messages])

    ## As a user, I cannot signup for an account with two different passwords
    def test_signup_password_mismatch(self):
        data = self.valid_user_data.copy()
        data["password2"] = "DifferentPassword"

        response = self.client.post(self.signup_url, data, follow=True)
        self.assertFalse(CustomUser.objects.filter(username="testuser").exists())  # check user isn't created

    ## As a user, I am assigned the pet I chose during sign-up
    def test_pet_association_on_signup(self):
        """Test if the pet is assigned to the user correctly."""
        self.client.post(self.signup_url, self.valid_user_data, follow=True)
        user = CustomUser.objects.get(username="testuser")

        pet = Pet.objects.filter(user=user).first()
        self.assertIsNotNone(pet)  # Pet should be created
        self.assertEqual(pet.pet_name, "Buddy")
        self.assertEqual(pet.pet_type, "Dog")

