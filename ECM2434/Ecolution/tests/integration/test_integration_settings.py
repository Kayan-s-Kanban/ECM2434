from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser

class SettingsTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username = 'testuser', password = 'password')  # create user
        self.client.login(username = 'testuser', password = 'password')  # login user

    ## As a user, I can change my password
    def test_settings_change_pwd(self):
        # user navigates to settings successfully
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)

        # user can enter new password into both fields
        response = self.client.post('change_password',{
                'old_password' : 'password',
                'new_password1': 'new_password',
                'new_password2': 'new_password',
        })

        # user logs out
        self.client.logout()

        # user can login to site with new pwd
        response = self.client.get(reverse('login'))
        self.client.post(reverse('login'),{
            'username' : 'testuser',
            'password' : 'new_password',
        })

    ## As a user, I cannot change my password with incorrect current password
    def test_settings_change_pwd_invalid_currentpwd(self):
        # user navigates to settings successfully
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)

        # user can enter new password into both fields
        response = self.client.post('change_password', {
            'old_password': 'notpassword',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        })

        # user logs out
        self.client.logout()

        # user cannot login to site with new pwd
        response = self.client.get(reverse('login'))
        self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'new_password',
        })

        # user is not redirected to home page
        self.assertNotEqual(response, 'ecolution/home/')

    ## As a user, I cannot change my password with the new password fields not matching
    def test_settings_change_pwd_different_newpwds(self):
        # user navigates to settings successfully
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)

        # user can enter new password into both fields
        response = self.client.post('change_password', {
            'old_password': 'password',
            'new_password1': 'new_password1',
            'new_password2': 'new_password2',
        })

        # user logs out
        self.client.logout()

        # user cannot login to site with the first new password
        response = self.client.get(reverse('login'))
        self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'new_password1',
        })

        # user is not redirected to home page
        self.assertNotEqual(response, 'ecolution/home/')

        # user cannot login to site with the second new password
        response = self.client.get(reverse('login'))
        self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'new_password2',
        })

        # user is not redirected to home page
        self.assertNotEqual(response, 'ecolution/home/')

    ## As a user, I can delete my account
    def test_settings_delete_account(self):
        # user is on settings page
        response = self.client.get(reverse('settings'))

        # user selects "delete account"
        response = self.client.post(reverse('delete_account'))

        # user selects "confirm"
        response = self.client.post(reverse('delete_account'))
        self.assertEqual(response.status_code, 302)

        # user should be logged out
        self.assertNotIn('_auth_user_id', self.client.session)

        # user should no longer exist in database
        try:
            # attempt to get the user from the database
            CustomUser.objects.get(username = 'testuser')
            self.fail("user should not exist in the database")
        except CustomUser.DoesNotExist:
            pass # user is deleted from db




