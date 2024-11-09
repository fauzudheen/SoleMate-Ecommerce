from django.db import models
from UserHome.models import UserProfile
from user_product.models import Product, ProductVariant
from AdminHome.models import DailySales
from datetime import datetime
from user_profile.models import Wallet


class OrderAddress(models.Model):
    full_name = models.CharField(max_length=200)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.IntegerField()

    class Meta:
        ordering = ['-id']

class OrderStatus(models.Model):
    status = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.status
    
    class Meta:
        ordering = ['-id']

class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    address = models.ForeignKey(OrderAddress, on_delete=models.CASCADE)
    total_amount = models.IntegerField()
    order_date = models.DateField()
    
    class Meta:
        ordering = ['-id']   

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variant = models.IntegerField()
    quantity = models.IntegerField()
    sub_total = models.IntegerField()
    payment_method = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=100, default="Pending")
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    tracking_number = models.IntegerField()
    delivery_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def qty_update_on_cancel(self):
        if self.order_status.status == "Cancelled":
            product_variant = ProductVariant.objects.get(product=self.product, size=self.product_variant)
            product_variant.quantity += self.quantity
            product_variant.save()

    def refund_wallet(self):
        if self.payment_status == "Complete":
            wallet = Wallet.objects.get(user=self.order.user)
            wallet.balance += self.sub_total
            wallet.save()
            wallet.update_transaction(self.sub_total, type="Refund")

    def add_to_sales_on_deliver(self):
        if self.order_status.status == "Delivered":
            DailySales.objects.create(
                date = datetime.now().date(),
                product = self.product,
                quantity  = self.quantity,
                amount = self.sub_total
            )

    def update_delivery_date(self):
        print("update_delivery_date called")
        if self.order_status.status == "Delivered":
            self.delivery_date = datetime.now().date()
            self.save()
    
class Payment(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE)
    amount=models.IntegerField()
    payment_method=models.CharField(max_length=50)
    razorpay_payment_id=models.CharField(max_length=50)

    def __str__(self):
        return f"Payment ID: {self.razorpay_payment_id}"
    






