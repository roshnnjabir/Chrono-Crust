# Generated by Django 5.1.2 on 2024-11-26 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0019_alter_order_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('cod', 'Cod'), ('pwallet', 'Personal Wallet'), ('paid', 'Paid'), ('refunded', 'Refunded')], default='pending', max_length=8),
        ),
    ]
