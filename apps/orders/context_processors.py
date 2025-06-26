# apps/orders/context_processors.py
def cart_context(request):
    """Контекстный процессор для отображения корзины в шаблонах"""
    cart_count = 0
    
    try:
        from .models import get_cart_for_request
        if hasattr(request, 'user'):
            cart = get_cart_for_request(request)
            if cart:
                cart_count = cart.items_count
    except Exception:
        cart_count = 0
    
    return {
        'cart_count': cart_count
    }