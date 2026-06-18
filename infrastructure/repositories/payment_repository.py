from typing import List, Optional
from datetime import datetime
from domain.payment import Payment, PaymentStatus

class PaymentRepository:
    def __init__(self):
        # En una implementación real, esto sería una base de datos
        self._payments = {}
    
    def save(self, payment: Payment) -> Payment:
        """Guardar un pago"""
        self._payments[payment.id] = payment
        return payment
    
    def get_by_id(self, payment_id: str) -> Optional[Payment]:
        """Obtener un pago por ID"""
        return self._payments.get(payment_id)
    
    def get_by_customer_email(self, customer_email: str) -> List[Payment]:
        """Obtener pagos por email del cliente"""
        return [
            payment for payment in self._payments.values()
            if payment.request.customer_email == customer_email
        ]
    
    def get_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Obtener pagos por estado"""
        return [
            payment for payment in self._payments.values()
            if payment.response.status == status
        ]
    
    def get_by_provider(self, provider: str) -> List[Payment]:
        """Obtener pagos por proveedor"""
        return [
            payment for payment in self._payments.values()
            if payment.provider == provider
        ]
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Payment]:
        """Obtener pagos por rango de fechas"""
        return [
            payment for payment in self._payments.values()
            if start_date <= payment.created_at <= end_date
        ]
    
    def update(self, payment: Payment) -> Payment:
        """Actualizar un pago"""
        self._payments[payment.id] = payment
        return payment
    
    def delete(self, payment_id: str) -> bool:
        """Eliminar un pago"""
        if payment_id in self._payments:
            del self._payments[payment_id]
            return True
        return False
    
    def list_all(self) -> List[Payment]:
        """Listar todos los pagos"""
        return list(self._payments.values())
    
    def count_by_status(self) -> dict:
        """Contar pagos por estado"""
        counts = {}
        for payment in self._payments.values():
            status = payment.response.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts
    
    def get_total_amount_by_status(self, status: PaymentStatus) -> float:
        """Obtener monto total por estado"""
        total = 0.0
        for payment in self._payments.values():
            if payment.response.status == status:
                total += payment.request.amount
        return total
