from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class WalletAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

        # ✅ Get JWT token by calling the login endpoint
        response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })

        self.assertEqual(response.status_code, 200)
        access_token = response.data['access']

        # ✅ Use the access token in Authorization header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        # ✅ Ensure wallet is active
        self.user.wallet.is_active = True
        self.user.wallet.save()

    def test_get_wallet_detail(self):
        response = self.client.get('/api/wallet/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('balance', response.data)

    def test_add_money(self):
        response = self.client.post('/api/wallet/add/', {'amount': '50.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('new_balance', response.data)
