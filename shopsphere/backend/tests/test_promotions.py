from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.promotions.models import Coupon, Announcement, NewsletterSubscriber


class PromotionsAndCouponsTests(APITestCase):
    def setUp(self):
        self.percentage_coupon = Coupon.objects.create(
            code='DISCOUNT20',
            discount_type=Coupon.DISCOUNT_PERCENTAGE,
            discount_value=Decimal('20.00'),
            min_order_amount=Decimal('50.00'),
            max_discount_amount=Decimal('40.00'),
            is_active=True
        )

        self.inactive_coupon = Coupon.objects.create(
            code='EXPIRED50',
            discount_type=Coupon.DISCOUNT_FIXED,
            discount_value=Decimal('50.00'),
            is_active=False
        )

        self.announcement = Announcement.objects.create(
            message='Summer promotion: Save 20% storewide',
            is_active=True
        )

    def test_coupon_validation_success(self):
        url = reverse('validate-coupon')
        response = self.client.post(url, {'code': 'DISCOUNT20', 'subtotal': '100.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 20% of 100 is 20.00
        self.assertEqual(Decimal(str(response.data['calculated_discount'])), Decimal('20.00'))

    def test_coupon_validation_max_discount_cap(self):
        url = reverse('validate-coupon')
        # 20% of 300 is 60, but max cap is 40.00
        response = self.client.post(url, {'code': 'DISCOUNT20', 'subtotal': '300.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(str(response.data['calculated_discount'])), Decimal('40.00'))

    def test_coupon_validation_below_min_order(self):
        url = reverse('validate-coupon')
        response = self.client.post(url, {'code': 'DISCOUNT20', 'subtotal': '30.00'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('minimum', response.data['error'].lower())

    def test_inactive_coupon_rejected(self):
        url = reverse('validate-coupon')
        response = self.client.post(url, {'code': 'EXPIRED50', 'subtotal': '100.00'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_newsletter_subscription(self):
        url = reverse('newsletter-subscribe')
        res = self.client.post(url, {'email': 'subscriber@example.com'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(NewsletterSubscriber.objects.filter(email='subscriber@example.com').exists())

        # Bad email format
        bad_res = self.client.post(url, {'email': 'not-an-email'})
        self.assertEqual(bad_res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_active_announcement_retrieval(self):
        url = reverse('active-announcement')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['message'], 'Summer promotion: Save 20% storewide')
