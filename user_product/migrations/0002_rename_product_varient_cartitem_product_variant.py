# Generated by Django 5.0 on 2024-01-14 04:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_product', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='product_varient',
            new_name='product_variant',
        ),
    ]
