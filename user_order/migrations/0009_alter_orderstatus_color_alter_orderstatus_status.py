# Generated by Django 5.0 on 2024-01-18 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_order', '0008_alter_orderstatus_is_listed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderstatus',
            name='color',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='status',
            field=models.CharField(max_length=100),
        ),
    ]