from django import forms
from .models import Cart, CartItem
from admin_product_management.models import ProductVariant

class AddToCartForm(forms.ModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control rounded'})
    )
    product_variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.all(),
        to_field_name='size',
        widget=forms.Select(attrs={'class': 'form-select form-select'}),
    )

    class Meta:
        model = CartItem
        fields = [ 'quantity', 'product_variant',]
        widgets = {
            'product_variant': forms.Select(attrs={'class': 'form-control rounded'}),
        }
    def __init__(self, *args, **kwargs):
        product_id = kwargs.pop('product_id', None)
        super().__init__(*args, **kwargs)
        
        if product_id:
            self.fields['product_variant'].queryset = ProductVariant.objects.filter(
                product_id=product_id
            ).order_by('size')
