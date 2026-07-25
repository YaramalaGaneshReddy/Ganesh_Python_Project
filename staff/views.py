from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from products.models import Product
from orders.models import Order, OrderItem
from .forms import ProductForm, OrderStatusForm

def is_staff_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_dashboard(request):
    total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0.00
    total_orders = Order.objects.count()
    
    status_counts = {
        'pending': Order.objects.filter(status='Pending').count(),
        'paid': Order.objects.filter(status='Paid').count(),
        'shipped': Order.objects.filter(status='Shipped').count(),
        'delivered': Order.objects.filter(status='Delivered').count(),
    }
    
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(stock__lte=5).count()
    total_customers = User.objects.count()
    
    recent_orders = Order.objects.all().order_by('-created_at')[:8]
    recent_products = Product.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'status_counts': status_counts,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
    }
    return render(request, 'staff/dashboard.html', context)

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_product_list(request):
    products = Product.objects.all().order_by('-created_at')
    
    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
        
    stock_filter = request.GET.get('stock')
    if stock_filter == 'low':
        products = products.filter(stock__gt=0, stock__lte=5)
    elif stock_filter == 'out':
        products = products.filter(stock=0)
        
    return render(request, 'staff/product_list.html', {
        'products': products,
        'query': query,
        'stock_filter': stock_filter,
    })

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' created successfully!")
            return redirect('staff:product_list')
        else:
            messages.error(request, "Failed to create product. Please check form errors.")
    else:
        form = ProductForm()
        
    return render(request, 'staff/product_form.html', {
        'form': form,
        'title': 'Add New Product',
        'button_text': 'Create Product',
    })

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect('staff:product_list')
        else:
            messages.error(request, "Failed to update product. Please check form errors.")
    else:
        form = ProductForm(instance=product)
        
    return render(request, 'staff/product_form.html', {
        'form': form,
        'product': product,
        'title': f'Edit Product: {product.name}',
        'button_text': 'Update Product',
    })

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f"Product '{product_name}' deleted successfully.")
    return redirect('staff:product_list')

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_quick_stock_update(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        try:
            new_stock = int(request.POST.get('stock', 0))
            if new_stock < 0:
                new_stock = 0
            product.stock = new_stock
            product.save()
            messages.success(request, f"Stock for '{product.name}' updated to {new_stock}.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid stock value.")
    return redirect('staff:product_list')

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter in ['Pending', 'Paid', 'Shipped', 'Delivered']:
        orders = orders.filter(status=status_filter)
        
    return render(request, 'staff/order_list.html', {
        'orders': orders,
        'status_filter': status_filter,
    })

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order #{order.id} status updated to {order.status}.")
            return redirect('staff:order_detail', pk=order.pk)
    else:
        form = OrderStatusForm(instance=order)
        
    return render(request, 'staff/order_detail.html', {
        'order': order,
        'form': form,
    })

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_user_list(request):
    users = User.objects.all().annotate(order_count=Count('orders')).order_by('-date_joined')
    return render(request, 'staff/user_list.html', {'users': users})

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_toggle_user(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        if user == request.user and not request.user.is_superuser:
            messages.error(request, "You cannot modify your own staff privileges.")
        else:
            user.is_staff = not user.is_staff
            user.save()
            status_str = "granted" if user.is_staff else "revoked"
            messages.success(request, f"Staff privileges {status_str} for user '{user.username}'.")
    return redirect('staff:user_list')

from orders.models import PaymentSetting

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_payment_settings(request):
    try:
        setting = PaymentSetting.objects.first()
        if not setting:
            setting = PaymentSetting.objects.create(
                upi_id="centralbank9361@ybl",
                account_name="Central Bank - 9361 (PhonePe)",
                qr_code_url="/static/images/phonepe_qr_scanner.jpg"
            )
    except Exception:
        setting = None

    if request.method == 'POST' and setting:
        setting.upi_id = request.POST.get('upi_id', setting.upi_id)
        setting.account_name = request.POST.get('account_name', setting.account_name)
        setting.qr_code_url = request.POST.get('qr_code_url', setting.qr_code_url)
        setting.save()
        messages.success(request, "Admin Payment QR Scanner settings updated successfully!")
        return redirect('staff:payment_settings')

    return render(request, 'staff/payment_settings.html', {'setting': setting})

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_user_detail(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    user_orders = Order.objects.filter(user=target_user).order_by('-created_at')
    total_spent = user_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0.00
    
    return render(request, 'staff/user_detail.html', {
        'target_user': target_user,
        'user_orders': user_orders,
        'total_spent': total_spent,
    })

@user_passes_test(is_staff_check, login_url='accounts:login')
def staff_database_summary(request):
    db_metrics = {
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_order_items': OrderItem.objects.count(),
        'total_revenue': Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0.00,
        'paid_orders_count': Order.objects.filter(status='Paid').count(),
        'pending_orders_count': Order.objects.filter(status='Pending').count(),
        'shipped_orders_count': Order.objects.filter(status='Shipped').count(),
        'cancelled_orders_count': Order.objects.filter(status='Cancelled').count(),
    }
    recent_users = User.objects.all().order_by('-date_joined')[:10]
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'staff/database_summary.html', {
        'db_metrics': db_metrics,
        'recent_users': recent_users,
        'recent_orders': recent_orders,
    })
