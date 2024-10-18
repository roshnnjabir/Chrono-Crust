# Generated by Django 5.1.2 on 2024-10-17 08:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('brand', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='adminapp.brand')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=3, default=0, max_digits=9)),
                ('description', models.CharField(blank=True, default='', max_length=500, null=True)),
                ('image', models.ImageField(upload_to='uploads/product')),
                ('collection', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='adminapp.collection')),
            ],
        ),
    ]
