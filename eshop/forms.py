from django import forms
from django.contrib.auth.forms import UserCreationForm

from eshop.models import User


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