# Generated by Django 5.0 on 2024-02-05 06:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0007_refferal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='refferal',
            old_name='redeemed',
            new_name='is_redeemed',
        ),
    ]
