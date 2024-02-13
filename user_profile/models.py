from django.db import models
from UserHome.models import UserProfile
from django.core.exceptions import ValidationError
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver


def validate_pin(value):
    if not value.isdigit():
        raise ValidationError('Pincode must be digits')
    if len(value) != 6:
        raise ValidationError('Pincode must have atleast 6 digits')


class UserAddresses(models.Model):
    full_name = models.CharField(max_length=200)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6, validators=[validate_pin])
    is_shipping = models.BooleanField(default=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='addresses')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.full_name}, {self.street_address}, {self.city}, {self.district}, {self.state} - {self.pincode}"
    
class Wallet(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    def update_transaction(self, amount, type):
        Transaction.objects.create(
            wallet=self,
            type=type,
            amount=amount
        )
    
    

@receiver(post_save, sender=UserProfile)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

def get_current_date():
    return datetime.now().date()

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    amount = models.IntegerField()
    date = models.DateField(default=get_current_date)

class Referral(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=8)
    is_redeemed = models.BooleanField(default=False)