from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from eshop.models import User, Product, Billing_Address
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        }),
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'required': True
        }),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "user_type",
            "address",
            "image",
            "phone_number",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={
                'type': 'text',
                'label': 'First Name',
                'class': 'form-control',
                'placeholder': 'First Name',
                'required': True
            }),
            "last_name": forms.TextInput(attrs={
                'type': 'text',
                'label': 'Last Name',
                'class': 'form-control',
                'placeholder': 'Last Name',
                'required': True
            }),
            "email": forms.TextInput(attrs={
                'type': 'text',
                'label': 'Email',
                'class': 'form-control',
                'placeholder': 'Email',
                'required': True
            }),
            # "password1": forms.PasswordInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Password',
            #     'required': True,
            #     'label': 'Password'
            # }),
            # "password2": forms.PasswordInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Confirm Password',
            #     'required': True,
            #     'label': 'Confirm Password'
            # }),
            "user_type": forms.Select(attrs={
                'class': 'form-select',
                'label': 'User Type',
                'placeholder': 'Select user type',
                'required': True
            }),
            "address": forms.Textarea(attrs={
                'type': 'text',
                'label': 'Address',
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Address',
            }),
            "image": forms.FileInput(attrs={
                'label': 'Profile Picture',
                'type': 'file',
                'id': 'image',
                'class': 'form-control',
                'accept': 'image/*',
             }),
            "phone_number": forms.NumberInput(attrs={
                'label': 'Phone Number',
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'step': '0.01',
            }),
        }


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "image",
            "price",
            "stock",
            "category",
         ]
        widgets = {
            "title": forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'id': 'productName',
                'placeholder': 'Product Name',
                'required': True
            }),
            "description": forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'productDescription',
                'rows': 3,
                'placeholder': 'Description',
                'required': True
            }),
            "price": forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'productPrice',
                'placeholder': 'Price',
                'step': '0.01',
                'required': True
            }),
            "stock": forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'productQuantity',
                'placeholder': 'Quantity in Stock',
                'required': True
            }),
            "category": forms.Select(attrs={
                'class': 'form-select',
                'id': 'productCategory',
                'placeholder': 'Select a category',
                'required': True
            }),
            "image": forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'productImage',
                'accept': 'image/*',
                'required': True
            })
        }


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
    

class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            # "email",
            "address",    
            "image",
            "phone_number",
            "bio",
            "gender",
            "date_of_birth"
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'First Name',
            }),
            "last_name": forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Last Name',
            }),
            # "email": forms.TextInput(attrs={
            #     'type': 'text',
            #     'class': 'form-control',
            #     'placeholder': 'Email',
            #     'disabled': True
            # }),
            "address": forms.Textarea(attrs={
                'type': 'text',
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Address',
            }),
            "image": forms.FileInput(attrs={
                'type': 'file',
                'id': 'image',
                'class': 'form-control',
                'accept': 'image/*',
             }),
            "phone_number": forms.NumberInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'step': '0.01',
            }),
            "gender": forms.Select(attrs={
                'type': 'form-select',
                'class': 'form-control',
                'placeholder': 'gender',
            }),
            "bio": forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Bio',
            }),
            "date_of_birth": forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Date of Birth',
            })
            
        }


class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = Billing_Address
        fields = [
            "first_name", "last_name", "phone_number",
            "address_line", "country", "city",
            "state", "pin_code"
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "John"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Doe"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": " +91"}),
            "address_line": forms.TextInput(attrs={"class": "form-control", "placeholder": "123 Street"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "India"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "New York"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "New York"}),
            "pin_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "123"}),
        }
