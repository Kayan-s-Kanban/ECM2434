from django.test import TestCase
from django.urls import reverse


class MapTestCase(TestCase):
    def SetUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # log user in
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('home'))

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

    ## As a user, I can open and close the menu
    def test_map_menu(self):
        # user selects menu button
        response = self.client.post(reverse('events'), {'show menu': True}, follow=True)  # TODO: check syntax

        # menu opens up
        self.assertContains(response, 'menu')


