from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from eshop.forms import CustomUserCreationForm, ResetPasswordForm
from django.contrib.auth import authenticate, login, logout
from eshop.models import User, Product
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from eshop.utils import generate_token, send_verification_mail, generate_forgotPassword_token, send_verification_mail1


class ResetPasswordView(TemplateView):
    template_name = "reset_password.html"
    
    def get(self, request):
        form = ResetPasswordForm(request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = ResetPasswordForm(request.user, request.POST)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Important to keep the user logged in
            messages.success(request, "password changed successfully!")
            return redirect('seller_dashboard')
        else:
            return render(request, self.template_name, {'form': form})

    
class SellerDashboard(TemplateView):
    # template_name = "eshop/seller.html"
    template_name = "seller/my_products.html"

    def get(self, request):
        user = request.user
        # if request.user.is_authenticated and request.user.user_type == "Seller":
        products = Product.objects.filter(user=user).order_by("-created_at")
        return render(request, self.template_name, {'products': products})


class SellerProfile(TemplateView):
    template_name = "seller/my_profile.html"


class BuyerProfile(TemplateView):
    template_name = "buyer/buyer_profile.html"


class MyOrderView(TemplateView):
    template_name = "buyer/my_order.html"


class ShopView(TemplateView):
    template_name = "eshop/shop.html"

    def get(self, request):
        products = Product.objects.all().order_by('-created_at')
        return render(request, self.template_name, {'products': products})


class HomeView(TemplateView):
    template_name = "buyer/buyer_dashboard.html"

    def get(self, request):
        products = Product.objects.all()
        print("hii")
        print(products)
        return render(request, self.template_name, {'products': products})


class AddProductView(TemplateView):
    template_name = "seller/add_product.html"


class LoginView(TemplateView):
    template_name = "eshop/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == "Seller":
                return redirect('seller_dashboard')
            elif user.user_type == "Buyer":
                return redirect('home')
        else:
            messages.error(request, "email or password invalid")
            return render(request, self.template_name)


class SignupView(TemplateView):
    template_name = "eshop/signup.html"

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        # print(form.is_valid)
        # print(form.errors)
        if form.is_valid():
            user = form.save()
            user.email_verified_token = generate_token()
            user.email_verified_sent_at = timezone.now()
            user.is_email_verified = False
            send_verification_mail(user)
            user.save()
            messages.info(
                request,
                "A verification email has been sent to your email address. Please check your inbox",
            )
            return redirect('checkmail')
        else:
            return render(request, self.template_name, {'form': form})


class EmailVerification(TemplateView):
    template_name = "seller/verify_mail.html"

    def get(self, request):
        token = request.GET.get('token')
        user = User.objects.filter(email_verified_token=token).first()

        if user and not user.is_email_verified:
            if user.email_verified_sent_at + timezone.timedelta(minutes=2) > timezone.now():
                user.is_email_verified = True
                user.save()
                messages.success(request, "email verified successfully!")
                return redirect('login')
            else:
                messages.info(request, "email verification link is invalid")
                return redirect('signup')
        else:
            messages.info(request, "email already verified")
            return redirect('signup')


class ForgotPasswordView(TemplateView):
    template_name = "eshop/forgot_password_form.html"

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            user.forgot_password_token = generate_forgotPassword_token()
            user.forgot_password_sent_at = timezone.now()
            user.reset_password = False
            user.save()
            send_verification_mail1(user)
            messages.success(request, "Please check your email")
        else:
            messages.error(request, "Email does not exit")
        return render(request, self.template_name)


class ForgotPasswordDoneView(TemplateView):
    template_name = "eshop/forgot_password_done.html"

    def get(self, request):
        token = request.GET.get('token')
        user = User.objects.filter(forgot_password_token=token).first()

        if user and not user.reset_password:
            if user.forgot_password_sent_at + timezone.timedelta(minutes=2) > timezone.now():
                return render(request, self.template_name, {'token': token})
            else:
                messages.info(request, "invalid link")
                return redirect('forgot_password_form')
        else:
            messages.error(request, "user does not exit")
            return redirect('forgot_password_form')
        
    def post(self, request):
        token = request.POST.get('token')
        password = request.POST.get('password1')
        user = User.objects.filter(forgot_password_token=token).first()

        if user and not user.reset_password:
            if user.forgot_password_sent_at + timezone.timedelta(minutes=2) > timezone.now():
                user.reset_password = True
                user.set_password(password)
                user.save()
                messages.success(request, "successfully changed password!")
                return redirect('login')
            else:
                messages.info(request, "invalid link")
                return redirect('forgot_password_form')
        else:
            messages.error(request, "user does not exit")
            return redirect('forgot_password_form')


class CheckmailView(TemplateView):
    template_name = "eshop/checkmail.html"

    # def get(self, request, *args, **kwargs):
    #     # if the user is logged in redirecting user to appropriate view via login
    #     if request.user.is_authenticated:
    #         return redirect("login")

    #     return render(request, self.template_name)

class LogoutView(TemplateView):
    template_name = "eshop/hello.html"

    def get(self, request):
        logout(request)
        return redirect('login')
    

class ProductView(TemplateView):
    template_name = "eshop/index.html"

    def get(self, request):
        products = Product.objects.all()
        print("hii")
        print(products)
        return render(request, self.template_name, {'products': products})
