# Generated by Django 5.0 on 2024-01-13 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_product_management', '0004_product_discounted_price_alter_offer_product_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discounted_price',
            field=models.IntegerField(default=0),
        ),
    ]