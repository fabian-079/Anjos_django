from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from adapters.api.decorators import admin_required
from infrastructure.container import get_order_usecases, get_cart_usecases
from domain.entities.order import OrderStatus, PaymentMethod


@login_required
def order_index(request):
    uc = get_order_usecases()
    if request.user.is_admin():
        orders = uc.get_all_orders()
    else:
        orders = uc.get_orders_by_user(request.user.id)
    return render(request, 'orders/index.html', {'orders': orders})


@login_required
def order_show(request, pk):
    order = get_order_usecases().get_order_by_id(pk)
    if not order:
        messages.error(request, 'Orden no encontrada.')
        return redirect('order_index')
    if not request.user.is_admin() and order.user_id != request.user.id:
        messages.error(request, 'No tienes permiso para ver esta orden.')
        return redirect('order_index')
    return render(request, 'orders/show.html', {'order': order})


@login_required
def checkout_view(request):
    uc = get_cart_usecases()
    items = uc.get_cart_items(request.user.id)
    if not items:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('carrito')
    total = uc.get_cart_total(request.user.id)
    from decimal import Decimal
    tax = total * Decimal('0.19')
    return render(request, 'orders/checkout.html', {
        'cart_items': items,
        'subtotal': total,
        'tax': tax,
        'total': total + tax,
        'payment_methods': PaymentMethod.CHOICES,
    })


@login_required
def order_create(request):
    if request.method != 'POST':
        return redirect('checkout')
    uc = get_order_usecases()
    try:
        order = uc.create_order(
            user_id=request.user.id,
            shipping_address=request.POST.get('shipping_address', '').strip(),
            billing_address=request.POST.get('billing_address', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            payment_method=request.POST.get('payment_method', 'TARJETA'),
            notes=request.POST.get('notes', '').strip() or None,
        )
        messages.success(request, f'Orden {order.order_number} creada exitosamente.')
        return redirect('order_show', pk=order.id)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('checkout')


@admin_required
def order_edit_form(request, pk):
    order = get_order_usecases().get_order_by_id(pk)
    if not order:
        messages.error(request, 'Orden no encontrada.')
        return redirect('order_index')
    return render(request, 'orders/edit.html', {
        'order': order,
        'status_choices': OrderStatus.CHOICES,
        'payment_methods': PaymentMethod.CHOICES,
    })


@admin_required
def order_update(request, pk):
    if request.method != 'POST':
        return redirect('order_index')
    uc = get_order_usecases()
    try:
        uc.update_order(
            order_id=pk,
            status=request.POST.get('status', 'PENDING'),
            shipping_address=request.POST.get('shipping_address', '').strip(),
            billing_address=request.POST.get('billing_address', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            payment_method=request.POST.get('payment_method', 'TARJETA'),
            notes=request.POST.get('notes', '').strip() or None,
        )
        messages.success(request, 'Orden actualizada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('order_show', pk=pk)


@admin_required
def order_delete(request, pk):
    if request.method == 'POST':
        try:
            get_order_usecases().deactivate_order(pk)
            messages.success(request, 'Orden desactivada.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('order_index')
