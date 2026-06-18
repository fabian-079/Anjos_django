from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from application.services.stripe_service import stripe_service

@login_required
def simple_checkout_view(request):
    """Checkout ultra-simple que funciona sin dependencias"""
    if request.method == 'POST':
        # Simular procesamiento de pago
        messages.success(request, '¡Pedido procesado exitosamente! (Modo simulado)')
        return redirect('simple_payment_success')
    
    # Obtener datos del carrito
    cart_items = request.session.get('cart', [])
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    
    return render(request, 'simple_checkout.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'user': request.user
    })

def simple_payment_success_view(request):
    """Página de éxito simple"""
    return render(request, 'simple_success.html')

def simple_buy_now_ajax(request):
    """API simple para Comprar Ahora"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            
            # Agregar al carrito de sesión
            cart = request.session.get('cart', [])
            
            # Simular producto (en caso real, obtener de BD)
            cart.append({
                'id': product_id,
                'name': f'Producto {product_id}',
                'price': 100000,  # Precio simulado
                'quantity': quantity,
                'image': '/static/images/product-placeholder.jpg'
            })
            
            request.session['cart'] = cart
            request.session.modified = True
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@require_http_methods(["POST"])
def create_stripe_checkout(request):
    """API para crear sesión de checkout de Stripe"""
    try:
        data = json.loads(request.body)
        cart_items = data.get('cart_items', [])
        total_amount = data.get('total_amount', 0)
        user_email = data.get('user_email', '')
        
        # Verificar que Stripe esté configurado
        if not stripe_service.is_configured():
            return JsonResponse({
                'success': False,
                'error': 'Stripe no está configurado. Contacta al administrador.'
            })
        
        # Crear URLs de retorno
        success_url = request.build_absolute_uri('/payment/success/')
        cancel_url = request.build_absolute_uri('/checkout/')
        
        # Crear sesión de Stripe
        result = stripe_service.create_checkout_session(
            cart_items=cart_items,
            total_amount=total_amount,
            user_email=user_email,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'session_id': result['session_id'],
                'checkout_url': result['checkout_url']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos inválidos'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error del servidor: {str(e)}'
        })
