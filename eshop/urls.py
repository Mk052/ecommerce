
from django.urls import path
from eshop.views import (
    HomeView, LoginView, SignupView, LogoutView,
    ProductView, SellerDashboard, SellerProfile, CheckmailView, EmailVerification,
    ForgotPasswordDoneView, ForgotPasswordView, ResetPasswordView, AddProductView,
    ShopView, BuyerProfile, MyOrderView, ProductDetailView, AddToCartView,
    DeleteCartView, BuyerCartView, IncreaseQuantityToCartView,
   )

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('login/', LoginView.as_view(), name="login"),
    path('signup/', SignupView.as_view(), name="signup"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('product/', ProductView.as_view(), name='product'),
    path('seller/', SellerDashboard.as_view(), name='seller_dashboard'),
    path('seller/profile/', SellerProfile.as_view(), name='seller_profile'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('checkmail/', CheckmailView.as_view(), name='checkmail'),
    path('verify-email/', EmailVerification.as_view(), name='verify_email'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password_form'),
    path('forgot-password-done/', ForgotPasswordDoneView.as_view(), name='forgot_password_done'),
    path('seller/add_product/', AddProductView.as_view(), name='add_product'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('my-order/', MyOrderView.as_view(), name='my_order'),
    path('buyer/profile/', BuyerProfile.as_view(), name='buyer_profile'),
    path('add_product/', AddProductView.as_view(), name='add_product'),
    path('product_detail/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('buyer/add_cart/<int:product_id>/', AddToCartView.as_view(), name='add_cart'),
    path('buyer/delete_cart/<int:cart_item_id>/', DeleteCartView.as_view(), name='delete_cart'),
    path('buyer/cart/', BuyerCartView.as_view(), name='buyer_cart'),
    path('buyer/cart/<int:cart_item_id>/', IncreaseQuantityToCartView.as_view(), name='buyer_cartitem_increase'),
#     path('buyer/cart/<int:cart_item_id>/', DecreaseQuantityToCartView.as_view(), name='buyer_cartitem_decrease),

]
