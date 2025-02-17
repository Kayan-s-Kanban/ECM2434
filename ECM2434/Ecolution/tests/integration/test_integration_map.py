from django.test import TestCase
from django.urls import reverse


class MapTestCase(TestCase):
    def SetUp(self):

    ## As a user, I can view the map
    def test_user_views_map(self):
        response = self.client.get(reverse("/map/"))
        self.assertEqual(response.status_code, 200) # user can view the map page

        # TODO: check that map appears and is visible to user

    ## As a user, I can interact with the map
    def test_user_interacts_map(self):
        response = self.client.get(reverse("/map/"))
        self.assertEqual(response.status_code, 200) # user can view the map page

        # TODO: check that user can select a point/event/location on the map?


