from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from eshop.forms import CustomUserCreationForm, ResetPasswordForm
from django.contrib.auth import authenticate, login, logout
from eshop.models import User, Product
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from eshop.utils import generate_token, send_verification_mail


class ResetPasswordView(TemplateView):
    template_name = "seller/reset_password.html"
    
    def get(self, request):
        form = ResetPasswordForm(request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = ResetPasswordForm(request.user, request.POST)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Important to keep the user logged in
            messages.success(request, "password changed successfully!")
            return redirect('selles_dashboard')
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


class HomeView(TemplateView):
    template_name = "eshop/index.html"

    def get(self, request):
        products = Product.objects.all()
        print("hii")
        print(products)
        return render(request, self.template_name, {'products': products})


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
