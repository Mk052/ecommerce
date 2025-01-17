from django.contrib import admin
from eshop.models import User, Product, Category, Cart, CartItem

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
