# Generated by Django 5.1.2 on 2024-11-11 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0002_alter_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupen',
            name='used_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
