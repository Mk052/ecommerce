from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from eshop.manager import CustomUserManager
from django.utils.timezone import now


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, TimestampedModel):  # extend AbstractUser to retain the default features while adding your own
    USER_TYPE = [
        ('Buyer', 'Buyer'),
        ('Seller', 'Seller'),
    ]
    username = None
    full_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=100, choices=USER_TYPE, default="Buyer")
    is_email_verified = models.BooleanField(default=False)
    email_verified_sent_at = models.DateTimeField(blank=True, null=True)
    email_verified_token = models.CharField(max_length=100, blank=True, null=True)
    reset_password = models.BooleanField(default=False)
    forgot_password_token = models.CharField(max_length=100, blank=True, null=True)
    forgot_password_sent_at = models.DateTimeField(blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Custom manager
    objects = (CustomUserManager())  # CustomUserManager is a custom class (defined separately) that provides methods for creating both regular users and superusers.
    USERNAME_FIELD = "email"  # Use email as the username field

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Category(TimestampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Product(TimestampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product")
    price = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="product")

   
    def __str__(self):
        return self.name