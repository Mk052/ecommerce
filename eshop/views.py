from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from eshop.forms import CustomUserCreationForm, ResetPasswordForm, AddProductForm, BuyerProfileForm, BillingAddressForm
from django.contrib.auth import authenticate, login, logout
from eshop.models import User, Product, Cart, CartItem, Billing_Address, Order, OrderItem, ProductOrder
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from eshop.utils import generate_token, send_verification_mail, generate_forgotPassword_token, send_verification_mail1

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator 
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from eshop.tasks import notify_seller_new_order
stripe.api_key = settings.STRIPE_SECRET_KEY


# ************************************************** Reset(Change) Password Views (start) ********************************************* #
class ResetPasswordView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    redirect_field_name = 'next'

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
            return redirect('login')


class SellerProfile(LoginRequiredMixin, TemplateView):
    template_name = "seller/my_profile.html"

    def get(self, request):
        if request.user.user_type != "Seller":
            return redirect('login')
        seller = request.user

        profile = User.objects.filter(id=seller.id).first()
        # print(buyer, profile)
        form = BuyerProfileForm(instance=profile)
        return render(request, self.template_name, {'form': form, 'seller': seller})

    def post(self, request):
        print("hello")
        buyer = request.user.id
        profile = User.objects.filter(id=buyer).first()
        # print(buyer, profile)
        form = BuyerProfileForm(request.POST, request.FILES, instance=profile)
        print(form.is_valid)
        print(form.errors)
        # breakpoint()
        if form.is_valid():
            form.save()
            messages.success(request, "profile updated successfully!")
            return redirect('seller_dashboard')
        else:
            print("not work")
            return render(request, self.template_name, {'form': form})


class AddProductView(TemplateView):
    template_name = "seller/add_product.html"

    def get(self, request):
        if request.user.user_type != "Seller":
            return redirect('login')
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

# ************************************************** Buyer Profile Views (start) ********************************************* #


class BuyerProfile(TemplateView, LoginRequiredMixin):
    template_name = "buyer/buyer_profile.html"

    def get(self, request):
        if request.user.user_type != "Buyer":
            return redirect('login')
        buyer = request.user

        profile = User.objects.filter(id=buyer.id).first()
        # print(buyer, profile)
        form = BuyerProfileForm(instance=profile)
        return render(request, self.template_name, {'form': form, 'buyer': buyer})
    
    def post(self, request):
        print("hello")
        buyer = request.user.id
        profile = User.objects.filter(id=buyer).first()
        # print(buyer, profile)
        form = BuyerProfileForm(request.POST, request.FILES, instance=profile)
        print(form.is_valid)
        print(form.errors)
        # breakpoint()
        if form.is_valid():
            form.save()
            messages.success(request, "profile updated successfully!")
            return redirect('home')
        else:
            print("not work")
            return render(request, self.template_name, {'form': form})


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
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'buyer/my_order.html'

    def post(self, request, *args, **kwargs):
        if request.user.user_type != "Buyer":
            return redirect('login')

        shipping_address = Billing_Address.objects.filter(user=request.user).first()
        
        cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product')
        
        if not cart_items.exists():
            return redirect('buyer_cart')  # Redirect back if no items

        total_price = sum(item.total_price() for item in cart_items)

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_price=total_price
        )

        # order_items = [
        #     OrderItem(order=order, product=item.product,  
        #               product_image=item.product.image.url if item.product.image else "/static/image/download.jpeg",
        #               price=item.total_price(), quantity=item.quantity)
        #     for item in cart_items
        # ]
        # OrderItem.objects.bulk_create(order_items)
        # print(order_items," my order")

        # cart_items.delete()  # Remove items after order is placed

        return redirect('create_payment', order.id)  # Redirect to My Orders page

# class MyOrderView(LoginRequiredMixin, TemplateView):
#     template_name = "buyer/my_order.html"
#     # login_url = "/login/"

#     def get(self, request):
#         if request.user.user_type != "Buyer":
#             return redirect('login')
#         shipping_address = Billing_Address.objects.filter(user=request.user).first()
#         # cart = Cart.objects.filter(user=request.user
#         cart_item = CartItem.objects.filter(cart__user=request.user)
        
#         total_price = sum(item.total_price() for item in cart_item)
#         order = Order.objects.create(user=request.user, shipping_address=shipping_address, total_price=total_price)
#         order.save()

#         for item in cart_item:
#             order_item = OrderItem.objects.create(order=order, product=item.product, price = item.total_price(), quantity=item.quantity)
#         order_item = OrderItem.objects.filter(order=order)
#         print("order", order)
#         print("orderitem", order_item)
#         cart_item.delete()
#         return render(request, self.template_name, {'order_items': order_item})
    
# ************************************************** Buyer Cart Views (start) ********************************************* #


