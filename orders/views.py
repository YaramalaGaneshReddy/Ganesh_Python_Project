from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from cart.models import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm

@login_required(login_url='accounts:login')
def order_create(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('products:home')

    if cart.items.count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('products:home')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Check stock for all items first
                    for item in cart.items.all():
                        if item.product.stock < item.quantity:
                            raise ValueError(f"Insufficient stock for product '{item.product.name}'. Only {item.product.stock} left.")

                    # Save Order
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_price = cart.get_total_price()
                    order.save()

                    # Create Order Items and update stock
                    for item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            price=item.product.price,
                            quantity=item.quantity
                        )
                        # Deduct stock
                        item.product.stock -= item.quantity
                        item.product.save()

                    # Clear the cart items
                    cart.items.all().delete()
                    
                messages.success(request, "Your order has been placed successfully!")
                return redirect('orders:order_detail', order_id=order.id)
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('cart:cart_detail')
            except Exception as e:
                messages.error(request, "There was an error processing your order. Please try again.")
                return redirect('cart:cart_detail')
        else:
            messages.error(request, "Please correct the shipping details errors.")
    else:
        # Prepopulate email if logged in
        form = OrderCreateForm(initial={'email': request.user.email})

    return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})

@login_required(login_url='accounts:login')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required(login_url='accounts:login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot import process_rag_query

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            message = data.get('message', '')
            response = process_rag_query(request.user, message)
            return JsonResponse(response)
        except Exception:
            return JsonResponse({"reply": "Sorry, an error occurred processing your query.", "action": "error"}, status=400)
    return JsonResponse({"error": "POST method required"}, status=405)
