from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem

@login_required(login_url='accounts:login')
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@login_required(login_url='accounts:login')
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    if product.stock <= 0:
        messages.error(request, f"Sorry, {product.name} is currently out of stock.")
        return redirect('products:product_detail', pk=product.id)
        
    if product.stock < quantity:
        messages.error(request, f"Sorry, only {product.stock} items left in stock.")
        return redirect('products:product_detail', pk=product.id)
        
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if item_created:
        cart_item.quantity = quantity
    else:
        total_qty = cart_item.quantity + quantity
        if product.stock < total_qty:
            messages.error(request, f"Cannot add more. Only {product.stock} items available in stock, and you already have {cart_item.quantity} in your cart.")
            return redirect('cart:cart_detail')
        cart_item.quantity = total_qty
        
    cart_item.save()
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect('cart:cart_detail')

@login_required(login_url='accounts:login')
def cart_update(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        
        try:
            new_quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            new_quantity = 1

        if new_quantity <= 0:
            cart_item.delete()
            messages.success(request, f"Removed {product.name} from your cart.")
        elif new_quantity > product.stock:
            messages.error(request, f"Cannot set quantity to {new_quantity}. Only {product.stock} items available in stock.")
        else:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"Updated quantity for {product.name} to {new_quantity}.")

    return redirect('cart:cart_detail')

@login_required(login_url='accounts:login')
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    
    action = request.POST.get('action', 'remove')
    if action == 'decrement' and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, f"Updated quantity of {product.name}.")
    else:
        cart_item.delete()
        messages.success(request, f"Removed {product.name} from your cart.")
        
    return redirect('cart:cart_detail')

@login_required(login_url='accounts:login')
def cart_clear(request):
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
            messages.success(request, "Your shopping cart has been cleared.")
    return redirect('cart:cart_detail')

