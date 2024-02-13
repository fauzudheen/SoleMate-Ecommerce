from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount']
    list_filter = ['user']
    search_fields = ['user__username']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'product_variant', 'quantity', 'sub_total']
    list_filter = ['cart']
    search_fields = ['cart__user__username', 'product__name']
