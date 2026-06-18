from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json

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
