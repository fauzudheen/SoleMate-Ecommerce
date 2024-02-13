from django import forms
from user_order.models import OrderItem
from .models import DeliveryCharge

class OrderStatusChangeForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ('order_status',)

class DeliveryChargeForm(forms.ModelForm):
    class Meta:
        model = DeliveryCharge
        fields = '__all__'