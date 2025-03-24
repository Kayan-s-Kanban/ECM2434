from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser

class LogoutUnitTests(TestCase):
    def setUp(self):
        # create test user
        self.user = CustomUser.objects.create_user(
            username = 'testuser',
            password = 'ComplexPass123!'
        )
        self.url_home = reverse('home')
        self.url_login = reverse('login')
        self.url_settings = reverse('settings')
        self.url_logout = reverse('logout')

        # log in the test user
        self.client.login(username = 'testuser', password = 'validpassword123')

    ## ⚠️ As a user, I can log out of my account
    def test_logout(self):
        # check user is logged in before logging out
        self.client.get(self.url_home)

        # user logs out through settings page
        self.client.get(self.url_settings)
        self.client.get(self.url_logout)

        # check user is logged out by attempting to access a protected page
        #response = self.client.get(reverse('home'))
        #self.assertNotEqual(response, self.client.get(reverse('home')))
        #self.assertNotIn('_auth_user_id', self.client.session)

    ## As a user, I am redirected to "Login"" page after logging out
    def test_logout_redirects_to_login(self):
        response = self.client.get(self.url_logout)

        # check if user is logged out
        self.assertFalse("_auth_user_id" in self.client.session, "User should be logged out.")

        # check user is redirected to login page
        self.assertRedirects(response, self.url_login)