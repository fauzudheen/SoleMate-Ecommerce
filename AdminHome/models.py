from django.db import models

from admin_product_management.models import Product

class Admin(models.Model):
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.CharField(max_length=100)  
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Banner(models.Model):
    image = models.ImageField(upload_to='banner_image/')
    heading = models.CharField(max_length=200)
    description = models.CharField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name
    
class DailySales(models.Model):
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    amount = models.IntegerField()

    def __str__(self):
        return f"Daily Sales - {self.date}"
