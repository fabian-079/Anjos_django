from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from adapters.api.decorators import admin_required
from infrastructure.container import get_webservice_usecases
from decimal import Decimal


@login_required
def webservice_dashboard(request):
    """Dashboard de servicios web disponibles"""
    return render(request, 'webservices/dashboard.html')


@login_required
@require_http_methods(["GET"])
def api_exchange_rates(request):
    """Obtener tasas de cambio actuales"""
    ws_uc = get_webservice_usecases()
    base_currency = request.GET.get('base', 'USD')
    
    rates = ws_uc.get_exchange_rates(base_currency)
    
    if rates:
        return JsonResponse({
            'success': True,
            'data': rates
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'No se pudieron obtener las tasas de cambio'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_convert_currency(request):
    """Convertir moneda"""
    ws_uc = get_webservice_usecases()
    
    try:
        amount = Decimal(request.GET.get('amount', '0'))
        from_currency = request.GET.get('from', 'USD')
        to_currency = request.GET.get('to', 'COP')
        
        converted = ws_uc.convert_currency(amount, from_currency, to_currency)
        
        if converted:
            return JsonResponse({
                'success': True,
                'data': {
                    'original_amount': float(amount),
                    'original_currency': from_currency,
                    'converted_amount': float(converted),
                    'target_currency': to_currency
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No se pudo realizar la conversión'
            }, status=400)
    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Parámetros inválidos: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["GET"])
def api_gold_price(request):
    """Obtener precio actual del oro"""
    ws_uc = get_webservice_usecases()
    gold_data = ws_uc.get_gold_price()
    
    if gold_data:
        return JsonResponse({
            'success': True,
            'data': gold_data
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'No se pudo obtener el precio del oro'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_location_info(request):
    """Obtener información de ubicación"""
    ws_uc = get_webservice_usecases()
    ip_address = request.GET.get('ip')
    
    location_data = ws_uc.get_location_info(ip_address)
    
    if location_data:
        return JsonResponse({
            'success': True,
            'data': location_data
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'No se pudo obtener información de ubicación'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_calculate_shipping(request):
    """Calcular costo de envío"""
    ws_uc = get_webservice_usecases()
    
    try:
        origin = request.POST.get('origin', 'Bogotá')
        destination = request.POST.get('destination', 'Medellín')
        weight = float(request.POST.get('weight', '1.0'))
        
        shipping_data = ws_uc.get_shipping_cost(origin, destination, weight)
        
        return JsonResponse({
            'success': True,
            'data': shipping_data
        })
    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Parámetros inválidos: {str(e)}'
        }, status=400)


@admin_required
def webservice_test_page(request):
    """Página de prueba de servicios web"""
    ws_uc = get_webservice_usecases()
    
    # Obtener datos de ejemplo
    exchange_rates = ws_uc.get_exchange_rates('USD')
    gold_price = ws_uc.get_gold_price()
    
    context = {
        'exchange_rates': exchange_rates,
        'gold_price': gold_price,
    }
    
    return render(request, 'webservices/test.html', context)


@login_required
@require_http_methods(["GET"])
def api_weather_info(request):
    """Obtener información del clima"""
    ws_uc = get_webservice_usecases()
    city = request.GET.get('city', 'Bogota')
    
    weather_data = ws_uc.get_weather_info(city)
    
    if weather_data:
        return JsonResponse({
            'success': True,
            'data': weather_data
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'No se pudo obtener información del clima'
        }, status=500)
