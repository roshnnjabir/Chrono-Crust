# Generated by Django 5.1.2 on 2024-12-11 04:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0031_collection_created_at_alter_collection_brand_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('DEPOSIT', 'Wallet Deposit'), ('WITHDRAWAL', 'Wallet Withdrawal'), ('PURCHASE', 'Purchase'), ('REFUND', 'Refund')], max_length=20)),
                ('payment_method', models.CharField(choices=[('RAZORPAY', 'Razorpay'), ('STRIPE', 'Stripe'), ('PAYPAL', 'PayPal'), ('BANK_TRANSFER', 'Bank Transfer')], max_length=20)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('SUCCESS', 'Successful'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')], max_length=20)),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=100, null=True)),
                ('razorpay_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to=settings.AUTH_USER_MODEL)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='adminapp.personalwallet')),
            ],
            options={
                'verbose_name_plural': 'Transaction Histories',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.DeleteModel(
            name='PersonalWalletTransactions',
        ),
    ]