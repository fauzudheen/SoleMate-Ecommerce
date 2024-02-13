from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError
import re

def validate_phone(value):
    if not value.isdigit():
        raise ValidationError('Phone number should contain only digits.')
    if len(value) != 10:
        raise ValidationError('Phone number should be exactly 10 digits long.')
    
    pattern = r"^(?:\+91[\-\s]?)?[789]\d{9}$"

    if not re.match(pattern, value):
        raise ValidationError('Please enter a valid Indian phone number.')
    
def validate_name(value):
    if not value.isalpha():
        raise ValidationError('Name should contain only alphabetic characters.')
    if value.strip() == '':
        raise ValidationError('Name cannot be just spaces.')

class UserProfile(AbstractUser):
    first_name = models.CharField(("first name"), max_length=150, validators=[validate_name])
    last_name = models.CharField(("last name"), max_length=150, validators=[validate_name])
    email = models.EmailField(("email address"), unique = True)
    phone_number = models.CharField(max_length=10, unique = True, validators=[validate_phone])
    referral_code = models.CharField(max_length=10, null=True, blank=True)
    
    def __str__(self):
        return self.username

class OTPModel(models.Model):
    email = models.EmailField(("email address"), unique=True)
    otp = models.CharField(max_length=4)
    user_data = JSONField()



