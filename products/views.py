from django.shortcuts import render, get_object_or_404
from .models import Product

def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    # Optional search query
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)
    return render(request, 'products/product_list.html', {'products': products, 'query': query})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})