from django.db import models
from django.forms import ValidationError
from UserHome.models import UserProfile
from django.utils import timezone
import pytz

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='category_image/')
    description = models.CharField(max_length=255)
    is_listed = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='brand_image/')
    is_listed = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name
    
def validate_price(value):
    if value < 0:
        raise ValidationError('The value must be a whole number')
    
class Product(models.Model):
    thumbnail = models.ImageField(upload_to='product_image/')
    name = models.CharField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    description = models.CharField()
    is_listed = models.BooleanField(default=True)
    price = models.IntegerField(validators=[validate_price])
    outer_material = models.CharField()

    class Meta:
        ordering = ['-id']
        
    def __str__(self):
        return self.name
    
    @property
    def display_price(self):
        offer = Offer.objects.filter(product=self).first()
        if offer and offer.discounted_price is not None:
            return round((100 - offer.percent) * offer.product.price / 100)
        else:
            return self.price
        
    def formatted_price(self):
        return f"₹{self.price}"
    
def validate_quantity(value):
    if value < 0:
        raise ValidationError('The value must be a whole number')
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=200)
    quantity = models.IntegerField(validators=[validate_quantity])

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.size
    
class Offer(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    percent = models.IntegerField()
    discounted_price = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.percent is not None:
            self.discounted_price = round((100 - self.percent) * self.product.price / 100)
        else:
            self.discounted_price = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.percent}%"
    
class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    images = models.ImageField(upload_to='product_images/')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.images
    
def validate_percent(value):
    if value > 100:
        raise ValidationError('Discount percent must be less than or equal to 100.')
    
class Coupon(models.Model):
    code = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    min_price = models.IntegerField()
    max_price = models.IntegerField()
    discount_percent  = models.IntegerField(validators=[validate_percent])
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.min_price < 0 or self.max_price < 0:
            raise ValidationError('Prices must be non-negative')

        if self.min_price >= self.max_price:
            raise ValidationError('Minimum price must be less than maximum price')
        

class UserCoupon(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    redeemed_at = models.TimeField(null=True)

    class Meta:
        ordering = ['-id']

    def redeem_coupon(self):
        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_time = timezone.now().astimezone(ist_timezone)
        self.redeemed_at = current_time
        self.save()



    