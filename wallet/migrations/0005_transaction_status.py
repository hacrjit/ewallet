# Generated by Django 5.2 on 2025-04-10 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0004_transaction_wallet_tran_wallet__168f5a_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=10),
        ),
    ]
