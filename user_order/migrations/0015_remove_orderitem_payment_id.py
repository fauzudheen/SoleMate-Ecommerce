# Generated by Django 5.0 on 2024-01-30 10:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_order', '0014_remove_payment_razorpay_order_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='payment_id',
        ),
    ]
