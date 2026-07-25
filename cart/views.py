from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem

class GuestCartItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity
    def get_cost(self):
        return self.product.price * self.quantity

class GuestCart:
    def __init__(self, request):
        self.session = request.session
        self.cart_data = self.session.get('session_cart', {})

    def items_all(self):
        items = []
        product_ids = [int(pk) for pk in self.cart_data.keys()]
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            qty = self.cart_data.get(str(product.id), 0)
            if qty > 0:
                items.append(GuestCartItem(product, qty))
        return items

    @property
    def items(self):
        guest_self = self
        class ItemsManager:
            def all(self):
                return guest_self.items_all()
            def count(self):
                return len(guest_self.items_all())
        return ItemsManager()

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items_all())

    def get_total_items(self):
        return sum(self.cart_data.values())

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    return GuestCart(request)

def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
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

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if item_created:
            cart_item.quantity = quantity
        else:
            total_qty = cart_item.quantity + quantity
            if product.stock < total_qty:
                messages.error(request, f"Cannot add more. Only {product.stock} items available.")
                return redirect('cart:cart_detail')
            cart_item.quantity = total_qty
        cart_item.save()
    else:
        # Session Guest Cart
        session_cart = request.session.get('session_cart', {})
        prod_id_str = str(product.id)
        current_qty = session_cart.get(prod_id_str, 0)
        new_qty = current_qty + quantity
        if product.stock < new_qty:
            messages.error(request, f"Cannot add more. Only {product.stock} items available.")
            return redirect('cart:cart_detail')
        session_cart[prod_id_str] = new_qty
        request.session['session_cart'] = session_cart

    messages.success(request, f"Added {product.name} to your cart.")
    return redirect('cart:cart_detail')

def cart_update(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        try:
            new_quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            new_quantity = 1

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_item = get_object_or_404(CartItem, cart=cart, product=product)
            if new_quantity <= 0:
                cart_item.delete()
                messages.success(request, f"Removed {product.name} from your cart.")
            elif new_quantity > product.stock:
                messages.error(request, f"Cannot set quantity to {new_quantity}. Only {product.stock} available.")
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, f"Updated quantity for {product.name}.")
        else:
            session_cart = request.session.get('session_cart', {})
            prod_id_str = str(product.id)
            if new_quantity <= 0:
                session_cart.pop(prod_id_str, None)
                messages.success(request, f"Removed {product.name} from your cart.")
            elif new_quantity > product.stock:
                messages.error(request, f"Cannot set quantity to {new_quantity}. Only {product.stock} available.")
            else:
                session_cart[prod_id_str] = new_quantity
                messages.success(request, f"Updated quantity for {product.name}.")
            request.session['session_cart'] = session_cart

    return redirect('cart:cart_detail')

def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    action = request.POST.get('action', 'remove')
    
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        if action == 'decrement' and cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f"Updated quantity of {product.name}.")
        else:
            cart_item.delete()
            messages.success(request, f"Removed {product.name} from your cart.")
    else:
        session_cart = request.session.get('session_cart', {})
        prod_id_str = str(product.id)
        current_qty = session_cart.get(prod_id_str, 0)
        if action == 'decrement' and current_qty > 1:
            session_cart[prod_id_str] = current_qty - 1
            messages.success(request, f"Updated quantity of {product.name}.")
        else:
            session_cart.pop(prod_id_str, None)
            messages.success(request, f"Removed {product.name} from your cart.")
        request.session['session_cart'] = session_cart
        
    return redirect('cart:cart_detail')

def cart_clear(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                cart.items.all().delete()
        else:
            request.session['session_cart'] = {}
        messages.success(request, "Your shopping cart has been cleared.")
    return redirect('cart:cart_detail')
