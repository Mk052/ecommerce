from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from .manager import CustomUserManager
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
    GENDER = [
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Other', 'Other'),
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
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER, null=True, blank=True)

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
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product")
    image = models.ImageField(upload_to='images/')
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="product")

    def __str__(self):
        return self.title


class Cart(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return self.user.email

    
class CartItem(TimestampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='item')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.cart.user.email}, {self.product.title}"
    
    def total_price(self):
        return self.product.price * self.quantity
    
class Billing_Address(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to user
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    address_line = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=6)
    is_shipping = models.BooleanField(default=False)  # Whether this is a shipping address

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}, {self.country}"

# Order Model
class Order(TimestampedModel):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Billing_Address, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"Order {self.id} - {self.user} - {self.status}"

    # def calculate_total(self):
    #     total = sum(item.price * item.quantity for item in self.items.all())
    #     self.total_price = total
    #     self.save()
        
    def shipping_charges(self):
        return self.total_price + 40


class OrderItem(TimestampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.CharField(max_length=255)
    product_image = models.URLField()  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product} ({self.quantity})"


class ProductOrder(TimestampedModel):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
    ]
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    address = models.CharField(max_length=225)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Completed")