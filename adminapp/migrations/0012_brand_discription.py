# Generated by Django 5.1.2 on 2024-11-19 04:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0011_remove_brand_image_brand_banner_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='discription',
            field=models.TextField(default=datetime.datetime(2024, 11, 19, 4, 39, 45, 671195, tzinfo=datetime.timezone.utc), max_length=50),
            preserve_default=False,
        ),
    ]
