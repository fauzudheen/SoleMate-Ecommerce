from django.db import models

# Create your models here.
class DeliveryCharge(models.Model):
    city = models.CharField(max_length=50)
    amount = models.IntegerField()