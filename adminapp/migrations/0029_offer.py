# Generated by Django 5.1.2 on 2024-11-28 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0028_alter_order_payment_status_delete_offer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], max_length=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('applicable_brands', models.ManyToManyField(blank=True, to='adminapp.brand')),
                ('applicable_collections', models.ManyToManyField(blank=True, to='adminapp.collection')),
                ('applicable_products', models.ManyToManyField(blank=True, to='adminapp.product')),
            ],
        ),
    ]