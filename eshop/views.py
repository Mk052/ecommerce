from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from eshop.forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from eshop.models import User, Product


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
        print(form.is_valid)
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, self.template_name, {'form': form})
    

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
