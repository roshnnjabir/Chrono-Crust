# Generated by Django 5.1.2 on 2024-11-24 12:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0014_order_total_discount_alter_coupen_min_required'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collection',
            old_name='image',
            new_name='banner_image',
        ),
        migrations.AddField(
            model_name='collection',
            name='logo_image',
            field=models.ImageField(default=datetime.datetime(2024, 11, 24, 12, 45, 8, 720538, tzinfo=datetime.timezone.utc), upload_to='uploads/collection'),
            preserve_default=False,
        ),
    ]