class DisplayCartView(LoginRequiredMixin, TemplateView):
    template_name = "buyer/cart.html"
    login_url = '/login/'

    def get(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        cart_item = CartItem.objects.filter(cart=cart)
        total_cart_price = sum(item.total_price() for item in cart_item)
        shipping_charge = total_cart_price + 40
        return render(request, self.template_name, {'cart_item': cart_item, 'total_cart_price': total_cart_price, 'shipping_charge': shipping_charge})


class AddToCartView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'

    def post(self, request, product_id):
        product = Product.objects.filter(id=product_id).first()
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            cart = Cart.objects.create(user=request.user)
        CartItem.objects.get_or_create(cart=cart, product=product) 
        # product.stock -= 1
        # product.save()  
        return redirect('/shop')
    

class IncreaseQuantityToCartView(TemplateView):

    def post(self, request, cart_item_id):
        cart_item = CartItem.objects.filter(id=cart_item_id, cart__user=request.user).first()   
        # cart_item = CartItem.object.filter(product__stock)
        # print(product, "product")
        print(cart_item.quantity)
        if cart_item.product.stock > cart_item.quantity:
            
            # print(cart_item.product.stock, "increae product quantity")
            if cart_item.quantity >= 0:
                # cart_item.product.stock -= 1
                # cart_item.product.save()
                cart_item.quantity += 1
                print(cart_item.quantity, " in pro ")
                cart_item.save()
        else:
            messages.info(request, "you can't order the product or product out of stock")
        # print("after increace",cart_item.quantity)
        return redirect('buyer_cart')


class DecreaseQuantityToCartView(TemplateView):

    def post(self, request, cart_item_id):
        cart_item = CartItem.objects.filter(id=cart_item_id, cart__user=request.user).first()
        # print(cart_item.quantity)
        
        if cart_item.quantity > 1:
            # cart_item.product.stock += 1
            # cart_item.product.save()
            # print(cart_item.product.stock, "increae product quantity")
            cart_item.quantity -= 1
            # print(cart_item.quantity, " out pro q")

            cart_item.save()
        # print("after decresse", cart_item.quantity)
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
        price_ranges = request.GET.getlist('price_range')
        print("hi", price_ranges)
        if price_ranges:
            minm, maxm, count = 0, 0, 0
            for price_range in price_ranges:
                min_price, max_price = map(int, price_range.split('-'))
                if count == 0:
                    minm = min_price
                    count = 1
                minm = min_price if minm > min_price else minm
                # print(minm)
                maxm = max_price if maxm < max_price else maxm
                # print(maxm)
            print(minm, maxm)
            products = Product.objects.filter(price__gte=minm, price__lte=maxm)
        return render(request, self.template_name, {'products': products, "price_ranges" : price_ranges})
    
    def post(self, request):
        search_item = request.POST.get('search')
        sort_by = request.POST.get('sort_by')
        # price_ranges = request.GET.getlist('price_range')
        # print(sort_by)
        # print(search_item)
        # print("hi", price_ranges)
        # for price_range in price_ranges:
        #     min_price, max_price = map(int, price_ranges.split('-'))
        #     print(min_price, max_price)
        # if price_ranges:
        #     filters = []
        #     for price_range in price_ranges:
        #         min_price, max_price = map(int, price_range.split('-'))
        #         filters.append((min_price, max_price))
        
        if search_item:
            products = Product.objects.filter(title__icontains=search_item)
            print(products)
            return render(request, self.template_name, {'products': products, 'search_item': search_item})
        if sort_by == "high":
            products = Product.objects.all().order_by("-price")
        elif sort_by == "low":
            products = Product.objects.all().order_by("price")
        elif sort_by == "latest":
            products = Product.objects.all().order_by("-created_at")
        else:
            products = Product.objects.all().order_by('-created_at')
        return render(request, self.template_name, {'products': products})
    

class HomeView(TemplateView):
    template_name = "buyer/buyer_dashboard.html"

    def get(self, request):
        print("get")
        products = Product.objects.all()
        context = {
            'products': products,
        }
        return render(request, self.template_name, context)

# pre-view cache
# @method_decorator(cache_page(60*10), name='dispatch')
# class HomeView(TemplateView):
#     template_name = "buyer/buyer_dashboard.html"

#     def get(self, request):
#         print("get")
#         products = Product.objects.all()
#         context = {
#             'products': products,
#         }
#         return render(request, self.template_name, context)

    # Database cache
    # def get(self, request):
    #     products = cache.get('product_list')
    #     print("get product", products)

    #     if not products:
    #         products = Product.objects.all()
    #         cache.set('product_list', products, timeout=60)
    #         print("set product", products)
    #     context = {
    #         'products': products,
    #     }
    #     return render(request, self.template_name, context)

    # File based cache
    # def get(self, request):
       
    #     products = Product.objects.all()
    #     cache.set('product_list', products, timeout=60)
    #     print("set product", products)
    #     context = {
    #         'products': products,
    #     }
    #     return render(request, self.template_name, context)


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


# class CheckoutView(TemplateView):
#     template_name = "buyer/checkout.html"

#     def get(self, request):
#         cart = Cart.objects.filter(user=request.user).first()
#         print(cart)
#         cart_item = CartItem.objects.filter(cart=cart)
#         total_cart_price = sum(item.total_price() for item in cart_item)
#         shipping_charge = total_cart_price + 40
#         print(cart_item)
#         address = Billing_Address.objects.filter(user=request.user).first()
#         print(address)
#         form = BillingAddressForm(instance=address)
#         return render(request, self.template_name, {'form': form, 'cart_items': cart_item, 'total_cart_price': total_cart_price, 'shipping_charge': shipping_charge})
    
#     def post(self, request):
#         cart = Cart.objects.filter(user=request.user).first()
#         cart_item = CartItem.objects.filter(cart=cart)
#         total_cart_price = sum(item.total_price() for item in cart_item)
#         shipping_charge = total_cart_price + 40
#         address = Billing_Address.objects.filter(user=request.user).first()
#         form = BillingAddressForm(request.POST, instance=address)
#         print(form.is_valid())
#         if form.is_valid():
#             form = form.save(commit=False)
#             form.user = request.user
#             form.save()
            
#             return render(request, self.template_name, {'form': form, 'cart_items': cart_item, 'total_cart_price': total_cart_price, 'shipping_charge': shipping_charge})
#         form = BillingAddressForm(instance=address)
#         print(form.errors)
#         return render(request, self.template_name, {'form': form, 'cart_items': cart_item, 'total_cart_price': total_cart_price, 'shipping_charge': shipping_charge})


class CheckoutView(TemplateView):
    template_name = "buyer/checkout.html"

    def get(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart)
        total_cart_price = sum(item.total_price() for item in cart_items)
        shipping_charge = total_cart_price + 40

        address = Billing_Address.objects.filter(user=request.user).first()
        form = BillingAddressForm(instance=address)


        step = 1  # Default: Bag step
        if cart_items.exists():
            step = 2  # Move to Address Step
        if address:
            step = 3  # Move to Payment Step

        return render(request, self.template_name, {
            'form': form, 'cart_items': cart_items, 'total_cart_price': total_cart_price,
            'shipping_charge': shipping_charge, 'address': address, 'step': step
        })

    def post(self, request):
        address = Billing_Address.objects.filter(user=request.user).first()
        form = BillingAddressForm(request.POST, instance=address)

        if form.is_valid():
            billing_address = form.save(commit=False)
            billing_address.user = request.user  
            billing_address.save()
            return redirect('checkout')  

        return render(request, self.template_name, {'form': form})





class EditAddressView(TemplateView):
    template_name = "buyer/edit_address.html"

    def get(self, request):
        address = Billing_Address.objects.filter(user=request.user).first()
        form = BillingAddressForm(instance=address)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        address = Billing_Address.objects.filter(user=request.user).first()
        form = BillingAddressForm(request.POST, instance=address)

        if form.is_valid():
            form.save()
            return redirect("checkout")  # Redirect back to checkout after updating

        return render(request, self.template_name, {"form": form})
    
class PaymentSuccessView(LoginRequiredMixin, View):
    
    def get(self, request):
        cart_items = CartItem.objects.filter(cart__user=request.user)
        order = Order.objects.filter(user=request.user).last()
        order_items = [
            OrderItem(order=order, product=item.product,  
                      product_image=item.product.image.url if item.product.image else "/static/image/download.jpeg",
                      price=item.total_price(), quantity=item.quantity)
            for item in cart_items
        ]
        order_item = OrderItem.objects.bulk_create(order_items)
        for item in order_item:
            product_order = ProductOrder.objects.create(buyer=request.user, product=item.product, address=item.order.shipping_address, quantity=item.quantity)
            print(product_order.id)
            notify_seller_new_order.delay(product_order.id)
        cart_items.delete()
        return redirect('all_myordered_product')
    
@method_decorator(csrf_exempt, name='dispatch')
class CreatePaymentView(LoginRequiredMixin, View):

    def get(self, request, order_id):
        order = Order.objects.get(id=order_id, user=request.user)
        
        success_url = "http://127.0.0.1:8000/buyer/payment-success/"
        cancel_url = "http://127.0.0.1:8000/buyer/checkout/"

        # Create Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'Order #{}'.format(order.id)},
                        'unit_amount': int(order.total_price * 100),
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        return redirect(session.url)


# # views.py
# class PaymentSuccessView(TemplateView):
#     def get(self, request):
#         return render(request, "buyer/payment_success.html")


class AllMyOrderedProductView(LoginRequiredMixin, TemplateView):
    template_name = "buyer/my_order.html"
    login_url = '/login/'
    redirect_field_name = 'next'

    def handle_no_permission(self):
        return redirect(f"{self.login_url}?next={self.request.path}")

    def get(self, request, *args, **kwargs):
        if request.user.user_type != "Buyer":
            return redirect('login')

        # Fetch existing orders of the logged-in user
        # order = Order.objects.filter(user=request.user).first()
        order_items = OrderItem.objects.filter(order__user=request.user).order_by('-created_at')
        # print("all order_items", order_items)

        return render(request, self.template_name, {'order_items': order_items})
    

class ViewSoldItemsView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'seller/view_sold_items.html'

    def get(self, request, *args, **kwargs):
        
        product_order = ProductOrder.objects.filter(product__user=request.user)
        return render(request, self.template_name, {'product_items': product_order})