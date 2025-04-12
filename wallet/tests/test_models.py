# wallet/tests/test_models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from wallet.models import Transaction
from decimal import Decimal

User = get_user_model()

class WalletModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser1', password='pass123')

    def test_wallet_created(self):
        self.assertTrue(hasattr(self.user, 'wallet'))
        self.assertEqual(self.user.wallet.balance, Decimal('0.00'))

    def test_transaction_creation(self):
        wallet = self.user.wallet
        wallet.balance = Decimal(wallet.balance) + Decimal('100.00')
        wallet.save()
        tx = Transaction.objects.create(wallet=wallet, amount=Decimal('100.00'), transaction_type='credit')
        self.assertEqual(tx.amount, Decimal('100.00'))
        self.assertEqual(tx.transaction_type, 'credit')
        self.assertEqual(wallet.transactions.count(), 1)
