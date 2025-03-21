from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser

class SettingsTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username = 'testuser', password = 'password')  # create user
        self.client.login(username = 'testuser', password = 'password')  # login user
        self.url_change_password = reverse('change_password')
        self.url_change_username = reverse('change_username')

    ## As a user, I can change my password
    def test_settings_change_pwd(self):
        # user can enter new password into both fields
        response = self.client.post('change_password',{
                'old_password' : 'password',
                'new_password1': 'new_password',
                'new_password2': 'new_password',
        })

        self.client.logout()

        # user can log in to site with new pwd
        response = self.client.get(reverse('login'))
        self.client.post(reverse('login'),{
            'username' : 'testuser',
            'password' : 'new_password',
        })

    ## As a user, I cannot change my password with incorrect current password
    def test_settings_change_pwd_invalid_currentpwd(self):
        # send POST request with incorrect current password
        response = self.client.post(self.url_change_password, {
            "current_password": "wrongpassword123",
            "new_password1": "newpassword123",
            "new_password2": "newpassword123"
        })

        # check response redirects to the settings page with an error message
        self.assertRedirects(response, reverse("settings"))

        # check if the error message is present
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Current password is incorrect!")

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

    def test_get_request_redirects(self):
        # send GET request (which should be rejected)
        response = self.client.get(self.url_change_password)

        # check response redirects to the settings page
        self.assertRedirects(response, reverse("settings"))

    def test_password_not_changed_when_get_request(self):
        # save current password hash
        current_password_hash = self.user.password

        # try to change password with a GET request
        self.client.get(self.url_change_password)

        # refresh the user object from the database
        self.user.refresh_from_db()

        # check the password hash remains the same
        self.assertEqual(self.user.password, current_password_hash)

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

    def test_username_changed_successfully(self):
        data = {
            "current_username": "old_username",  # Current username
            "new_username1": "new_username",     # New username
            "new_username2": "new_username",     # Confirm new username
        }

        response = self.client.post(self.url_change_username, data)

        # refresh the user from the database to check if the username was updated
        self.user.refresh_from_db()

        # check username has been successfully updated
        self.assertEqual(self.user.get_username(), "new_username")

        # Check if the response contains a success message
        self.assertContains(response, "Username updated successfully!")

    ## As a user, I cannot change my username if I enter two different usernames
    def test_username_mismatch_error(self):
        data = {
            'current_username': 'oldusername',
            'new_username1': 'newusername1',  # new username
            'new_username2': 'wrongusername',  # confirm new username (mismatch)
        }
        response = self.client.post(self.url_change_username, data)

        # assert a redirect response to the settings page
        self.assertRedirects(response, reverse("settings"))

        # check that the username was not changed
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, 'oldusername')

    def test_incorrect_current_username_error(self):
        data = {
            'current_username': 'incorrectusername',
            'new_username1': 'newusername',
            'new_username2': 'newusername',
        }
        response = self.client.post(self.url_change_username, data)

        # check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Current username is incorrect!')

        # check username was not changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'oldusername')

        self.assertRedirects(response, 'settings')  # Update this if needed

    def test_invalid_request_method(self):
        response = self.client.get(self.url_change_username)
        self.assertRedirects(response, '/ecolution/settings/')

    def test_user_not_logged_in(self):
        self.client.logout()
        data = {
            'current_username': 'oldusername',
            'new_username1': 'newusername',
            'new_username2': 'newusername',
        }
        response = self.client.post(self.url_change_username, data)

        # should redirect to login page if not authenticated
        self.assertRedirects(response, '/ecolution/login/?next=' + self.url_change_username)

    ## As a user, I cannot change my username if the username already exists for another account
    def test_username_not_unique(self):
        second_user = CustomUser.objects.create_user(
            username='seconduser', password='password123'
        )

        data = {
            'current_username': 'oldusername',
            'new_username1': 'seconduser',  # try to change to an existing username
            'new_username2': 'seconduser',
        }
        response = self.client.post(self.url_change_username, data)

        # check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Username already exists.')

        # check username was not changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'oldusername')



