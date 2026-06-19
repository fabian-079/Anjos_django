from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from adapters.api.decorators import admin_required
from infrastructure.container import get_order_usecases, get_cart_usecases, get_user_usecases
from domain.entities.order import OrderStatus, PaymentMethod
from application.services.stripe_checkout_service import StripeCheckoutService
from application.services.wompi_service import WompiService

# PDF generation
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


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
    txn_id = request.GET.get('txn_id', '')
    wompi_ref = request.GET.get('wompi_ref', '')
    return render(request, 'orders/show.html', {
        'order': order,
        'txn_id': txn_id,
        'wompi_ref': wompi_ref,
    })


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

    # --- TARJETA (Wompi) ---
    if payment_method == 'TARJETA':
        card_number = request.POST.get('card_number', '').strip()
        card_holder = request.POST.get('card_holder', '').strip()
        card_exp_month = request.POST.get('card_exp_month', '').strip()
        card_exp_year = request.POST.get('card_exp_year', '').strip()
        card_cvc = request.POST.get('card_cvc', '').strip()
        card_installments = int(request.POST.get('card_installments', '1'))

        if not card_number or not card_holder or not card_exp_month or not card_exp_year or not card_cvc:
            messages.error(request, 'Debes completar todos los datos de la tarjeta.')
            return redirect('checkout')

        # Validar nombre del titular (Wompi exige minimo 5 caracteres)
        if len(card_holder.strip()) < 5:
            messages.error(request, 'El nombre del titular debe tener al menos 5 caracteres.')
            return redirect('checkout')

        wompi_service = WompiService()
        if wompi_service.is_configured():
            # 1. Tokenizar la tarjeta
            token_result = wompi_service.tokenize_card(
                number=card_number,
                cvc=card_cvc,
                exp_month=card_exp_month,
                exp_year=card_exp_year,
                card_holder=card_holder,
            )
            if not token_result['success']:
                messages.error(request, f'Error con la tarjeta: {token_result["error"]}')
                return redirect('order_show', pk=order.id)

            # 2. Crear la transaccion
            txn_result = wompi_service.create_card_transaction(
                order=order,
                token_id=token_result['token_id'],
                installments=card_installments,
                customer_email=request.user.email or '',
                customer_name=request.user.name or '',
                customer_phone=request.POST.get('phone', '').strip() or (request.user.phone or ''),
            )

            if txn_result['success']:
                txn_id = txn_result.get('transaction_id')
                wompi_ref = txn_result.get('reference')

                # Si requiere redireccion 3D Secure
                if txn_result.get('redirect_url'):
                    return redirect(txn_result['redirect_url'])

                # Si fue aprobada inmediatamente
                status = (txn_result.get('status') or '').upper()
                if status in ('APPROVED', 'COMPLETED'):
                    try:
                        get_order_usecases().update_order_status(order.id, OrderStatus.PROCESSING)
                    except Exception:
                        pass
                    messages.success(
                        request,
                        f'Pago aprobado! Tu orden {order.order_number} esta en proceso.'
                    )
                    return render(request, 'orders/stripe_success.html', {'order': order})
                elif status in ('DECLINED', 'REJECTED', 'VOIDED', 'ERROR'):
                    messages.error(
                        request,
                        f'El pago fue rechazado (estado: {status}). '
                        f'Intenta con otro metodo de pago o contacta a tu banco.'
                    )
                    return redirect(f'/orders/{order.id}/?txn_id={txn_id or ""}&wompi_ref={wompi_ref or ""}')
                else:
                    # Estado PENDING u otro intermedio - pasar txn_id en URL para poder verificar despues
                    return redirect(f'/orders/{order.id}/?txn_id={txn_id or ""}&wompi_ref={wompi_ref or ""}')
            else:
                messages.error(
                    request,
                    f'No se pudo procesar el pago: {txn_result.get("error", "Error desconocido")}'
                )
                return redirect('order_show', pk=order.id)
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
            return redirect('order_show', pk=order.id)
        if not user_legal_id:
            messages.error(request, 'Debes ingresar tu numero de documento para PSE.')
            return redirect('order_show', pk=order.id)

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
def order_pay_pse(request, pk):
    """
    Iniciar pago PSE para una orden existente.
    Se usa cuando el usuario va a 'Mis Ordenes' y quiere pagar una orden pendiente.
    """
    order = get_order_usecases().get_order_by_id(pk)
    if not order:
        messages.error(request, 'Orden no encontrada.')
        return redirect('order_index')

    if order.user_id != request.user.id and not request.user.is_admin():
        messages.error(request, 'No tienes permiso.')
        return redirect('order_index')

    if order.status != OrderStatus.PENDING or order.payment_method != 'PSE':
        messages.info(request, 'Esta orden no requiere pago PSE.')
        return redirect('order_show', pk=pk)

    wompi_service = WompiService()
    if not wompi_service.is_configured():
        messages.error(request, 'Wompi no esta configurado. Contacta al administrador.')
        return redirect('order_show', pk=pk)

    # Datos del usuario para PSE (usar datos de la orden como fallback)
    from infrastructure.models.user_model import User
    try:
        user = User.objects.get(pk=order.user_id)
        user_email = user.email or ''
        user_name = user.name or ''
        user_phone = user.phone or ''
    except User.DoesNotExist:
        user_email = ''
        user_name = ''
        user_phone = ''

    result = wompi_service.create_pse_transaction(
        order=order,
        order_items=order.items,
        bank_code='1',  # Banco que aprueba (sandbox)
        user_type=0,
        user_legal_id='1098800000',
        user_legal_id_type='CC',
        customer_email=user_email,
        customer_name=user_name,
        customer_phone=user_phone or order.phone,
        bank_name='Banco que aprueba',
    )

    if result['success']:
        if result.get('redirect_url'):
            return redirect(result['redirect_url'])
        else:
            messages.warning(
                request,
                f'Transaccion creada en Wompi (ID: {result.get("transaction_id")}) '
                f'pero no devolvio URL de redireccion. Estado: {result.get("status")}.'
            )
            return redirect('order_show', pk=pk)
    else:
        messages.error(request, f'No se pudo iniciar PSE: {result.get("error", "Error desconocido")}')
        return redirect('order_show', pk=pk)


