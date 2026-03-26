from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from infrastructure.container import get_cart_usecases


@login_required
def cart_view(request):
    uc = get_cart_usecases()
    items = uc.get_cart_items(request.user.id)
    total = uc.get_cart_total(request.user.id)
    return render(request, 'carrito.html', {'cart_items': items, 'cart_total': total})


@login_required
def cart_update(request, pk):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            get_cart_usecases().update_quantity(pk, quantity)
            messages.success(request, 'Cantidad actualizada.')
        except Exception as e:
            messages.error(request, str(e))
    return redirect('carrito')


@login_required
def cart_remove(request, pk):
    if request.method == 'POST':
        try:
            get_cart_usecases().remove_from_cart(pk)
            messages.success(request, 'Producto removido del carrito.')
        except Exception as e:
            messages.error(request, str(e))
    return redirect('carrito')
