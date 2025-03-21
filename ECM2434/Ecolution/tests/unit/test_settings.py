import json

from django.test import TestCase
from django.urls import reverse
from Ecolution.models import CustomUser
from Ecolution.models import UserTask
from Ecolution.models import Task

class SettingsTestCase(TestCase):
    def setUp(self):
        # create user
        self.user = CustomUser.objects.create_user(username = 'testuser', password = 'password')

        # login user
        self.client.login(username = 'testuser', password = 'password')

        # urls
        self.url_settings = reverse('settings')
        self.url_update_fontsize = reverse('update_fontsize')
        self.url_get_fontsize = reverse('get_fontsize')

        # Constants for font size options
        self.font_size_small = 10
        self.font_size_medium = 16
        self.font_size_large = 18
        self.invalid_font_size = 999

    def test_valid_font_size_update(self):
        data = {
            'preferred_font_size': self.font_size_medium,
        }

        # convert data to JSON format
        response = self.client.post(self.url_update_fontsize, json.dumps(data), content_type="application/json")

        # check data entry was successful
        self.assertEqual(response.status_code, 200)

        # refresh the user from the database and check font size was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.preferred_font_size, self.font_size_medium)

    def test_invalid_font_size(self):
        data = {
            'preferred_font_size': self.invalid_font_size,
        }

        # convert the data to JSON format
        response = self.client.post(self.url_update_fontsize, json.dumps(data), content_type="application/json")

        # check response indicates an error
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"status": "error", "message": "Invalid font size"})

    def test_missing_font_size(self):
        data = {}  # No font size key

        # convert the data to JSON format
        response = self.client.post(self.url_update_fontsize, json.dumps(data), content_type="application/json")

        # check response indicates an error
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"status": "error", "message": "Invalid font size"})

    def test_invalid_json_format(self):
        # send a malformed JSON body (e.g., missing a closing brace)
        response = self.client.post(self.url_update_fontsize, '{"preferred_font_size": 14',
                                    content_type="application/json")

        # check response indicates an error due to invalid JSON
        self.assertEqual(response.status_code, 200)

    def test_non_post_request(self):
        # try sending a GET request instead of a POST
        response = self.client.get(self.url_update_fontsize)

        # check response indicates an error
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"status": "error", "message": "Invalid request"})