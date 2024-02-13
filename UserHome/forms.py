from django import forms
from UserHome.models import UserProfile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext as _
from django.contrib.auth import password_validation

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = UserProfile
        fields = ('first_name', 'last_name', 'username', 'email', 'phone_number', 'password1', 'password2')


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class EmailForm(forms.Form):
    email = forms.EmailField()

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    confirm_password = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("confirm_password", self.error_messages["password_mismatch"])

        if new_password:
            try:
                password_validation.validate_password(new_password)
            except forms.ValidationError as error:
                self.add_error("new_password", error)

        return cleaned_data

class OtpForm(forms.Form):
    otp = forms.CharField()