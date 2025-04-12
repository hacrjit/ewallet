from django.db.models.signals import post_save
from wallet.models import Wallet
from django.contrib.auth.models import User
from wallet.signals import create_user_wallet  
from django.test import TestCase 

class WalletTransferTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Disconnect signal before tests
        post_save.disconnect(create_user_wallet, sender=User)

    @classmethod
    def tearDownClass(cls):
        # Reconnect signal after tests
        post_save.connect(create_user_wallet, sender=User)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.sender = User.objects.create_user(username='sender_user', password='password123')
        cls.receiver = User.objects.create_user(username='receiver_user', password='password456')

        cls.sender_wallet = Wallet.objects.create(user=cls.sender, balance=1000.00)
        cls.receiver_wallet = Wallet.objects.create(user=cls.receiver, balance=500.00)
