from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models import Category, Product
from apps.cart.models import Cart, CartItem
from apps.cart.utils import merge_session_cart

User = get_user_model()


class CartOperationsTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Home', slug='home', is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            name='Desk Organizer',
            slug='desk-organizer',
            sku='TEST-CART-001',
            price=Decimal('50.00'),
            sale_price=Decimal('40.00'),
            stock=10,
            is_active=True
        )
        self.user = User.objects.create_user(
            username='cart_user',
            email='cartuser@example.com',
            password='CartPassword123!'
        )

    def test_anonymous_user_can_add_to_cart(self):
        url = reverse('cart-add-item')
        response = self.client.post(url, {
            'product_id': self.product.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_data = response.data['cart']
        self.assertEqual(cart_data['total_items'], 2)
        # Unit price is 40.00, so line total is 80.00
        self.assertEqual(Decimal(str(cart_data['subtotal'])), Decimal('80.00'))

    def test_add_to_cart_stock_validation(self):
        url = reverse('cart-add-item')
        # Try to add 15 items when only 10 in stock
        response = self.client.post(url, {
            'product_id': self.product.id,
            'quantity': 15
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', response.data['error'].lower())

    def test_update_cart_item_quantity(self):
        # First add 2
        self.client.post(reverse('cart-add-item'), {'product_id': self.product.id, 'quantity': 2})

        # Get cart
        cart_res = self.client.get(reverse('cart-detail'))
        item_id = cart_res.data['items'][0]['id']

        # Update to 4
        update_url = reverse('cart-item-detail', kwargs={'item_id': item_id})
        update_res = self.client.put(update_url, {'quantity': 4})
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)
        self.assertEqual(update_res.data['cart']['total_items'], 4)

    def test_remove_cart_item(self):
        self.client.post(reverse('cart-add-item'), {'product_id': self.product.id, 'quantity': 2})
        cart_res = self.client.get(reverse('cart-detail'))
        item_id = cart_res.data['items'][0]['id']

        # Delete item
        del_url = reverse('cart-item-detail', kwargs={'item_id': item_id})
        del_res = self.client.delete(del_url)
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertEqual(del_res.data['cart']['total_items'], 0)

    def test_clear_cart(self):
        self.client.post(reverse('cart-add-item'), {'product_id': self.product.id, 'quantity': 2})
        clear_res = self.client.delete(reverse('cart-detail'))
        self.assertEqual(clear_res.status_code, status.HTTP_200_OK)
        self.assertEqual(clear_res.data['cart']['total_items'], 0)

    def test_cart_merge_on_login(self):
        # 1. Anonymous visitor adds item to cart
        self.client.post(reverse('cart-add-item'), {'product_id': self.product.id, 'quantity': 3})
        session_key = self.client.session.session_key
        anon_cart = Cart.objects.get(session_key=session_key, user=None)
        self.assertEqual(anon_cart.total_items, 3)

        # 2. User logs in
        login_res = self.client.post(reverse('login'), {
            'email': 'cartuser@example.com',
            'password': 'CartPassword123!'
        })
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

        # 3. Verify user's cart now has the merged items
        user_cart = Cart.objects.get(user=self.user)
        self.assertEqual(user_cart.total_items, 3)

        # 4. Old anonymous cart deleted
        self.assertFalse(Cart.objects.filter(id=anon_cart.id).exists())
