from .models import Cart

def cart_total_items(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            return {'cart_total_items': cart.get_total_items()}
        except Cart.DoesNotExist:
            return {'cart_total_items': 0}
    else:
        session_cart = request.session.get('session_cart', {})
        total = sum(session_cart.values())
        return {'cart_total_items': total}
