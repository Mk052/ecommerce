
from django.urls import path
from eshop.views import (
    HomeView, LoginView, SignupView, LogoutView,
    ProductView, SellerDashboard, SellerProfile, CheckmailView, EmailVerification,
    ForgotPasswordDoneView, ForgotPasswordView, ResetPasswordView )

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('login/', LoginView.as_view(), name="login"),
    path('signup/', SignupView.as_view(), name="signup"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('product/', ProductView.as_view(), name='product'),
    path('seller/', SellerDashboard.as_view(), name='seller_dashboard'),
    path('seller/profile/', SellerProfile.as_view(), name='seller_profile'),
    path('seller/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('checkmail/', CheckmailView.as_view(), name='checkmail'),
    path('verify-email/', EmailVerification.as_view(), name='verify_email'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password_form'),
    path('forgot-password-done/', ForgotPasswordDoneView.as_view(), name='forgot_password_done'),
]
