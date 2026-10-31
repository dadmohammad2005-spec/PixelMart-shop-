from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.accounts.models import Address

User = get_user_model()


class AccountsAuthTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'john_doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567890',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
        }
        self.existing_user = User.objects.create_user(
            username='jane_smith',
            email='jane@example.com',
            password='JanePassword123!',
            first_name='Jane',
            last_name='Smith'
        )

    def test_user_registration_success(self):
        url = reverse('register')
        response = self.client.post(url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='john@example.com').exists())
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'john@example.com')

    def test_user_registration_password_mismatch(self):
        url = reverse('register')
        bad_data = self.user_data.copy()
        bad_data['password_confirm'] = 'DifferentPassword123!'
        response = self.client.post(url, bad_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_login_with_email(self):
        url = reverse('login')
        response = self.client.post(url, {
            'email': 'jane@example.com',
            'password': 'JanePassword123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'jane@example.com')

    def test_user_login_invalid_credentials(self):
        url = reverse('login')
        response = self.client.post(url, {
            'email': 'jane@example.com',
            'password': 'WrongPassword123!'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout(self):
        self.client.force_authenticate(user=self.existing_user)
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_view_and_update(self):
        self.client.force_authenticate(user=self.existing_user)
        url = reverse('profile')
        # GET profile
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Jane')

        # Update profile
        update_response = self.client.put(url, {'first_name': 'Janet', 'phone_number': '555-0199'})
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.existing_user.refresh_from_db()
        self.assertEqual(self.existing_user.first_name, 'Janet')

    def test_address_management_and_isolation(self):
        self.client.force_authenticate(user=self.existing_user)
        url = reverse('address-list')

        # Add address
        address_payload = {
            'full_name': 'Jane Smith',
            'phone_number': '555-0199',
            'address_line1': '100 Market St',
            'city': 'San Francisco',
            'state': 'CA',
            'postal_code': '94105',
            'country': 'United States',
            'is_default_shipping': True
        }
        res = self.client.post(url, address_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        address_id = res.data['id']

        # Verify address belongs to jane
        address = Address.objects.get(id=address_id)
        self.assertEqual(address.user, self.existing_user)

        # Another user cannot view jane's address
        other_user = User.objects.create_user(username='other', email='other@example.com', password='Password123!')
        self.client.force_authenticate(user=other_user)
        list_res = self.client.get(url)
        results = list_res.data['results'] if 'results' in list_res.data else list_res.data
        self.assertEqual(len(results), 0)
