from django.db import models
from UserHome.models import UserProfile
from admin_product_management.models import Product, ProductVariant
# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    total_amount = models.IntegerField(default=0)

    class Meta:
        ordering = ['-id']   

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sub_total = models.IntegerField(default=0)

    class Meta:
        ordering = ['-id']

    def save_dup(self, *args, **kwargs):
        self.sub_total = round(self.product.display_price * self.quantity)
        super().save(*args, **kwargs)

class WishlistItem(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']
