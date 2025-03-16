from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser, Event, Pet

class GDPRPPTestCase(TestCase):
    def setUp(self):
        # create + login user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')

    # As a user, I can view the Terms and Conditions page within the app
    def test_view_gdpr(self):
        # login user
        self.client.login(username = 'testuser', password = 'password')

        # navigate to settings
        self.client.get(reverse('settings'))

        # navigate to T&C and PP
        self.client.get(reverse('term_of_use'))

    # As a user, I can view the Terms and Conditions page on signup
    def test_view_gdpr_signup(self):
        # navigate to signup page
        self.client.get(reverse('signup'))

        # navigate to T&C and PP
        self.client.get(reverse('term_of_use'))

    # As a user, I can agree to the Privacy Policy and Terms and Conditions
    def test_agree_gdpr_pp(self):
        # redirect to signup page
        self.client.get(reverse('signup'))

        # user selects agree button
        response = self.client.get(reverse('term_of_use'), {
            'agree_terms' : 'on',
        })

        # assert that the response says terms were agreed to
        self.assertNotContains(response, "You must agree to the terms and conditions")