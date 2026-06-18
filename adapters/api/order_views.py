from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from adapters.api.decorators import admin_required
from infrastructure.container import get_order_usecases, get_cart_usecases
from domain.entities.order import OrderStatus, PaymentMethod
from application.services.stripe_checkout_service import StripeCheckoutService


# ---------------------------------------------------------------------------
# Vistas públicas / cliente
# ---------------------------------------------------------------------------

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
    """
    Crear la orden y, si el método es TARJETA y Stripe está configurado,
    redirigir al usuario a Stripe Checkout.
    """
    if request.method != 'POST':
        return redirect('checkout')

    payment_method = request.POST.get('payment_method', 'TARJETA')

    try:
        order = get_order_usecases().create_order(
            user_id=request.user.id,
            shipping_address=request.POST.get('shipping_address', '').strip(),
            billing_address=request.POST.get('billing_address', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            payment_method=payment_method,
            notes=request.POST.get('notes', '').strip() or None,
        )
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('checkout')

    # Si es pago con tarjeta, intentar redirigir a Stripe Checkout
    if payment_method == 'TARJETA':
        stripe_service = StripeCheckoutService()
        if stripe_service.is_configured():
            result = stripe_service.create_checkout_session(
                order=order,
                order_items=order.items,
            )
            if result['success']:
                # Guardar session_id en la orden para referencia futura
                # (Podríamos guardarlo en BD si tuviéramos el campo; por ahora lo pasamos en URL)
                return redirect(result['checkout_url'])
            else:
                messages.warning(
                    request,
                    f'Orden creada, pero no se pudo iniciar Stripe: {result["error"]}. '
                    f'Puedes pagarla más tarde desde Mis Órdenes.'
                )
                return redirect('order_show', pk=order.id)
        else:
            messages.info(
                request,
                f'Orden {order.order_number} creada exitosamente. '
                f'El pago con tarjeta está en configuración; contacta al administrador para finalizar.'
            )
            return redirect('order_show', pk=order.id)

    # Otros métodos (PSE, Efectivo): solo crea la orden
    messages.success(request, f'Orden {order.order_number} creada exitosamente.')
    return redirect('order_show', pk=order.id)


@login_required
def stripe_success(request):
    """
    Stripe redirige aquí después de un pago exitoso.
    Actualiza la orden a PROCESSING y muestra confirmación.
    """
    order_id = request.GET.get('order_id')
    if not order_id:
        messages.error(request, 'No se encontró información de la orden.')
        return redirect('order_index')

    try:
        order_id = int(order_id)
    except ValueError:
        messages.error(request, 'ID de orden inválido.')
        return redirect('order_index')

    order = get_order_usecases().get_order_by_id(order_id)
    if not order:
        messages.error(request, 'Orden no encontrada.')
        return redirect('order_index')

    if order.user_id != request.user.id and not request.user.is_admin():
        messages.error(request, 'No tienes permiso para ver esta orden.')
        return redirect('order_index')

    # Actualizar estado a PROCESSING si está PENDING
    if order.status == OrderStatus.PENDING:
        try:
            get_order_usecases().update_order_status(order_id, OrderStatus.PROCESSING)
            messages.success(request, f'¡Pago confirmado! Tu orden {order.order_number} está en proceso.')
        except Exception as e:
            messages.warning(request, f'Pago recibido, pero hubo un problema actualizando la orden: {e}')
    elif order.status == OrderStatus.PROCESSING:
        messages.success(request, f'Tu orden {order.order_number} ya fue confirmada.')

    return render(request, 'orders/stripe_success.html', {'order': order})


@login_required
def stripe_cancel(request):
    """
    Stripe redirige aquí si el usuario cancela el pago.
    La orden queda en PENDING para que pueda reintentar.
    """
    order_id = request.GET.get('order_id')
    if not order_id:
        messages.error(request, 'No se encontró información de la orden.')
        return redirect('order_index')

    try:
        order_id = int(order_id)
    except ValueError:
        messages.error(request, 'ID de orden inválido.')
        return redirect('order_index')

    order = get_order_usecases().get_order_by_id(order_id)
    if not order:
        messages.error(request, 'Orden no encontrada.')
        return redirect('order_index')

    if order.user_id != request.user.id and not request.user.is_admin():
        messages.error(request, 'No tienes permiso.')
        return redirect('order_index')

    messages.warning(
        request,
        f'El pago de la orden {order.order_number} fue cancelado. '
        f'Puedes intentar nuevamente desde Mis Órdenes.'
    )
    return redirect('order_show', pk=order.id)


# ---------------------------------------------------------------------------
# Webhook de Stripe (público, no requiere login)
# ---------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Recibe eventos de Stripe de forma asincrónica.
    Usar para confirmar pagos reales en producción.
    """
    from django.conf import settings
    stripe_service = StripeCheckoutService()

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        if stripe_service.webhook_secret:
            event = stripe_service.construct_webhook_event(payload, sig_header)
        else:
            import json
            event = json.loads(payload)
    except Exception as e:
        return HttpResponse(f'Invalid payload: {e}', status=400)

    event_type = event.get('type') if isinstance(event, dict) else getattr(event, 'type', None)

    if event_type == 'checkout.session.completed':
        data_object = event.get('data', {}).get('object', {}) if isinstance(event, dict) else event.data.object
        metadata = data_object.get('metadata', {})
        order_id = metadata.get('order_id')

        if order_id:
            try:
                get_order_usecases().update_order_status(int(order_id), OrderStatus.PROCESSING)
            except Exception:
                pass

    return HttpResponse(status=200)


# ---------------------------------------------------------------------------
# Vistas de administración
# ---------------------------------------------------------------------------

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
