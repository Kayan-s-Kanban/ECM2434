from django.urls import reverse
from Ecolution.models import CustomUser
from Ecolution.tests.base_test import BaseTestCase

class HomepageUnitTests(BaseTestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')

        # log user in
        self.client.login(username = 'testuser', password = 'password')

        # urls
        self.url_home = reverse('home')
        self.url_login = reverse('login')

    #️As a user, I can view my XP
    def test_homepage_view_xp(self):
        response = self.client.get(self.url_home)

        # check XP bar appears on user page (even if 0 xp)
        self.assertContains(response, 'xp')

    # As a user, I can view current tasks
    def test_homepage_view_current_tasks(self):
        response = self.client.get(self.url_home)

        # check that "Tasks" section
        self.assertContains(response, 'Current Tasks')
