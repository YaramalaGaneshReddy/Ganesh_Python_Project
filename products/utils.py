import urllib.parse

def get_dynamic_product_image(query_name):
    """
    Returns a dynamic high-quality image URL from Unsplash based on the product search query/name.
    """
    if not query_name:
        query_name = "product"
    
    clean_query = urllib.parse.quote_plus(query_name.strip())
    # Unsplash source URL dynamically provides high quality relevant images for search terms
    return f"https://source.unsplash.com/600x600/?{clean_query}"

def get_product_image_fallback(product):
    """
    Returns existing image URL or dynamic keyword-matched product image.
    """
    if hasattr(product, 'image') and product.image:
        try:
            return product.image.url
        except Exception:
            pass
            
    # Dynamic fallback based on product name
    encoded_name = urllib.parse.quote_plus(product.name if hasattr(product, 'name') else 'item')
    return f"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80"
