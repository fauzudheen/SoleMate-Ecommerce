# Generated by Django 5.0 on 2024-02-04 16:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_product_management', '0015_rename_discount_amount_coupon_discount_percent_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usercoupon',
            options={'ordering': ['-id']},
        ),
    ]