@login_required
def order_check_card_status(request, pk):
    """
    Verificar el estado de una transaccion con tarjeta Wompi.
    Se usa desde Mis Ordenes cuando el pago quedo en estado PENDING.
    """
    order = get_order_usecases().get_order_by_id(pk)
    if not order:
        messages.error(request, 'Orden no encontrada.')
        return redirect('order_index')

    if order.user_id != request.user.id and not request.user.is_admin():
        messages.error(request, 'No tienes permiso.')
        return redirect('order_index')

    transaction_id = request.GET.get('txn_id') or request.session.get('last_wompi_transaction_id')
    if not transaction_id:
        messages.info(request, 'No hay informacion de transaccion para verificar.')
        return redirect('order_show', pk=pk)

    wompi_service = WompiService()
    result = wompi_service.get_transaction_status(transaction_id)

    if result.get('success'):
        status = (result.get('status') or '').upper()
        if status in ('APPROVED', 'COMPLETED'):
            try:
                get_order_usecases().update_order_status(pk, OrderStatus.PROCESSING)
            except Exception:
                pass
            messages.success(request, f'Pago confirmado! Tu orden {order.order_number} esta en proceso.')
        elif status in ('DECLINED', 'REJECTED', 'VOIDED', 'ERROR'):
            messages.error(request, f'El pago fue rechazado (estado: {status}).')
        else:
            messages.info(request, f'El pago sigue en proceso (estado: {status}). Intenta mas tarde.')
    else:
        messages.error(request, f'No se pudo consultar el estado: {result.get("error")}')

    return redirect('order_show', pk=pk)


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

    # Metodo 1: extraer de reference (ANJOS-{order_number}-{timestamp})
    if reference.startswith('ANJOS-'):
        order_number = WompiService.extract_order_number_from_reference(reference)
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
                order_number = WompiService.extract_order_number_from_reference(ref)
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


# ---------------------------------------------------------------------------
# Comprobante / Recibo PDF de orden
# ---------------------------------------------------------------------------

_STATUS_ES = {
    'PENDING': 'Pendiente',
    'PROCESSING': 'En proceso',
    'SHIPPED': 'Enviado',
    'DELIVERED': 'Entregado',
    'CANCELLED': 'Cancelado',
}

_PAYMENT_ES = {
    'TARJETA': 'Tarjeta de crédito / débito',
    'PSE': 'PSE (Transferencia bancaria)',
    'EFECTIVO': 'Efectivo / Contra entrega',
}


def _status_es(value):
    return _STATUS_ES.get(value, value)


def _payment_es(value):
    return _PAYMENT_ES.get(value, value)


