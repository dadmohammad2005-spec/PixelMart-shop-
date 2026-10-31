from .models import Cart, CartItem


def get_or_create_cart(request):
    """
    Retrieve or initialize the cart for either authenticated user or guest visitor.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    if not request.session.session_key:
        request.session.create()

    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
    return cart


def merge_session_cart(request, user, old_session_key=None):
    """
    Safely merges guest session cart items into authenticated user cart upon login/registration.
    """
    session_key = old_session_key or request.session.session_key
    if not session_key:
        return

    try:
        session_cart = Cart.objects.get(session_key=session_key, user=None)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    for item in session_cart.items.select_related('product').all():
        product = item.product
        existing_item = user_cart.items.filter(product=product).first()
        if existing_item:
            # Combine quantities up to available stock
            new_quantity = existing_item.quantity + item.quantity
            if product.stock > 0:
                existing_item.quantity = min(new_quantity, product.stock)
                existing_item.save()
        else:
            # Reassign item to user cart up to available stock
            if product.stock > 0:
                item.cart = user_cart
                item.quantity = min(item.quantity, product.stock)
                item.save()
            else:
                item.delete()

    if session_cart.coupon_code and not user_cart.coupon_code:
        user_cart.coupon_code = session_cart.coupon_code
        user_cart.save()

    session_cart.delete()
