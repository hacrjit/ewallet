from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Wallet, Transaction, AuditLog

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)



@receiver(post_save, sender=Transaction)
def log_transaction(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            user=instance.wallet.user,
            action='money_added' if instance.transaction_type == 'credit' else 'money_withdrawn',
            message=f"{instance.transaction_type.title()} ₹{instance.amount} to wallet"
        )

@receiver(post_save, sender=Wallet)
def log_wallet_activation(sender, instance, created, **kwargs):
    if not created and instance.is_active:
        AuditLog.objects.get_or_create(
            user=instance.user,
            action='wallet_activated',
            message="Wallet activated"
        )