# user_home/signals.py
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender='UserHome.UserProfile')
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet = apps.get_model('user_profile', 'Wallet')
        Wallet.objects.create(user=instance)
