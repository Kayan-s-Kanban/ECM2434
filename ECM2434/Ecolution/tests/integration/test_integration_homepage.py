from django.test import TestCase
from django.urls import reverse

class HomepageTestCase(TestCase):
    # As a user, I can view my pet
    # As a user, I can view my current tasks

    # As a user, I can open and close the menu
    def test_homepage_menu(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('home'))

        # user selects menu button
        response = self.client.post(reverse('home'), {'show menu': True}, follow=True)  # TODO: check syntax

        # menu opens up
        self.assertContains(response, 'menu')

    # As a user, I can view my XP
    # As a user, I can remove a current task from my list
    # As a user, I can see my points increase after completing a task
    # As a user, I can see my points decrease after removing a completed task