
from django.urls import path
from eshop.views import (HomeView, LoginView, SignupView, LogoutView, ProductView)

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('login', LoginView.as_view(), name="login"),
    path('signup', SignupView.as_view(), name="signup"),
    path('logout', LogoutView.as_view(), name='logout'),
    path('product', ProductView.as_view(), name='product'),
]