from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from cart.models import Cart
from cart.views import get_or_create_cart
from .models import Order, OrderItem
from .forms import OrderCreateForm

def order_create(request):
    cart = get_or_create_cart(request)

    if cart.items.count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('products:home')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        payment_method = request.POST.get('payment_method', 'card')
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Check stock for all items first
                    for item in cart.items.all():
                        if item.product.stock < item.quantity:
                            raise ValueError(f"Insufficient stock for product '{item.product.name}'. Only {item.product.stock} left.")

                    # Save Order
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    else:
                        order.user = None
                    order.total_price = cart.get_total_price()
                    
                    # Set payment status
                    if payment_method in ['card', 'upi']:
                        order.status = 'Paid'
                    else:
                        order.status = 'Pending'
                        
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

                    # Clear cart
                    if request.user.is_authenticated:
                        user_cart = Cart.objects.filter(user=request.user).first()
                        if user_cart:
                            user_cart.items.all().delete()
                    else:
                        request.session['session_cart'] = {}
                        
                messages.success(request, f"Your order #{order.id} has been placed successfully ({'Paid Online' if order.status == 'Paid' else 'Cash on Delivery'})!")
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
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['email'] = request.user.email
            initial_data['first_name'] = request.user.first_name
            initial_data['last_name'] = request.user.last_name
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})

@login_required(login_url='accounts:login')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})

@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            order_id = data.get('order_id')
            payment_method = data.get('payment_method', 'Online Payment')
            
            order = get_object_or_404(Order, id=order_id)
            order.status = 'Paid'
            order.save()
            
            return JsonResponse({"status": "success", "message": f"Payment via {payment_method} verified!", "order_id": order.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"error": "POST required"}, status=405)

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
