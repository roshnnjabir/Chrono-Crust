# Generated by Django 5.1.2 on 2024-11-28 00:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0026_ledger_alter_order_payment_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Ledger',
        ),
    ]
