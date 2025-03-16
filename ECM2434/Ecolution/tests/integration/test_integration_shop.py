from django.test import TestCase
from django.urls import reverse

from Ecolution.models import CustomUser, Event, Pet, ShopItem


class ShopIntegrationTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username='testuser', password='password')

        self.client.login(username = 'testuser', password = 'password')

        # add points to the user
        self.user1.points += 50
        self.user1.save()  # save to the database (user now has 50 points)

        # refresh from the database
        self.user1.refresh_from_db()

        # create new item in shop
        self.item1 = ShopItem.objects.create(
            name = 'item1',
            price = 10
        )

    # As a user, I can purchase an item multiple times after a cooldown period

    # As a user, I can purchase an item, and the points are removed from my account
    def test_shop_user_points_decrease(self):
        # check user starts with 50 points
        self.assertEqual(self.user1.points, 50)

        # user buys shop item
        response = self.client.post(reverse('buy_item', args = [self.item1.id]))
        self.assertEqual(response.status_code, 200)
        print(response.content)

        # refresh from the database
        self.user1.refresh_from_db()

        # check user now has 40 points
        self.assertEqual(self.user1.points, 40)
