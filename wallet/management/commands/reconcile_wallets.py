from django.core.management.base import BaseCommand
from wallet.models import Wallet, Transaction
from decimal import Decimal

class Command(BaseCommand):
    help = 'Recalculates wallet balances from transactions'

    def handle(self, *args, **kwargs):
        wallets = Wallet.objects.all()
        for wallet in wallets:
            transactions = Transaction.objects.filter(wallet=wallet)
            recalculated_balance = Decimal('0.00')

            for tx in transactions:
                if tx.transaction_type == 'credit':
                    recalculated_balance += tx.amount
                elif tx.transaction_type == 'debit':
                    recalculated_balance -= tx.amount

            if recalculated_balance != wallet.balance:
                self.stdout.write(
                    f"[Mismatch] Wallet ID {wallet.id}: Stored={wallet.balance}, Calculated={recalculated_balance}"
                )
                wallet.balance = recalculated_balance
                wallet.save()
                self.stdout.write(f"[Fixed] Wallet ID {wallet.id} balance updated.")
            else:
                self.stdout.write(f"[OK] Wallet ID {wallet.id} is consistent.")
