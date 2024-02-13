from django import forms
from AdminHome.models import Banner

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date'}),
            'end_date': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date'}),
        }
