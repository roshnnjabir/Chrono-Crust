# Generated by Django 5.1.2 on 2024-11-26 04:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0017_alter_order_address'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalwallet',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='personal_wallet', to=settings.AUTH_USER_MODEL),
        ),
    ]
