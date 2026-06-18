import stripe
from django.conf import settings
from django.http import JsonResponse
import json

class StripeService:
    """Servicio de Stripe seguro y funcional"""
    
    def __init__(self):
        # Configurar Stripe con las claves
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
        self.publishable_key = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
    
    def create_checkout_session(self, cart_items, total_amount, user_email, success_url, cancel_url):
        """Crear una sesión de checkout de Stripe"""
        try:
            # Convertir items al formato de Stripe
            line_items = []
            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'cop',  # Pesos colombianos
                        'product_data': {
                            'name': item['name'],
                            'description': f'Producto ANJOS - {item["name"]}',
                            'images': [item.get('image', '/static/images/logo.png')]
                        },
                        'unit_amount': int(item['price'] * 100),  # Stripe usa centavos
                    },
                    'quantity': item['quantity'],
                })
            
            # Asegurar URLs absolutas y válidas
            if not success_url.startswith('http'):
                success_url = f'https://anjosdjango-production.up.railway.app{success_url}'
            if not cancel_url.startswith('http'):
                cancel_url = f'https://anjosdjango-production.up.railway.app{cancel_url}'
            
            # Crear la sesión de checkout
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user_email,
                metadata={
                    'user_id': str(user_email) if user_email else 'guest',
                    'source': 'ANJOS Website'
                },
                billing_address_collection='required',
                shipping_address_collection={
                    'allowed_countries': ['CO', 'US'],  # Colombia y Estados Unidos
                }
            )
            
            return {
                'success': True,
                'session_id': session.id,
                'checkout_url': session.url
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': f'Error de Stripe: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error general: {str(e)}'
            }
    
    def get_publishable_key(self):
        """Obtener la clave publicable de Stripe"""
        return self.publishable_key
    
    def is_configured(self):
        """Verificar si Stripe está configurado"""
        return bool(stripe.api_key and self.publishable_key)

# Instancia global
stripe_service = StripeService()
