from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from eshop.models import User
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "is_email_verified",
            "reset_password",
            "user_type",
        ]


class ResetPasswordForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Old Password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            return ValidationError("password must be atleast 8 characters long")
        if not any(i.isalpha() for i in password1):
            return ValidationError("password must contain a alphabat characters")
        if not any(i.isupper() for i in password1):
            return ValidationError("password must contain a upperclass characters")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            return ValidationError("password must contain a special characters")
        return password1
    