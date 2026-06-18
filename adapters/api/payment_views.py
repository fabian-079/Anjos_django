from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from decimal import Decimal

from adapters.api.decorators import admin_required
from infrastructure.container import get_payment_usecases
from domain.payment import PaymentMethod, PaymentStatus, Currency

def get_payment_usecases():
    from infrastructure.container import get_payment_usecases
    return get_payment_usecases()

def payment_methods_view(request):
    """Vista para mostrar métodos de pago disponibles"""
    payment_uc = get_payment_usecases()
    methods = payment_uc.get_payment_methods_available()
    
    return render(request, 'payments/methods.html', {
        'payment_methods': methods
    })

def payment_checkout_view(request):
    """Vista principal de checkout"""
    if request.method == 'POST':
        return create_payment(request)
    
    # Obtener datos del carrito o producto
    cart_items = request.session.get('cart', [])
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    
    payment_uc = get_payment_usecases()
    methods = payment_uc.get_payment_methods_available()
    
    return render(request, 'payments/checkout.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'payment_methods': methods,
        'user': request.user
    })

def create_payment(request):
    """Crear un nuevo pago"""
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        # Validar datos
        required_fields = ['amount', 'description', 'payment_method']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Campo {field} requerido'}, status=400)
        
        # Obtener items del carrito
        cart_items = request.session.get('cart', [])
        if not cart_items:
            return JsonResponse({'error': 'Carrito vacío'}, status=400)
        
        payment_uc = get_payment_usecases()
        
        # Crear pago
        response = payment_uc.create_payment_request(
            amount=float(data['amount']),
            description=data['description'],
            customer_email=request.user.email,
            customer_name=request.user.get_full_name() or request.user.username,
            items=cart_items,
            payment_method=PaymentMethod(data['payment_method']),
            currency=Currency.COP,  # Por defecto pesos colombianos
            customer_phone=data.get('phone'),
            return_url=request.build_absolute_uri('/payment/success/'),
            cancel_url=request.build_absolute_uri('/payment/cancel/'),
            metadata={'user_id': request.user.id}
        )
        
        if response.status == PaymentStatus.FAILED:
            return JsonResponse({
                'error': response.message,
                'status': 'failed'
            }, status=400)
        
        # Si es una API request, devolver JSON
        if request.content_type == 'application/json':
            return JsonResponse({
                'payment_id': response.payment_id,
                'payment_url': response.payment_url,
                'status': response.status.value,
                'message': response.message
            })
        
        # Si es formulario, redirigir a URL de pago
        if response.payment_url:
            return redirect(response.payment_url)
        
        return redirect('payment_pending')
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def payment_success_view(request):
    """Vista de pago exitoso"""
    payment_id = request.GET.get('payment_id') or request.session.get('last_payment_id')
    
    if not payment_id:
        messages.error(request, 'No se encontró información del pago')
        return redirect('home')
    
    payment_uc = get_payment_usecases()
    payment = payment_uc.get_payment_status(payment_id)
    
    if not payment:
        messages.error(request, 'Pago no encontrado')
        return redirect('home')
    
    # Actualizar estado si es necesario
    if payment.response.status != PaymentStatus.COMPLETED:
        # Aquí se verificaría el estado real con el proveedor
        pass
    
    # Limpiar carrito
    request.session['cart'] = []
    request.session.modified = True
    
    return render(request, 'payments/success.html', {
        'payment': payment
    })

def payment_cancel_view(request):
    """Vista de pago cancelado"""
    payment_id = request.GET.get('payment_id') or request.session.get('last_payment_id')
    
    if payment_id:
        payment_uc = get_payment_usecases()
        payment_uc.update_payment_status(payment_id, PaymentStatus.CANCELLED)
    
    messages.warning(request, 'Pago cancelado. Puedes intentar nuevamente.')
    return redirect('payment_checkout')

def payment_pending_view(request):
    """Vista de pago pendiente"""
    payment_id = request.session.get('last_payment_id')
    
    if not payment_id:
        return redirect('home')
    
    payment_uc = get_payment_usecases()
    payment = payment_uc.get_payment_status(payment_id)
    
    return render(request, 'payments/pending.html', {
        'payment': payment
    })

