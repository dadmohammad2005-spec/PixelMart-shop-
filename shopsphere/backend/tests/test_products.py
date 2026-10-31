from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.products.models import Category, Product

User = get_user_model()


class ProductCatalogTests(APITestCase):
    def setUp(self):
        self.category_elec = Category.objects.create(name='Electronics', slug='electronics', is_active=True)
        self.category_app = Category.objects.create(name='Apparel', slug='apparel', is_active=True)

        self.prod1 = Product.objects.create(
            category=self.category_elec,
            name='Audio Headset Pro',
            slug='audio-headset-pro',
            sku='TEST-SKU-001',
            short_description='Quality studio audio headset',
            description='Detailed description of audio headset.',
            price=Decimal('100.00'),
            sale_price=Decimal('80.00'),
            stock=15,
            is_active=True,
            is_featured=True
        )

        self.prod2 = Product.objects.create(
            category=self.category_elec,
            name='Wireless Mouse',
            slug='wireless-mouse',
            sku='TEST-SKU-002',
            short_description='Ergonomic quiet mouse',
            description='Detailed description of wireless mouse.',
            price=Decimal('40.00'),
            stock=5,
            is_active=True,
            is_featured=False
        )

        self.inactive_prod = Product.objects.create(
            category=self.category_app,
            name='Discontinued Jacket',
            slug='discontinued-jacket',
            sku='TEST-SKU-003',
            description='Inactive product',
            price=Decimal('50.00'),
            stock=0,
            is_active=False
        )

        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admintest@example.com',
            password='AdminPassword123!'
        )

    def test_public_product_listing_only_shows_active(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results can be paginated (DRF pagination structure contains 'results')
        results = response.data['results'] if 'results' in response.data else response.data
        skus = [p['sku'] for p in results]
        self.assertIn('TEST-SKU-001', skus)
        self.assertIn('TEST-SKU-002', skus)
        self.assertNotIn('TEST-SKU-003', skus)

    def test_product_detail_page(self):
        url = reverse('product-detail', kwargs={'slug': 'audio-headset-pro'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Audio Headset Pro')
        self.assertEqual(Decimal(str(response.data['current_price'])), Decimal('80.00'))
        self.assertTrue(response.data['is_on_sale'])

    def test_product_filtering_by_category(self):
        url = reverse('product-list') + '?category=electronics'
        response = self.client.get(url)
        results = response.data['results'] if 'results' in response.data else response.data
        for p in results:
            self.assertEqual(p['category_slug'], 'electronics')

    def test_product_filtering_by_price(self):
        url = reverse('product-list') + '?min_price=50&max_price=150'
        response = self.client.get(url)
        results = response.data['results'] if 'results' in response.data else response.data
        skus = [p['sku'] for p in results]
        self.assertIn('TEST-SKU-001', skus)
        self.assertNotIn('TEST-SKU-002', skus)

    def test_product_search(self):
        url = reverse('product-list') + '?search=Mouse'
        response = self.client.get(url)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['sku'], 'TEST-SKU-002')

    def test_product_sorting_price_asc_desc(self):
        # Sort price asc
        url = reverse('product-list') + '?sort=price_asc'
        response = self.client.get(url)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertTrue(Decimal(str(results[0]['price'])) <= Decimal(str(results[1]['price'])))

        # Sort price desc
        url = reverse('product-list') + '?sort=price_desc'
        response = self.client.get(url)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertTrue(Decimal(str(results[0]['price'])) >= Decimal(str(results[1]['price'])))

    def test_non_admin_cannot_create_product(self):
        url = reverse('product-list')
        payload = {
            'name': 'Hacker Product',
            'sku': 'HACK-01',
            'category': self.category_elec.id,
            'price': 10.0,
            'stock': 10,
            'description': 'Test'
        }
        response = self.client.post(url, payload)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_admin_can_create_product(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-list')
        payload = {
            'name': 'Staff Approved Monitor',
            'sku': 'STAFF-MON-01',
            'category': self.category_elec.id,
            'price': '350.00',
            'stock': 8,
            'description': 'High resolution professional monitor'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(sku='STAFF-MON-01').exists())
