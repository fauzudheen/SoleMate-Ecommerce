# Generated by Django 5.0 on 2024-01-16 15:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_order', '0004_alter_orderstatus_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_status',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_status',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='order_status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user_order.orderstatus'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='payment_method',
            field=models.CharField(default='Default', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='payment_status',
            field=models.CharField(default='Pending', max_length=100),
        ),
    ]
