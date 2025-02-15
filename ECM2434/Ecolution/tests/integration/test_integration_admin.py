from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser

class AdminTestCase(TestCase):
    def setUp(self):
        # create admin user
        self.user = CustomUser.objects.create_user(
            username = 'admin',
            password = 'password'
        )

        self.admin_url = reverse('admin')
        self.client.login(username = 'admin', password = 'password')

    ## As an admin, I can log into admin page
    def test_admin_login(self):
        # attempt to log in with correct credentials
        response = self.client.post(self.admin_url, {
            'username': 'admin',
            'password': 'password',
        })

        # check that the user is logged in and redirected to the intended page
        self.assertRedirects(response, '/admin/')
        # or check if the user is logged in using session or user info
        self.assertTrue('_auth_user_id', self.client.session)

    ## As an admin, I cannot log into admin page with invalid user
    def test_admin_login_invalid_user(self):
        # attempt to log in with invalid user
        response = self.client.post(self.admin_url, {
            'username': 'notAdmin',
            'password': 'password',
        })

        # check that the user is logged in and redirected to the intended page
        self.assertNotEqual(response, '/admin/')
        # or check if the user is logged in using session or user info
        self.assertFalse('_auth_user_id', self.client.session)

    # As an admin, I cannot log into admin page with invalid password
    def test_admin_login_invalid_pwd(self):
        # attempt to log in with invalid password
        response = self.client.post(self.admin_url, {
            'username': 'Admin',
            'password': 'notPassword',
        })

        # check that the user is logged in and redirected to the intended page
        self.assertNotEqual(response, '/admin/')
        # or check if the user is logged in using session or user info
        self.assertFalse('_auth_user_id', self.client.session)

    ## As an admin, I can add content
    ## As an admin, I can remove content
    ## As an admin, I can edit content
    ## As an admin, I can remove(?) users
    ## As an admin, I can add(?) users
