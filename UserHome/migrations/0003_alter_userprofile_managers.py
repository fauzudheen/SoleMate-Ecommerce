# Generated by Django 5.0 on 2024-01-10 13:58

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserHome', '0002_alter_userprofile_managers_alter_userprofile_email'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='userprofile',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
