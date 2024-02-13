# Generated by Django 5.0 on 2024-01-18 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserHome', '0004_otpmodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otpmodel',
            name='user',
        ),
        migrations.AddField(
            model_name='otpmodel',
            name='email',
            field=models.EmailField(default='Default', max_length=254, unique=True, verbose_name='email address'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='otpmodel',
            name='user_data',
            field=models.JSONField(default={'key': 'value'}),
            preserve_default=False,
        ),
    ]