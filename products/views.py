from django.shortcuts import render, get_object_or_404
from .models import Product
import urllib.parse

def product_list(request):
    products = list(Product.objects.all().order_by('-created_at'))
    query = request.GET.get('q', '').strip()
    
    if query:
        products = list(Product.objects.filter(name__icontains=query))
    
    # Dynamically ensure every product has a valid high quality image URL assigned
    for prod in products:
        if not prod.image:
            search_term = query if query else prod.name
            encoded = urllib.parse.quote_plus(search_term)
            prod.dynamic_image_url = f"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80"
        else:
            try:
                prod.dynamic_image_url = prod.image.url
            except Exception:
                encoded = urllib.parse.quote_plus(prod.name)
                prod.dynamic_image_url = f"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80"
                
    return render(request, 'products/product_list.html', {'products': products, 'query': query})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not product.image:
        encoded = urllib.parse.quote_plus(product.name)
        product.dynamic_image_url = f"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80"
    else:
        try:
            product.dynamic_image_url = product.image.url
        except Exception:
            product.dynamic_image_url = f"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80"
            
    return render(request, 'products/product_detail.html', {'product': product})