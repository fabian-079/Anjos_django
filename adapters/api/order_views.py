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
from application.services.wompi_service import WompiService


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
    # Obtener lista de bancos PSE para el checkout
    wompi_service = WompiService()
    pse_banks = wompi_service.get_pse_banks()
    wompi_status = wompi_service.get_config_status()
    return render(request, 'orders/checkout.html', {
        'cart_items': items,
        'subtotal': total,
        'tax': tax,
        'total': total + tax,
        'payment_methods': PaymentMethod.CHOICES,
        'pse_banks': pse_banks,
        'wompi_configured': wompi_status['configured'],
    })


@login_required
def order_create(request):
    """
    Crear la orden y, si el metodo es TARJETA o PSE, redirigir al gateway de pago.
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
    except Exception as e:
        messages.error(request, f'Error inesperado al crear la orden: {str(e)}')
        return redirect('checkout')

    # Verificar que la orden tenga ID valido antes de continuar
    if not order or not order.id:
        messages.error(request, 'La orden no se pudo guardar. Intenta nuevamente.')
        return redirect('checkout')

    # Guardar order_id en sesion como respaldo para callbacks
    request.session['last_order_id'] = order.id
    request.session['last_order_number'] = order.order_number

    # --- TARJETA (Stripe) ---
    if payment_method == 'TARJETA':
        stripe_service = StripeCheckoutService()
        if stripe_service.is_configured():
            result = stripe_service.create_checkout_session(
                order=order,
                order_items=order.items,
            )
            if result['success']:
                return redirect(result['checkout_url'])
            else:
                messages.warning(
                    request,
                    f'Orden {order.order_number} creada, pero no se pudo iniciar Stripe: {result.get("error", "Error desconocido")}. '
                    f'Puedes pagarla mas tarde desde Mis Ordenes.'
                )
        else:
            messages.info(
                request,
                f'Orden {order.order_number} creada. El pago con tarjeta esta en configuracion.'
            )
        return redirect('order_show', pk=order.id)

    # --- PSE (Wompi) ---
    if payment_method == 'PSE':
        bank_code = request.POST.get('pse_bank', '').strip()
        user_type = request.POST.get('pse_user_type', '0')
        user_legal_id = request.POST.get('pse_user_legal_id', '').strip()
        user_legal_id_type = request.POST.get('pse_user_legal_id_type', 'CC')

        if not bank_code:
            messages.error(request, 'Debes seleccionar un banco para PSE.')
            return redirect('checkout')
        if not user_legal_id:
            messages.error(request, 'Debes ingresar tu numero de documento para PSE.')
            return redirect('checkout')

        wompi_service = WompiService()
        if wompi_service.is_configured():
            pse_banks = wompi_service.get_pse_banks()
            bank_name = ''
            for b in pse_banks:
                if str(b.get('code')) == bank_code:
                    bank_name = b.get('name', '')
                    break

            result = wompi_service.create_pse_transaction(
                order=order,
                order_items=order.items,
                bank_code=bank_code,
                user_type=int(user_type),
                user_legal_id=user_legal_id,
                user_legal_id_type=user_legal_id_type,
                customer_email=request.user.email or '',
                customer_name=request.user.name or '',
                customer_phone=request.POST.get('phone', '').strip() or (request.user.phone or ''),
                bank_name=bank_name,
            )
            if result['success']:
                if result.get('redirect_url'):
                    return redirect(result['redirect_url'])
                else:
                    messages.warning(
                        request,
                        f'Orden {order.order_number} creada, pero Wompi no devolvio URL de pago. '
                        f'Detalles: {result.get("debug_data", "N/A")}. Intenta desde Mis Ordenes.'
                    )
            else:
                messages.warning(
                    request,
                    f'Orden {order.order_number} creada, pero no se pudo iniciar PSE: {result.get("error", "Error desconocido")}. '
                    f'Puedes intentar nuevamente desde Mis Ordenes.'
                )
        else:
            messages.info(
                request,
                f'Orden {order.order_number} creada. El pago PSE esta en configuracion.'
            )
        return redirect('order_show', pk=order.id)

    # --- EFECTIVO ---
    if payment_method == 'EFECTIVO':
        messages.success(
            request,
            f'Orden {order.order_number} creada exitosamente. Pagas contra entrega al recibir tu pedido.'
        )
        return redirect('order_show', pk=order.id)

    messages.success(request, f'Orden {order.order_number} creada exitosamente.')
    return redirect('order_show', pk=order.id)


@login_required
def stripe_success(request):
    """
    Stripe redirige aqui despues de un pago exitoso.
    Actualiza la orden a PROCESSING y muestra confirmacion.
    """
    order_id = request.GET.get('order_id')
    # Fallback: buscar en sesion si no viene en URL
    if not order_id:
        order_id = request.session.get('last_order_id')

    if not order_id:
        messages.error(request, 'No se encontro informacion de la orden en la URL ni en la sesion.')
        return redirect('order_index')

    try:
        order_id = int(order_id)
    except ValueError:
        messages.error(request, 'ID de orden invalido.')
        return redirect('order_index')

    order = get_order_usecases().get_order_by_id(order_id)
    if not order:
        messages.error(request, f'Orden #{order_id} no encontrada en la base de datos.')
        return redirect('order_index')

    if order.user_id != request.user.id and not request.user.is_admin():
        messages.error(request, 'No tienes permiso para ver esta orden.')
        return redirect('order_index')

    # Actualizar estado a PROCESSING si esta PENDING
    if order.status == OrderStatus.PENDING:
        try:
            get_order_usecases().update_order_status(order_id, OrderStatus.PROCESSING)
            messages.success(request, f'Pago confirmado! Tu orden {order.order_number} esta en proceso.')
        except Exception as e:
            messages.warning(request, f'Pago recibido, pero hubo un problema actualizando la orden: {e}')
    elif order.status == OrderStatus.PROCESSING:
        messages.success(request, f'Tu orden {order.order_number} ya fue confirmada.')

    return render(request, 'orders/stripe_success.html', {'order': order})


@login_required
def stripe_cancel(request):
    """
    Stripe redirige aqui si el usuario cancela el pago.
    La orden queda en PENDING para que pueda reintentar.
    """
    order_id = request.GET.get('order_id')
    if not order_id:
        order_id = request.session.get('last_order_id')

    if not order_id:
        messages.error(request, 'No se encontro informacion de la orden en la URL ni en la sesion.')
        return redirect('order_index')

    try:
        order_id = int(order_id)
    except ValueError:
        messages.error(request, 'ID de orden invalido.')
        return redirect('order_index')

    order = get_order_usecases().get_order_by_id(order_id)
    if not order:
        messages.error(request, f'Orden #{order_id} no encontrada en la base de datos.')
        return redirect('order_index')

    if order.user_id != request.user.id and not request.user.is_admin():
        messages.error(request, 'No tienes permiso.')
        return redirect('order_index')

    messages.warning(
        request,
        f'El pago de la orden {order.order_number} fue cancelado. '
        f'Puedes intentar nuevamente desde Mis Ordenes.'
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
# Callback de Wompi (PSE y otros métodos)
# ---------------------------------------------------------------------------

@login_required
def wompi_callback(request):
    """
    Wompi redirige aqui despues de que el usuario completa el pago PSE.
    El estado real se confirma via webhook, pero aqui mostramos feedback al usuario.
    """
    transaction_id = request.GET.get('id')
    status = request.GET.get('status', 'PENDING')
    reference = request.GET.get('reference', '')

    order_id = None
    order_number = None

    # Metodo 1: extraer de reference (ANJOS-ORD-{timestamp})
    if reference.startswith('ANJOS-'):
        order_number = reference.replace('ANJOS-', '')
        try:
            order = get_order_usecases().get_by_order_number(order_number)
            if order:
                order_id = order.id
        except Exception:
            pass

    # Metodo 2: buscar via API Wompi por transaction_id
    if not order_id and transaction_id:
        wompi_service = WompiService()
        txn = wompi_service.get_transaction_status(transaction_id)
        if txn.get('success'):
            ref = txn.get('reference', '')
            if ref.startswith('ANJOS-'):
                order_number = ref.replace('ANJOS-', '')
                try:
                    order = get_order_usecases().get_by_order_number(order_number)
                    if order:
                        order_id = order.id
                except Exception:
                    pass

    # Metodo 3: fallback a sesion
    if not order_id:
        order_id = request.session.get('last_order_id')
        order_number = request.session.get('last_order_number')

    if not order_id:
        messages.error(request, 'No se encontro informacion de la orden. Ref: ' + (reference or 'N/A'))
        return redirect('order_index')

    order = get_order_usecases().get_order_by_id(order_id)
    if not order:
        messages.error(request, f'Orden #{order_id} no encontrada en la base de datos.')
        return redirect('order_index')

    if order.user_id != request.user.id and not request.user.is_admin():
        messages.error(request, 'No tienes permiso.')
        return redirect('order_index')

    if status.upper() in ('APPROVED', 'APROBADA', 'COMPLETED'):
        if order.status == OrderStatus.PENDING:
            try:
                get_order_usecases().update_order_status(order_id, OrderStatus.PROCESSING)
            except Exception:
                pass
        messages.success(request, f'Pago PSE confirmado! Tu orden {order.order_number} esta en proceso.')
        return render(request, 'orders/stripe_success.html', {'order': order})
    elif status.upper() in ('DECLINED', 'REJECTED', 'DENIED'):
        messages.error(request, f'El pago PSE de la orden {order.order_number} fue rechazado.')
        return redirect('order_show', pk=order.id)
    else:
        messages.info(
            request,
            f'Orden {order.order_number}: tu pago PSE esta siendo procesado. '
            f'Te notificaremos cuando se confirme.'
        )
        return redirect('order_show', pk=order.id)


# ---------------------------------------------------------------------------
# Webhook de Wompi (público, no requiere login)
# ---------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(["POST"])
def wompi_webhook(request):
    """
    Recibe eventos de Wompi de forma asincrónica.
    """
    import json
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)

    event = payload.get('event', '')
    data = payload.get('data', {})
    transaction = data.get('transaction', {})

    if event == 'transaction.updated':
        status = transaction.get('status', '')
        reference = transaction.get('reference', '')

        if reference.startswith('ANJOS-'):
            order_number = reference.replace('ANJOS-', '')
            try:
                order = get_order_usecases().get_by_order_number(order_number)
                if order:
                    if status in ('APPROVED', 'COMPLETED'):
                        if order.status == OrderStatus.PENDING:
                            get_order_usecases().update_order_status(order.id, OrderStatus.PROCESSING)
                    elif status in ('DECLINED', 'VOIDED', 'ERROR'):
                        if order.status == OrderStatus.PENDING:
                            get_order_usecases().update_order_status(order.id, OrderStatus.CANCELLED)
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