@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook_stripe(request):
    """Webhook de Stripe"""
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        # Verificar webhook (implementar con clave de Stripe)
        # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        
        data = json.loads(payload)
        event_type = data.get('type')
        
        payment_uc = get_payment_usecases()
        
        if event_type == 'checkout.session.completed':
            session = data['data']['object']
            payment_uc.update_payment_status(
                session.id,
                PaymentStatus.COMPLETED,
                provider_transaction_id=session.payment_intent
            )
        elif event_type == 'checkout.session.expired':
            session = data['data']['object']
            payment_uc.update_payment_status(
                session.id,
                PaymentStatus.CANCELLED,
                failure_reason='Sesión expirada'
            )
        
        return HttpResponse(status=200)
        
    except Exception as e:
        return HttpResponse(status=400)

@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook_paypal(request):
    """Webhook de PayPal"""
    try:
        data = json.loads(request.body)
        event_type = data.get('event_type')
        
        payment_uc = get_payment_usecases()
        
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            resource = data['resource']
            payment_uc.update_payment_status(
                resource['id'],
                PaymentStatus.COMPLETED
            )
        elif event_type == 'PAYMENT.CAPTURE.DENIED':
            resource = data['resource']
            payment_uc.update_payment_status(
                resource['id'],
                PaymentStatus.FAILED,
                failure_reason='Pago denegado'
            )
        
        return HttpResponse(status=200)
        
    except Exception as e:
        return HttpResponse(status=400)

@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook_wompi(request):
    """Webhook de Wompi"""
    try:
        data = json.loads(request.body)
        
        # Verificar firma de Wompi (implementar)
        
        event = data.get('event')
        transaction = data.get('data', {}).get('transaction')
        
        if transaction:
            payment_uc = get_payment_usecases()
            payment_id = transaction.get('reference')
            
            if event == 'transaction.updated':
                status_mapping = {
                    'APPROVED': PaymentStatus.COMPLETED,
                    'DECLINED': PaymentStatus.FAILED,
                    'ERROR': PaymentStatus.FAILED,
                    'VOIDED': PaymentStatus.CANCELLED
                }
                
                wompi_status = transaction.get('status')
                payment_status = status_mapping.get(wompi_status, PaymentStatus.PENDING)
                
                failure_reason = None
                if payment_status == PaymentStatus.FAILED:
                    failure_reason = transaction.get('status_message', 'Error en transacción')
                
                payment_uc.update_payment_status(
                    payment_id,
                    payment_status,
                    provider_transaction_id=transaction.get('id'),
                    failure_reason=failure_reason
                )
        
        return HttpResponse(status=200)
        
    except Exception as e:
        return HttpResponse(status=400)

@login_required
def payment_history_view(request):
    """Historial de pagos del usuario"""
    payment_uc = get_payment_usecases()
    payments = payment_uc.get_customer_payments(request.user.email)
    
    return render(request, 'payments/history.html', {
        'payments': payments
    })

@admin_required
def payment_admin_view(request):
    """Dashboard de administración de pagos"""
    payment_uc = get_payment_usecases()
    
    # Estadísticas
    all_payments = payment_uc._payment_repo.list_all()
    
    stats = {
        'total_payments': len(all_payments),
        'completed': len([p for p in all_payments if p.response.status == PaymentStatus.COMPLETED]),
        'pending': len([p for p in all_payments if p.response.status == PaymentStatus.PENDING]),
        'failed': len([p for p in all_payments if p.response.status == PaymentStatus.FAILED]),
        'total_amount': sum(p.request.amount for p in all_payments if p.response.status == PaymentStatus.COMPLETED)
    }
    
    return render(request, 'payments/admin.html', {
        'stats': stats,
        'payments': all_payments[-20:]  # Últimos 20 pagos
    })

def add_to_cart_view(request):
    """Agregar producto al carrito"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            product = {
                'id': data['id'],
                'name': data['name'],
                'price': float(data['price']),
                'quantity': int(data['quantity']),
                'image': data.get('image', '')
            }
            
            cart = request.session.get('cart', [])
            
            # Verificar si el producto ya está en el carrito
            for item in cart:
                if item['id'] == product['id']:
                    item['quantity'] += product['quantity']
                    break
            else:
                cart.append(product)
            
            request.session['cart'] = cart
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'cart_count': len(cart),
                'cart_total': sum(item['price'] * item['quantity'] for item in cart)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def get_cart_view(request):
    """Obtener carrito actual"""
    cart = request.session.get('cart', [])
    
    return JsonResponse({
        'items': cart,
        'count': len(cart),
        'total': sum(item['price'] * item['quantity'] for item in cart)
    })

def clear_cart_view(request):
    """Limpiar carrito"""
    request.session['cart'] = []
    request.session.modified = True
    
    return JsonResponse({'success': True})
