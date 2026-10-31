from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models import Category, Product
from apps.cart.utils import get_or_create_cart
from apps.cart.models import CartItem
from apps.orders.models import Order, OrderItem
from apps.promotions.models import Coupon

User = get_user_model()


class OrderAndCheckoutTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Gadgets', slug='gadgets', is_active=True)
        self.product = Product.objects.create(
            category=self.category,
            name='Precision Stylus',
            slug='precision-stylus',
            sku='TEST-ORD-001',
            price=Decimal('80.00'),
            sale_price=Decimal('60.00'),
            stock=10,
            is_active=True
        )

        self.coupon = Coupon.objects.create(
            code='SAVE10PERCENT',
            discount_type=Coupon.DISCOUNT_PERCENTAGE,
            discount_value=Decimal('10.00'),
            min_order_amount=Decimal('50.00'),
            is_active=True
        )

        self.user = User.objects.create_user(
            username='order_buyer',
            email='buyer@example.com',
            password='BuyerPassword123!',
            first_name='Alice',
            last_name='Buyer'
        )

        self.other_user = User.objects.create_user(
            username='stranger',
            email='stranger@example.com',
            password='StrangerPass123!'
        )

        self.admin = User.objects.create_superuser(
            username='super_admin',
            email='superadmin@example.com',
            password='AdminPassword123!'
        )

    def test_full_checkout_flow_and_inventory_deduction(self):
        self.client.force_authenticate(user=self.user)

        # 1. Add item to cart
        self.client.post(reverse('cart-add-item'), {'product_id': self.product.id, 'quantity': 2})

        # 2. Apply coupon
        self.client.post(reverse('cart-coupon'), {'code': 'SAVE10PERCENT'})

        # 3. Submit checkout
        checkout_payload = {
            'customer_name': 'Alice Buyer',
            'customer_email': 'buyer@example.com',
            'customer_phone': '+15551234567',
            'shipping_name': 'Alice Buyer',
            'shipping_phone': '+15551234567',
            'shipping_address_line1': '742 Evergreen Terrace',
            'shipping_city': 'Springfield',
            'shipping_state': 'OR',
            'shipping_postal_code': '97477',
            'shipping_country': 'United States',
            'shipping_method': 'standard',
            'payment_method': 'COD'
        }

        response = self.client.post(reverse('order-checkout'), checkout_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_number = response.data['order_number']

        # 4. Verify Order was created correctly
        order = Order.objects.get(order_number=order_number)
        self.assertEqual(order.user, self.user)
        # Subtotal: 2 * 60.00 = 120.00
        # Discount: 10% of 120.00 = 12.00
        # Shipping: over $100 => 0.00
        # Total: 120 - 12 + 0 = 108.00
        self.assertEqual(order.subtotal, Decimal('120.00'))
        self.assertEqual(order.discount_amount, Decimal('12.00'))
        self.assertEqual(order.shipping_cost, Decimal('0.00'))
        self.assertEqual(order.total_amount, Decimal('108.00'))

        # 5. Verify inventory deduction: was 10, should now be 8
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

        # 6. Verify historical snapshot in OrderItem
        item = order.items.first()
        self.assertEqual(item.product_name, 'Precision Stylus')
        self.assertEqual(item.price, Decimal('60.00'))
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.line_total, Decimal('120.00'))

        # 7. Even if product price later increases, historical snapshot doesn't change
        self.product.price = Decimal('999.00')
        self.product.sale_price = None
        self.product.save()

        item.refresh_from_db()
        self.assertEqual(item.price, Decimal('60.00'))

    def test_unauthorized_order_access_prevented(self):
        # Create an order for Alice
        order = Order.objects.create(
            user=self.user,
            customer_email='buyer@example.com',
            customer_name='Alice Buyer',
            customer_phone='555-1234',
            shipping_name='Alice Buyer',
            shipping_phone='555-1234',
            shipping_address_line1='123 Test St',
            shipping_city='City',
            shipping_state='State',
            shipping_postal_code='12345',
            shipping_country='USA',
            subtotal=Decimal('50.00'),
            total_amount=Decimal('50.00')
        )

        # Stranger attempts to view Alice's order
        self.client.force_authenticate(user=self.other_user)
        url = reverse('order-detail', kwargs={'order_number': order.order_number})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Alice CAN view her own order
        self.client.force_authenticate(user=self.user)
        alice_response = self.client.get(url)
        self.assertEqual(alice_response.status_code, status.HTTP_200_OK)

    def test_order_cancellation_restores_inventory(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(reverse('cart-add-item'), {'product_id': self.product.id, 'quantity': 3})
        res = self.client.post(reverse('order-checkout'), {
            'customer_name': 'Alice',
            'customer_email': 'buyer@example.com',
            'customer_phone': '555',
            'shipping_name': 'Alice',
            'shipping_phone': '555',
            'shipping_address_line1': '123 St',
            'shipping_city': 'City',
            'shipping_state': 'ST',
            'shipping_postal_code': '00000',
            'payment_method': 'COD'
        })
        order_num = res.data['order_number']
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

        # Cancel order
        cancel_url = reverse('order-cancel', kwargs={'order_number': order_num})
        cancel_res = self.client.post(cancel_url)
        self.assertEqual(cancel_res.status_code, status.HTTP_200_OK)

        # Stock should be restored to 10
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

    def test_admin_metrics_exclude_cancelled_orders(self):
        # Create one confirmed order and one cancelled order
        Order.objects.create(
            user=self.user,
            customer_email='buyer@example.com',
            customer_name='Alice',
            customer_phone='555',
            shipping_name='Alice',
            shipping_phone='555',
            shipping_address_line1='123',
            shipping_city='City',
            shipping_state='ST',
            shipping_postal_code='00000',
            subtotal=Decimal('100.00'),
            total_amount=Decimal('100.00'),
            status=Order.STATUS_CONFIRMED
        )
        Order.objects.create(
            user=self.user,
            customer_email='buyer@example.com',
            customer_name='Alice',
            customer_phone='555',
            shipping_name='Alice',
            shipping_phone='555',
            shipping_address_line1='123',
            shipping_city='City',
            shipping_state='ST',
            shipping_postal_code='00000',
            subtotal=Decimal('500.00'),
            total_amount=Decimal('500.00'),
            status=Order.STATUS_CANCELLED
        )

        self.client.force_authenticate(user=self.admin)
        metrics_url = reverse('admin-dashboard-metrics')
        res = self.client.get(metrics_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Revenue should strictly equal 100.00, NOT 600.00
        self.assertEqual(res.data['metrics']['total_revenue'], 100.0)
