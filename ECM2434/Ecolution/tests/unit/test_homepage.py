from django.test import TestCase
from django.urls import reverse
from Ecolution.models import Task, CustomUser, UserTask

class HomepageTestCase(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')

        # log user in
        self.client.login(username = 'testuser', password = 'password')
        response = self.client.get(reverse('home'))

    ## As a user, I can open and close the menu
    def test_homepage_menu_open(self):
       self.client.get(reverse('home'))
       response = self.client.post(reverse('home'), {'show menu': True}, follow = True)  # TODO: check syntax

       # menu opens up
       self.assertContains(response, 'menu')

       # user deselects menu button
       response = self.client.post(reverse('home'), {'show menu': False}, follow=False)

       # menu closes
       self.assertNotContains(response, 'menu')

    # As a user, I can view my XP
    def test_homepage_view_xp(self):
        response = self.client.get(reverse('home'))

        # check XP bar appears on user page (even if 0 xp)
        self.assertContains(response, 'xp')

    ## As a user, I can view tasks page by selecting "View all"
    def test_homepage_view_all(self):
        response = self.client.get(reverse('home'))

        # check that "View all" button exists
        self.assertContains(response, 'View all')

        # user selects "View all"
        self.client.post(reverse('view_all'))

        # user is redirected to task's page
        self.assertRedirects(response, reverse('tasks'))

