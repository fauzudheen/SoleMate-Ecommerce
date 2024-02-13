from django import forms
from .models import UserAddresses
from UserHome.models import UserProfile
from user_order.models import OrderItem

class AddressForm(forms.ModelForm):
    class Meta:
        model = UserAddresses
        fields = "__all__"
        exclude = ['user', 'is_shipping']

        widgets = {
        'full_name': forms.TextInput(attrs={'class': 'form-control rounded'}),
        'street_address': forms.TextInput(attrs={'class': 'form-control rounded'}),
        'city': forms.TextInput(attrs={'class': 'form-control rounded'}),
        'district': forms.TextInput(attrs={'class': 'form-control rounded'}),
        'state': forms.TextInput(attrs={'class': 'form-control rounded'}),
        'pincode': forms.TextInput(attrs={'class': 'form-control rounded'}),

    }

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control rounded'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control rounded'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control rounded'}),
        }

        required = ['first_name']    

class TrackOrderForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ('tracking_number',)
        widgets = {
            'tracking_number': forms.TextInput(attrs={'class': 'form-control rounded'}),
        }