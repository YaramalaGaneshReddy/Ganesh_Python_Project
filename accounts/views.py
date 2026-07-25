from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegisterForm
from cart.models import Cart, CartItem
from products.models import Product

def merge_session_cart(request, user):
    session_cart = request.session.get('session_cart', {})
    if session_cart:
        cart, _ = Cart.objects.get_or_create(user=user)
        for prod_id_str, qty in session_cart.items():
            try:
                prod = Product.objects.get(id=int(prod_id_str))
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=prod)
                if created:
                    cart_item.quantity = qty
                else:
                    cart_item.quantity += qty
                cart_item.save()
            except Exception:
                pass
        request.session['session_cart'] = {}

def register_user(request):
    if request.user.is_authenticated:
        return redirect('products:home')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username}! You can now login.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_user(request):
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                merge_session_cart(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('products:home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_user(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('products:home')