@login_required
def order_receipt_pdf(request, pk):
    """Genera y descarga el comprobante/recibo de una orden en PDF."""
    order = get_order_usecases().get_order_by_id(pk)
    if not order:
        messages.error(request, 'Orden no encontrada.')
        return redirect('order_index')
    if not request.user.is_admin() and order.user_id != request.user.id:
        messages.error(request, 'No tienes permiso para ver esta orden.')
        return redirect('order_index')

    user = get_user_usecases().get_user_by_id(order.user_id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        leftMargin=0.6*inch, rightMargin=0.6*inch,
        topMargin=0.6*inch, bottomMargin=0.6*inch,
    )
    elements = []
    styles = getSampleStyleSheet()

    gold = colors.HexColor('#C8A951')
    dark = colors.HexColor('#1a1a1a')
    soft = colors.HexColor('#f9f6f0')

    title_style = ParagraphStyle(
        'T', parent=styles['Heading1'],
        fontSize=20, textColor=gold, alignment=TA_CENTER, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'S', parent=styles['Normal'],
        fontSize=9, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=14,
    )
    section_style = ParagraphStyle(
        'Sec', parent=styles['Heading2'],
        fontSize=11, textColor=dark, spaceBefore=12, spaceAfter=6,
    )
    label_style = ParagraphStyle(
        'Lbl', parent=styles['Normal'],
        fontSize=9, textColor=colors.grey, spaceAfter=2,
    )
    value_style = ParagraphStyle(
        'Val', parent=styles['Normal'],
        fontSize=10, textColor=dark, spaceAfter=6,
    )
    right_style = ParagraphStyle(
        'R', parent=styles['Normal'],
        fontSize=10, textColor=dark, alignment=TA_RIGHT,
    )
    footer_style = ParagraphStyle(
        'F', parent=styles['Normal'],
        fontSize=8, textColor=colors.grey, alignment=TA_CENTER, spaceBefore=20,
    )

    # Header
    elements.append(Paragraph('ANJOS JEWELRY', title_style))
    elements.append(Paragraph('Comprobante de compra', subtitle_style))

    # Order info block
    order_data = [
        [Paragraph(f'<b>N° Pedido:</b> {order.order_number}', value_style),
         Paragraph(f'<b>Fecha:</b> {order.created_at.strftime("%d/%m/%Y %H:%M") if order.created_at else "N/A"}', right_style)],
        [Paragraph(f'<b>Estado:</b> {_status_es(order.status)}', value_style),
         Paragraph(f'<b>Método de pago:</b> {_payment_es(order.payment_method)}', right_style)],
    ]
    order_table = Table(order_data, colWidths=[doc.width/2, doc.width/2])
    order_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),
    ]))
    elements.append(order_table)
    elements.append(Spacer(1, 8))

    # Client info
    elements.append(Paragraph('Información del cliente', section_style))
    client_name = user.name if user else 'Cliente'
    client_email = user.email if user else ''
    client_phone = order.phone or (user.phone if user else '')
    client_address = order.shipping_address or (user.address if user else '')

    client_data = [
        [Paragraph('<b>Nombre:</b>', label_style), Paragraph(client_name, value_style)],
        [Paragraph('<b>Email:</b>', label_style), Paragraph(client_email, value_style)],
        [Paragraph('<b>Teléfono:</b>', label_style), Paragraph(str(client_phone) if client_phone else '—', value_style)],
        [Paragraph('<b>Dirección de envío:</b>', label_style), Paragraph(str(client_address) if client_address else '—', value_style)],
    ]
    client_table = Table(client_data, colWidths=[doc.width*0.28, doc.width*0.72])
    client_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 6))

    # Items table
    elements.append(Paragraph('Detalle de productos', section_style))

    item_header = [
        ['Producto', 'Ref.', 'Cant.', 'Precio unit.', 'Subtotal'],
    ]
    item_rows = []
    for item in order.items:
        item_rows.append([
            item.product_name or '',
            f'#{item.product_id}' if item.product_id else '—',
            str(item.quantity),
            f'${item.price:,.0f}',
            f'${item.subtotal:,.0f}',
        ])

    items_data = item_header + item_rows
    items_table = Table(items_data, colWidths=[doc.width*0.34, doc.width*0.14, doc.width*0.12, doc.width*0.20, doc.width*0.20])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), dark),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, soft]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 12))

    # Totals
    totals_data = [
        ['', '', '', 'Subtotal:', f'${order.subtotal:,.0f}'],
        ['', '', '', 'IVA (19%):', f'${order.tax:,.0f}'],
        ['', '', '', Paragraph('<b>Total:</b>', ParagraphStyle('Tot', parent=value_style, fontSize=11, textColor=dark, alignment=TA_RIGHT)),
         Paragraph(f'<b>${order.total:,.0f}</b>', ParagraphStyle('TotV', parent=right_style, fontSize=11, textColor=gold))],
    ]
    totals_table = Table(totals_data, colWidths=[doc.width*0.34, doc.width*0.14, doc.width*0.12, doc.width*0.20, doc.width*0.20])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (3, 0), (-1, 0), 0.5, colors.HexColor('#dddddd')),
        ('LINEABOVE', (3, 2), (-1, 2), 1.5, gold),
    ]))
    elements.append(totals_table)

    # Notes
    if order.notes:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph('Notas:', label_style))
        elements.append(Paragraph(str(order.notes), value_style))

    # Footer
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(
        'Gracias por tu compra. Para cualquier consulta escríbenos a soporte@anjos.com',
        footer_style,
    ))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Comprobante_{order.order_number}.pdf"'
    response.write(pdf)
    return response
