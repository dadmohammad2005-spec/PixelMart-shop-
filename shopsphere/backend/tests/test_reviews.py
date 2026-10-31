from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.reviews.models import Review

User = get_user_model()


class ReviewSystemTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Tech', slug='tech', is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            name='Ergonomic Chair',
            slug='ergonomic-chair',
            sku='REV-CHAIR-01',
            price=Decimal('250.00'),
            stock=10,
            is_active=True
        )

        self.buyer = User.objects.create_user(
            username='verified_buyer',
            email='verified@example.com',
            password='Password123!'
        )

        self.non_buyer = User.objects.create_user(
            username='casual_user',
            email='casual@example.com',
            password='Password123!'
        )

        # Create confirmed order for verified_buyer
        order = Order.objects.create(
            user=self.buyer,
            customer_email='verified@example.com',
            customer_name='Verified Buyer',
            customer_phone='555',
            shipping_name='Verified',
            shipping_phone='555',
            shipping_address_line1='123 Road',
            shipping_city='City',
            shipping_state='State',
            shipping_postal_code='00000',
            subtotal=Decimal('250.00'),
            total_amount=Decimal('250.00'),
            status=Order.STATUS_CONFIRMED
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            product_sku=self.product.sku,
            price=self.product.price,
            quantity=1,
            line_total=self.product.price
        )

    def test_verified_purchase_review_submission(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('review-list')
        payload = {
            'product_slug': 'ergonomic-chair',
            'rating': 5,
            'title': 'Exceptional comfort and posture support',
            'comment': 'I have used this chair for 3 weeks and my back pain is completely gone.'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        review = Review.objects.get(product=self.product, user=self.buyer)
        self.assertTrue(review.is_verified_purchase)
        self.assertEqual(review.rating, 5)

    def test_duplicate_review_prevention(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('review-list')
        payload = {
            'product_slug': 'ergonomic-chair',
            'rating': 5,
            'title': 'First Review',
            'comment': 'First review comment.'
        }
        first_res = self.client.post(url, payload)
        self.assertEqual(first_res.status_code, status.HTTP_201_CREATED)

        # Attempt second review for same product
        second_res = self.client.post(url, payload)
        self.assertEqual(second_res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_rating_value_rejected(self):
        self.client.force_authenticate(user=self.non_buyer)
        url = reverse('review-list')
        # Rating 6 is invalid (must be 1-5)
        payload = {
            'product_slug': 'ergonomic-chair',
            'rating': 6,
            'title': 'Invalid rating',
            'comment': 'Rating out of range.'
        }
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
