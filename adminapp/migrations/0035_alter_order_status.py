# Generated by Django 5.1.2 on 2024-12-14 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0034_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('return_requested', 'Return Requested'), ('returned', 'Returned'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
    ]
