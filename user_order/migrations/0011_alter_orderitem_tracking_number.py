# Generated by Django 5.0 on 2024-01-20 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_order', '0010_alter_order_options_alter_orderaddress_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='tracking_number',
            field=models.IntegerField(),
        ),
    ]
