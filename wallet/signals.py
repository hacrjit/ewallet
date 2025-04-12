import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Wallet, Transaction, AuditLog, Notification
from django.db.models.signals import pre_save, post_save

logger = logging.getLogger(__name__)

# Store previous state in pre_save
@receiver(pre_save, sender=Wallet)
def capture_wallet_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_is_active = Wallet.objects.get(pk=instance.pk).is_active
        except Wallet.DoesNotExist:
            instance._previous_is_active = None


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)


# for logging 
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

@receiver(post_save, sender=Transaction)
def log_transaction(sender, instance, created, **kwargs):
    if created:
        user = instance.wallet.user
        message = f"[{instance.timestamp}] {user.username} {'received' if instance.transaction_type == 'credit' else 'sent'} ₹{instance.amount} | New Balance: ₹{instance.wallet.balance}"
        
        # Log the transaction
        logger.info(message)


# for sending notifications
@receiver(post_save, sender=Transaction)
def notify_transaction(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.wallet.user,
            title=f"{'Credit' if instance.transaction_type == 'credit' else 'Debit'} of ₹{instance.amount}",
            message=f"Your wallet was {'credited' if instance.transaction_type == 'credit' else 'debited'} with ₹{instance.amount}. New balance: ₹{instance.wallet.balance}",
            description=instance.description
        )

@receiver(post_save, sender=Wallet)
def notify_wallet_activation(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_previous_is_active'):
        if not instance._previous_is_active and instance.is_active:
            Notification.objects.create(
                user=instance.user,
                title="Wallet Activated",
                message="Your wallet is now active and ready to use."
            )