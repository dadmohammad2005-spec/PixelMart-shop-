from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models import Category, Product
from apps.wishlist.models import WishlistItem
from apps.cart.models import Cart

User = get_user_model()


class WishlistTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Fitness', slug='fitness', is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            name='Yoga Block Set',
            slug='yoga-block-set',
            sku='TEST-WISH-01',
            price=Decimal('25.00'),
            stock=15,
            is_active=True
        )
        self.user = User.objects.create_user(
            username='wishlist_fan',
            email='fan@example.com',
            password='FanPassword123!'
        )

    def test_anonymous_cannot_access_wishlist(self):
        url = reverse('wishlist-list-create')
        res = self.client.get(url)
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_authenticated_add_and_view_wishlist(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('wishlist-list-create')

        # Add to wishlist
        add_res = self.client.post(url, {'product_id': self.product.id})
        self.assertEqual(add_res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

        # View wishlist
        view_res = self.client.get(url)
        self.assertEqual(view_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(view_res.data), 1)
        self.assertEqual(view_res.data[0]['product']['sku'], 'TEST-WISH-01')

    def test_move_wishlist_item_to_cart(self):
        self.client.force_authenticate(user=self.user)
        # Add to wishlist
        WishlistItem.objects.create(user=self.user, product=self.product)

        # Move to cart
        move_url = reverse('wishlist-move-to-cart', kwargs={'product_id': self.product.id})
        move_res = self.client.post(move_url)
        self.assertEqual(move_res.status_code, status.HTTP_200_OK)

        # Wishlist should now be empty
        self.assertFalse(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

        # User's cart should have 1 item
        user_cart = Cart.objects.get(user=self.user)
        self.assertEqual(user_cart.total_items, 1)
