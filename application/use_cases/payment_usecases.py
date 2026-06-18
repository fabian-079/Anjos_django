from typing import List, Optional
from datetime import datetime
from infrastructure.repositories.payment_repository import PaymentRepository
from application.services.payment_service import payment_service
from domain.payment import (
    PaymentRequest, PaymentResponse, Payment, 
    PaymentMethod, PaymentStatus, Currency, PaymentItem
)

class PaymentUseCases:
    def __init__(self, payment_repo: PaymentRepository):
        self._payment_repo = payment_repo
    
    def create_payment_request(self, 
                             amount: float,
                             description: str,
                             customer_email: str,
                             customer_name: str,
                             items: List[dict],
                             payment_method: PaymentMethod,
                             currency: Currency = Currency.COP,
                             customer_phone: Optional[str] = None,
                             return_url: Optional[str] = None,
                             cancel_url: Optional[str] = None,
                             metadata: Optional[dict] = None) -> PaymentResponse:
        """Crear una solicitud de pago"""
        
        # Convertir items a PaymentItem
        payment_items = []
        for item in items:
            payment_items.append(PaymentItem(
                name=item['name'],
                description=item.get('description', ''),
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total_price=item['unit_price'] * item['quantity']
            ))
        
        # Crear PaymentRequest
        request = PaymentRequest(
            amount=amount,
            currency=currency,
            description=description,
            items=payment_items,
            customer_email=customer_email,
            customer_name=customer_name,
            customer_phone=customer_phone,
            payment_method=payment_method,
            return_url=return_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        # Procesar pago con el servicio
        response = payment_service.create_payment(request)
        
        # Guardar en base de datos
        payment = Payment(
            id=response.payment_id,
            request=request,
            response=response,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            provider=self._get_provider_name(payment_method),
            provider_payment_id=response.provider_transaction_id
        )
        
        self._payment_repo.save(payment)
        
        return response
    
    def get_payment_status(self, payment_id: str) -> Optional[Payment]:
        """Obtener estado de un pago"""
        return self._payment_repo.get_by_id(payment_id)
    
    def update_payment_status(self, payment_id: str, status: PaymentStatus, 
                            provider_transaction_id: Optional[str] = None,
                            failure_reason: Optional[str] = None) -> bool:
        """Actualizar estado de un pago"""
        payment = self._payment_repo.get_by_id(payment_id)
        if not payment:
            return False
        
        payment.response.status = status
        payment.updated_at = datetime.now()
        
        if provider_transaction_id:
            payment.provider_payment_id = provider_transaction_id
        
        if failure_reason:
            payment.failure_reason = failure_reason
        
        self._payment_repo.update(payment)
        return True
    
    def get_customer_payments(self, customer_email: str) -> List[Payment]:
        """Obtener todos los pagos de un cliente"""
        return self._payment_repo.get_by_customer_email(customer_email)
    
    def get_payments_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Obtener pagos por estado"""
        return self._payment_repo.get_by_status(status)
    
    def refund_payment(self, payment_id: str) -> bool:
        """Reembolsar un pago"""
        payment = self._payment_repo.get_by_id(payment_id)
        if not payment or payment.response.status != PaymentStatus.COMPLETED:
            return False
        
        # Implementar lógica de reembolso según el proveedor
        # Por ahora solo actualizamos el estado
        return self.update_payment_status(payment_id, PaymentStatus.REFUNDED)
    
    def _get_provider_name(self, payment_method: PaymentMethod) -> str:
        """Obtener nombre del proveedor según el método de pago"""
        provider_mapping = {
            PaymentMethod.STRIPE_CARD: "stripe",
            PaymentMethod.PAYPAL: "paypal",
            PaymentMethod.PSE: "wompi",
            PaymentMethod.EFECTY: "wompi",
            PaymentMethod.NEQUI: "wompi",
            PaymentMethod.BANCOLOMBIA_TRANSFER: "wompi"
        }
        return provider_mapping.get(payment_method, "unknown")
    
    def get_payment_methods_available(self) -> List[dict]:
        """Obtener métodos de pago disponibles"""
        return [
            {
                "id": PaymentMethod.STRIPE_CARD.value,
                "name": "Tarjeta de Crédito/Débito",
                "description": "Visa, Mastercard, American Express",
                "icon": "credit-card",
                "enabled": True
            },
            {
                "id": PaymentMethod.PAYPAL.value,
                "name": "PayPal",
                "description": "Pago seguro con PayPal",
                "icon": "paypal",
                "enabled": True
            },
            {
                "id": PaymentMethod.PSE.value,
                "name": "PSE",
                "description": "Pago electrónico desde tu cuenta bancaria",
                "icon": "bank",
                "enabled": True
            },
            {
                "id": PaymentMethod.EFECTY.value,
                "name": "Efecty",
                "description": "Paga en efectivo en puntos autorizados",
                "icon": "money-bill",
                "enabled": True
            },
            {
                "id": PaymentMethod.NEQUI.value,
                "name": "Nequi",
                "description": "Pago desde tu cuenta Nequi",
                "icon": "mobile",
                "enabled": False  # Puede habilitarse más tarde
            },
            {
                "id": PaymentMethod.BANCOLOMBIA_TRANSFER.value,
                "name": "Transferencia Bancolombia",
                "description": "Transferencia desde Bancolombia",
                "icon": "exchange-alt",
                "enabled": False  # Puede habilitarse más tarde
            }
        ]
