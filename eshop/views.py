from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from eshop.forms import CustomUserCreationForm, ResetPasswordForm, AddProductForm
from django.contrib.auth import authenticate, login, logout
from eshop.models import User, Product, Cart, CartItem
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from eshop.utils import generate_token, send_verification_mail, generate_forgotPassword_token, send_verification_mail1


# ************************************************** Reset(Change) Password Views (start) ********************************************* #
class ResetPasswordView(TemplateView, LoginRequiredMixin): 
    def get_template_names(self, request):
        if request.user.user_type == "Seller":
            template_name = "seller/reset_password.html"
            return template_name
        else:
            template_name = "buyer/reset_password.html"
            return template_name
    
    def get(self, request):
        form = ResetPasswordForm(request.user)
        template_name = self.get_template_names(request)
        return render(request, template_name, {'form': form})
    
    def post(self, request):
        form = ResetPasswordForm(request.user, request.POST)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Important to keep the user logged in
            messages.success(request, "password changed successfully!")
            return redirect('seller_dashboard')
        else:
            template_name = self.get_template_names(request)
            return render(request, template_name, {'form': form})


# ************************************************** Reset(Change) Password Views (End) ********************************************* #

# ************************************************** Seller Dashboard Views (start) ********************************************* #

class SellerDashboard(TemplateView):
    template_name = "seller/my_products.html"

    def get(self, request):
        user = request.user
        if request.user.is_authenticated and request.user.user_type == "Seller":
            products = Product.objects.filter(user=user).order_by("-created_at")
            return render(request, self.template_name, {'products': products})
        else:
            return redirect('home')


class SellerProfile(LoginRequiredMixin, TemplateView):
    template_name = "seller/my_profile.html"


class AddProductView(TemplateView):
    template_name = "seller/add_product.html"

    def get(self, request):
        form = AddProductForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AddProductForm(request.POST, request.FILES)
        print(form.is_valid)
        print(form.errors)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product = form.save()
            messages.success(request, "successfully added product")
            return redirect('seller_dashboard')
        else:
            form = AddProductForm()
            return render(request, self.template_name, {'form': form})


# ************************************************** Seller Dashboard Views (End) ********************************************* #

# ************************************************** Seller Profile Views (start) ********************************************* #


class BuyerProfile(TemplateView, LoginRequiredMixin):
    template_name = "buyer/buyer_profile.html"


class ProductDetailView(TemplateView):
    template_name = "buyer/view_product.html"

    def get(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        product = Product.objects.filter(id=product_id).first()
        # cart_item = CartItem.objects.filter(cart__user=request.user, product=product).first()
        context = {
            'product': product
        }
        return render(request, self.template_name, context)


class MyOrderView(LoginRequiredMixin, TemplateView):
    template_name = "buyer/my_order.html"
    login_url = "/login/"
    
# ************************************************** Buyer Cart Views (start) ********************************************* #


class DisplayCartView(LoginRequiredMixin, TemplateView):
    template_name = "buyer/cart.html"
    login_url = '/login/'

    def get(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        cart_item = CartItem.objects.filter(cart=cart)
        return render(request, self.template_name, {'cart_item': cart_item})


class AddToCartView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'

    def post(self, request, product_id):
        product = Product.objects.filter(id=product_id).first()
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            cart = Cart.objects.create(user=request.user)
        CartItem.objects.get_or_create(cart=cart, product=product)
        return redirect('/shop')
    

class IncreaseQuantityToCartView(TemplateView):

    def post(self, request, cart_item_id):
        cart_item = CartItem.objects.filter(id=cart_item_id, cart__user=request.user).first()
        print(cart_item.quantity)
        if cart_item.product.stock > cart_item.quantity:
            if cart_item.quantity >= 0:
                cart_item.quantity += 1
                cart_item.save()
        else:
            messages.info(request, "you can't order the product or stock is out of range")
        print("after increace",cart_item.quantity)
        return redirect('buyer_cart')


class DecreaseQuantityToCartView(TemplateView):

    def post(self, request, cart_item_id):
        cart_item = CartItem.objects.filter(id=cart_item_id, cart__user=request.user).first()
        print(cart_item.quantity)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        print("after decresse", cart_item.quantity)
        return redirect('buyer_cart')            


class DeleteCartView(TemplateView):
    def post(self, request, **kwargs):
        cart_item_id = self.kwargs.get("cart_item_id")
        print(cart_item_id)
        print("delete")
        # carts = Cart.objects.filter(user=request.user).first()
        cart_item = CartItem.objects.filter(id=cart_item_id, cart__user=request.user).first()
        cart_item.delete()
        print("done")
        return redirect('buyer_cart')


# ************************************************** Buyer Cart Views (end) ********************************************* #

class ShopView(TemplateView):
    template_name = "buyer/shop.html"

    def get(self, request):
        products = Product.objects.all().order_by('-created_at')
        return render(request, self.template_name, {'products': products})


class HomeView(TemplateView):
    template_name = "buyer/buyer_dashboard.html"

    def get(self, request):
        products = Product.objects.all()
        context = {
            'products': products,
        }
        return render(request, self.template_name, context)


# ************************************************** Login, Signup, Logout  Views (start) ********************************************* #


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
        form = CustomUserCreationForm(request.POST, request.FILES)
        print(form.is_valid)
        print(form.errors)
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
        

class LogoutView(TemplateView, LoginRequiredMixin):
    template_name = "eshop/hello.html"

    def get(self, request):
        logout(request)
        return redirect('login')


# ************************************************** Login, Signup, Logout  Views (end) ********************************************* #

# ************************************************** Email Verification  Views (start) ********************************************* #


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
            return redirect('login')


class CheckmailView(TemplateView):
    template_name = "eshop/checkmail.html"


# ************************************************** Email Verification  Views (end) ********************************************* #

# ************************************************** Forgot Password  Views (start) ********************************************* #


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

# ************************************************** Forgot Password  Views (end) ********************************************* #

    # def get(self, request, *args, **kwargs):
    #     # if the user is logged in redirecting user to appropriate view via login
    #     if request.user.is_authenticated:
    #         return redirect("login")

    #     return render(request, self.template_name)
    

class ProductView(TemplateView):
    template_name = "eshop/index.html"

    def get(self, request):
        products = Product.objects.all()
        print("hii")
        print(products)
        return render(request, self.template_name, {'products': products})
