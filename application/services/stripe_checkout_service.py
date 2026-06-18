"""
Servicio profesional de integración con Stripe Checkout.
Crea sesiones de checkout con datos reales de la orden.
"""
import stripe
from django.conf import settings
from decimal import Decimal


class StripeCheckoutService:
    """Servicio de Stripe Checkout para ANJOS Jewelry."""

    def __init__(self):
        self.secret_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        self.publishable_key = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
        self.webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        if self.secret_key:
            stripe.api_key = self.secret_key

    def is_configured(self) -> bool:
        """Verificar si Stripe tiene credenciales reales configuradas."""
        return bool(
            self.secret_key
            and self.secret_key.startswith('sk_')
            and self.publishable_key
            and self.publishable_key.startswith('pk_')
        )

    def get_publishable_key(self) -> str:
        return self.publishable_key

    def build_absolute_url(self, path: str) -> str:
        """Construir URL absoluta usando BASE_URL configurado."""
        base = getattr(settings, 'BASE_URL', '')
        if not base:
            base = 'https://anjosdjango-production.up.railway.app'
        base = base.rstrip('/')
        path = path.lstrip('/')
        return f"{base}/{path}"

    def create_checkout_session(self, order, order_items) -> dict:
        """
        Crear una sesión de Stripe Checkout a partir de una orden real.
        Retorna dict con: success, session_id, checkout_url, error
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Stripe no está configurado. Contacta al administrador.'
            }

        try:
            line_items = []
            for item in order_items:
                # Stripe usa centavos: $12.50 -> 1250
                unit_amount_cents = int(item.price * 100)
                product_image = None
                if item.product_image:
                    img = item.product_image
                    if img.startswith('http'):
                        product_image = img

                product_data = {
                    'name': item.product_name or 'Producto ANJOS',
                }
                if product_image:
                    product_data['images'] = [product_image]

                line_items.append({
                    'price_data': {
                        'currency': 'cop',
                        'product_data': product_data,
                        'unit_amount': unit_amount_cents,
                    },
                    'quantity': item.quantity,
                })

            success_url = self.build_absolute_url(f'/orders/stripe/success/?order_id={order.id}')
            cancel_url = self.build_absolute_url(f'/orders/stripe/cancel/?order_id={order.id}')

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                    'user_id': str(order.user_id) if order.user_id else '',
                    'source': 'ANJOS_Website',
                },
                billing_address_collection='required',
                shipping_address_collection={
                    'allowed_countries': ['CO'],
                },
                phone_number_collection={'enabled': True},
            )

            return {
                'success': True,
                'session_id': session.id,
                'checkout_url': session.url,
            }

        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': f'Error de Stripe: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }

    def construct_webhook_event(self, payload: bytes, sig_header: str):
        """Verificar y construir evento de webhook de Stripe."""
        if not self.webhook_secret:
            # Si no hay webhook secret configurado, parseamos sin verificar
            import json
            return json.loads(payload)
        return stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)
