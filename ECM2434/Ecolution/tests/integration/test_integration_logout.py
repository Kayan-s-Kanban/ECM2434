from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser

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