from django.test import TestCase
from django.urls import reverse
from Ecolution.models import Task, CustomUser, UserTask

class HomepageUnitTests(TestCase):
    def setUp(self):
        # create a test user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')

        # log user in
        self.client.login(username = 'testuser', password = 'password')

        # urls
        self.url_home = reverse('home')
        self.url_index = reverse('index')
        self.url_login = reverse('login')

    # ⚠️As a user, I can view my XP
    def test_homepage_view_xp(self):
        response = self.client.get(self.url_home)

        # check XP bar appears on user page (even if 0 xp)
        self.assertContains(response, 'xp')

    # ⚠️ As a user, I can view tasks page by selecting "View all"
    def test_homepage_view_all(self):
        response = self.client.get(self.url_home)

        # check that "View all" button exists
        self.assertContains(response, 'View All')

        # user selects "View all"
        self.client.post(reverse('view_all')) # TODO: make user select button, this view does not exist

        # user is redirected to task's page
        self.assertRedirects(response, reverse('tasks'))

    # ⚠️As a user, I am redirected to "Home" page if I try accessing "Index"
    def test_index_redirects_to_home(self):
        response = self.client.get(self.url_index)

        self.assertRedirects(response, self.url_login)

