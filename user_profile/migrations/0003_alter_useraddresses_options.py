# Generated by Django 5.0 on 2024-01-12 14:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_useraddresses_is_shipping'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='useraddresses',
            options={'ordering': ['-id']},
        ),
    ]
