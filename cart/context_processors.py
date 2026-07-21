from .models import Cart

def cart_total_items(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            return {'cart_total_items': cart.get_total_items()}
        except Cart.DoesNotExist:
            return {'cart_total_items': 0}
    return {'cart_total_items': 0}
