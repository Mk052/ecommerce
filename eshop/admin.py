from django.contrib import admin
from eshop.models import User, Product, Category, Cart, CartItem, Billing_Address, Order, OrderItem

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Billing_Address)
admin.site.register(Order)
admin.site.register(OrderItem)