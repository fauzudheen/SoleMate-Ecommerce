from django import forms
from .models import OrderStatus

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = OrderStatus
        fields = "__all__"


class RazorpayPaymentForm(forms.Form):
    razorpay_order_id = forms.CharField(widget=forms.HiddenInput)
