import stripe
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any
from django.conf import settings
from domain.payment import (
    PaymentRequest, PaymentResponse, Payment, 
    PaymentMethod, PaymentStatus, Currency
)

class PaymentService:
    def __init__(self):
        # Configurar Stripe
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
        
        # Configurar PayPal
        self.paypal_client_id = getattr(settings, 'PAYPAL_CLIENT_ID', None)
        self.paypal_client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', None)
        self.paypal_base_url = "https://api-m.sandbox.paypal.com"  # Cambiar a producción
        
        # Configurar Wompi
        self.wompi_public_key = getattr(settings, 'WOMPI_PUBLIC_KEY', None)
        self.wompi_private_key = getattr(settings, 'WOMPI_PRIVATE_KEY', None)
        self.wompi_base_url = "https://sandbox.wompi.co/v1"
    
    def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Crear pago según el método seleccionado"""
        if request.payment_method == PaymentMethod.STRIPE_CARD:
            return self._create_stripe_payment(request)
        elif request.payment_method == PaymentMethod.PAYPAL:
            return self._create_paypal_payment(request)
        elif request.payment_method == PaymentMethod.PSE:
            return self._create_wompi_pse_payment(request)
        elif request.payment_method == PaymentMethod.EFECTY:
            return self._create_wompi_efecty_payment(request)
        else:
            return PaymentResponse(
                payment_id="",
                status=PaymentStatus.FAILED,
                message="Método de pago no soportado"
            )
    
    def _create_stripe_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Crear pago con Stripe"""
        try:
            # Crear Checkout Session de Stripe
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': request.currency.value.lower(),
                        'product_data': {
                            'name': request.description,
                            'description': request.description,
                        },
                        'unit_amount': int(request.amount * 100), # Stripe usa centavos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.return_url or f"{settings.SITE_URL}/payment/success/",
                cancel_url=request.cancel_url or f"{settings.SITE_URL}/payment/cancel/",
                customer_email=request.customer_email,
                metadata=request.metadata or {}
            )
            
            return PaymentResponse(
                payment_id=checkout_session.id,
                status=PaymentStatus.PENDING,
                payment_url=checkout_session.url,
                provider_transaction_id=checkout_session.payment_intent,
                message="Pago Stripe creado exitosamente"
            )
            
        except Exception as e:
            return PaymentResponse(
                payment_id="",
                status=PaymentStatus.FAILED,
                message=f"Error creando pago Stripe: {str(e)}"
            )
    
    def _create_paypal_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Crear pago con PayPal"""
        try:
            # Obtener token de acceso PayPal
            auth_response = requests.post(
                f"{self.paypal_base_url}/v1/oauth2/token",
                headers={
                    "Accept": "application/json",
                    "Accept-Language": "en_US"
                },
                auth=(self.paypal_client_id, self.paypal_client_secret),
                data="grant_type=client_credentials"
            )
            
            if auth_response.status_code != 200:
                return PaymentResponse(
                    payment_id="",
                    status=PaymentStatus.FAILED,
                    message="Error autenticando PayPal"
                )
            
            access_token = auth_response.json()['access_token']
            
            # Crear orden PayPal
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "reference_id": f"ANJOS_{datetime.now().timestamp()}",
                    "description": request.description,
                    "amount": {
                        "currency_code": request.currency.value,
                        "value": str(request.amount)
                    },
                    "custom_id": request.customer_email
                }],
                "application_context": {
                    "return_url": request.return_url or f"{settings.SITE_URL}/payment/paypal/success/",
                    "cancel_url": request.cancel_url or f"{settings.SITE_URL}/payment/paypal/cancel/",
                    "brand_name": "ANJOS Jewelry",
                    "locale": "es-ES",
                    "landing_page": "BILLING",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "PAY_NOW"
                }
            }
            
            order_response = requests.post(
                f"{self.paypal_base_url}/v2/checkout/orders",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                json=order_data
            )
            
            if order_response.status_code != 201:
                return PaymentResponse(
                    payment_id="",
                    status=PaymentStatus.FAILED,
                    message="Error creando orden PayPal"
                )
            
            order_data = order_response.json()
            approval_url = None
            
            for link in order_data['links']:
                if link['rel'] == 'approve':
                    approval_url = link['href']
                    break
            
            return PaymentResponse(
                payment_id=order_data['id'],
                status=PaymentStatus.PENDING,
                payment_url=approval_url,
                provider_transaction_id=order_data['id'],
                message="Pago PayPal creado exitosamente"
            )
            
        except Exception as e:
            return PaymentResponse(
                payment_id="",
                status=PaymentStatus.FAILED,
                message=f"Error creando pago PayPal: {str(e)}"
            )
    
    def _create_wompi_pse_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Crear pago con PSE via Wompi"""
        try:
            # Obtener token de Wompi
            auth_response = requests.post(
                f"{self.wompi_base_url}/links/auth",
                json={
                    "public_key": self.wompi_public_key,
                    "private_key": self.wompi_private_key
                }
            )
            
            if auth_response.status_code != 200:
                return PaymentResponse(
                    payment_id="",
                    status=PaymentStatus.FAILED,
                    message="Error autenticando Wompi"
                )
            
            # Crear enlace de pago Wompi
            payment_link_data = {
                "name": request.description,
                "description": request.description,
                "single_use": True,
                "collect_shipping": False,
                "currency": request.currency.value,
                "amount_in_cents": int(request.amount * 100),  # Wompi usa centavos
                "redirect_url": request.return_url or f"{settings.SITE_URL}/payment/wompi/success/",
                "presets": [
                    {
                        "name": "PSE",
                        "type": "PSE"
                    }
                ]
            }
            
            link_response = requests.post(
                f"{self.wompi_base_url}/links",
                json=payment_link_data,
                headers={
                    "Authorization": f"Bearer {auth_response.json()['data']['presets']['token']}"
                }
            )
            
            if link_response.status_code != 201:
                return PaymentResponse(
                    payment_id="",
                    status=PaymentStatus.FAILED,
                    message="Error creando enlace Wompi"
                )
            
            link_data = link_response.json()['data']
            
            return PaymentResponse(
                payment_id=link_data['id'],
                status=PaymentStatus.PENDING,
                payment_url=link_data['url'],
                provider_transaction_id=link_data['id'],
                message="Pago PSE creado exitosamente"
            )
            
        except Exception as e:
            return PaymentResponse(
                payment_id="",
                status=PaymentStatus.FAILED,
                message=f"Error creando pago PSE: {str(e)}"
            )
    
    def _create_wompi_efecty_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Crear pago con Efecty via Wompi"""
        try:
            # Similar a PSE pero con preset de Efecty
            auth_response = requests.post(
                f"{self.wompi_base_url}/links/auth",
                json={
                    "public_key": self.wompi_public_key,
                    "private_key": self.wompi_private_key
                }
            )
            
            if auth_response.status_code != 200:
                return PaymentResponse(
                    payment_id="",
                    status=PaymentStatus.FAILED,
                    message="Error autenticando Wompi"
                )
            
            payment_link_data = {
                "name": request.description,
                "description": request.description,
                "single_use": True,
                "collect_shipping": False,
                "currency": request.currency.value,
                "amount_in_cents": int(request.amount * 100),
                "redirect_url": request.return_url or f"{settings.SITE_URL}/payment/wompi/success/",
                "presets": [
                    {
                        "name": "Efecty",
                        "type": "EFECTY"
                    }
                ]
            }
            
            link_response = requests.post(
                f"{self.wompi_base_url}/links",
                json=payment_link_data,
                headers={
                    "Authorization": f"Bearer {auth_response.json()['data']['presets']['token']}"
                }
            )
            
            if link_response.status_code != 201:
                return PaymentResponse(
                    payment_id="",
                    status=PaymentStatus.FAILED,
                    message="Error creando enlace Efecty"
                )
            
            link_data = link_response.json()['data']
            
            return PaymentResponse(
                payment_id=link_data['id'],
                status=PaymentStatus.PENDING,
                payment_url=link_data['url'],
                provider_transaction_id=link_data['id'],
                message="Pago Efecty creado exitosamente"
            )
            
        except Exception as e:
            return PaymentResponse(
                payment_id="",
                status=PaymentStatus.FAILED,
                message=f"Error creando pago Efecty: {str(e)}"
            )
    
    def get_payment_status(self, payment_id: str, provider: str) -> PaymentStatus:
        """Obtener estado de un pago"""
        # Implementar según el proveedor
        return PaymentStatus.PENDING

# Instancia global
payment_service = PaymentService()
