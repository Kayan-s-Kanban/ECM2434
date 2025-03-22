from django.test import TestCase
from django.urls import reverse

from Ecolution.models import CustomUser, Event, Pet, ShopItem, UserItem
from Ecolution.views import User


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

## As a user, I cannot buy and assign a shop item that does not exist in the database
    def test_no_shopitem_if_not_exists(self):
        """Test that no ShopItem is assigned if it does not exist in the database."""
        ShopItem.objects.filter(name="Dog").delete()  # Ensure no matching ShopItem exists

        user = User.objects.get(username="testuser")

        user_item = UserItem.objects.filter(user=user).exists()
        self.assertFalse(user_item)  # No UserItem should be assigned if the ShopItem doesn't exist

