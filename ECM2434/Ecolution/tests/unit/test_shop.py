from django.test import TestCase
from django.urls import reverse
from django.db import connection
from Ecolution.models import CustomUser, Event, Pet, ShopItem

class ShopTest(TestCase):
    def setUp(self):
        # create and login new user
        self.user1 = CustomUser.objects.create_user(username = 'testuser', password = 'password')
        self.client.login(username = 'testuser', password = 'password')

        # create new item in shop
        self.item1 = ShopItem.objects.create(
            name = 'item1',
            price = 0
        )

    # As a user, I can access the Shop page
    def test_view_shop(self):
        # user redirects to "Shop" page
        response = self.client.get(reverse('shop'))

        # user is redirected to the correct URL
        print(response.content)
        self.assertEqual(response.status_code, 200)

    # As a user, I can view the name of an item
    def test_view_item_name(self):
        # user navigates to shop item
        response = self.client.post(reverse('buy_item', args=[self.item1.id]))
        self.assertEqual(response.status_code, 200)

        # check item name matches db
        print(response.content)
        self.assertContains(response, self.item1.name)

    # As a user, I can see the price of an item
    def test_view_item_price(self):
        # user navigates to shop item
        response = self.client.post(reverse('buy_item', args = [self.item1.id]))
        self.assertEqual(response.status_code, 200)

        # check item name matches db
        print(response.content)
        self.assertContains(response, self.item1.price)

    # As a user, I can see the description of an item <-- check if having description for shop items
    #def test_view_item_description(self):
        # user navigates to shop item
    #    response = self.client.get(reverse('shop', args = [self.item1.id]))
    #    self.assertEqual(response.status_code, 200)

        # check item name matches db
    #    self.assertContains(response, self.item1.description)

    # As a user, I can see a picture of an item
    def test_view_item_image(self):
        # user navigates to shop item
        response = self.client.post(reverse('buy_item', args = [self.item1.id]))
        self.assertEqual(response.status_code, 200)

    # As a user, I cannot purchase a one-time-purchase item more than once
    def test_cannot_buy_item_again(self):
        # user buys shop item
        response = self.client.post(reverse('buy_item', args=[self.item1.id]))
        self.assertEqual(response.status_code, 200)
        print(response.content)

        # check item no longer has "available"/"buy" button OR user cannot select button again
        response = self.client.post(reverse('buy_item', args=[self.item1.id]))
        self.assertNotEqual(response.status_code, 200)
        print(response.content)
