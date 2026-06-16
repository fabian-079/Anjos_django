from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect
from infrastructure.container import get_cart_usecases


def cart_view(request):
    if request.user.is_authenticated:
        uc = get_cart_usecases()
        items = uc.get_cart_items(request.user.id)
        total = uc.get_cart_total(request.user.id)
        is_guest = False
    else:
        items, total = _guest_cart_items(request)
        is_guest = True
    return render(request, 'carrito.html', {
        'cart_items': items, 'cart_total': total, 'is_guest': is_guest,
    })


def cart_update(request, pk):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if request.user.is_authenticated:
            try:
                get_cart_usecases().update_quantity(pk, quantity)
                messages.success(request, 'Cantidad actualizada.')
            except Exception as e:
                messages.error(request, str(e))
        else:
            guest_cart = request.session.get('guest_cart', {})
            if str(pk) in guest_cart:
                if quantity > 0:
                    guest_cart[str(pk)] = quantity
                else:
                    del guest_cart[str(pk)]
                request.session['guest_cart'] = guest_cart
    return redirect('carrito')


def cart_remove(request, pk):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                get_cart_usecases().remove_from_cart(pk)
                messages.success(request, 'Producto removido del carrito.')
            except Exception as e:
                messages.error(request, str(e))
        else:
            guest_cart = request.session.get('guest_cart', {})
            guest_cart.pop(str(pk), None)
            request.session['guest_cart'] = guest_cart
    return redirect('carrito')


def _guest_cart_items(request):
    from infrastructure.container import get_product_usecases
    guest_cart = request.session.get('guest_cart', {})
    uc = get_product_usecases()
    items = []
    total = Decimal('0')
    for pid_str, qty in guest_cart.items():
        product = uc.get_product_by_id(int(pid_str))
        if product and product.is_active:
            subtotal = product.price * qty
            total += subtotal
            items.append({
                'id': int(pid_str),
                'product_id': int(pid_str),
                'product_name': product.name,
                'product_image': product.get_image_url(),
                'product_price': product.price,
                'quantity': qty,
                'subtotal': subtotal,
            })
    return items, total
