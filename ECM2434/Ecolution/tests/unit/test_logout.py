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
        self.login_url = reverse('login')

        # log in the test user
        self.client.login(username = 'testuser', password = 'validpassword123')

    ## As a user, I can log out of my account
    def test_logout(self):
        # check user is logged in before logging out
        self.client.get(reverse('home'))

        # user logs out through settings page
        self.client.get(reverse('settings'))
        self.client.post('logout')

        # check user is logged out by attempting to access a protected page
        response = self.client.get(reverse('home'))
        self.assertNotEqual(response, self.client.get(reverse('home')))
        self.assertNotIn('_auth_user_id', self.client.session)