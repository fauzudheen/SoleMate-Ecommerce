# Generated by Django 5.0 on 2024-02-01 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_order', '0016_orderitem_delivery_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='delivery_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]