# Generated by Django 5.0 on 2024-01-29 08:33

import admin_product_management.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_product_management', '0010_alter_brand_name_alter_category_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(validators=[admin_product_management.models.validate_price]),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='quantity',
            field=models.IntegerField(validators=[admin_product_management.models.validate_quantity]),
        ),
    ]