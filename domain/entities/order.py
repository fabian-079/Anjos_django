from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


class OrderStatus:
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    SHIPPED = 'SHIPPED'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'

    CHOICES = [
        (PENDING, 'Pendiente'),
        (PROCESSING, 'En proceso'),
        (SHIPPED, 'Enviado'),
        (DELIVERED, 'Entregado'),
        (CANCELLED, 'Cancelado'),
    ]


class PaymentMethod:
    TARJETA = 'TARJETA'
    PSE = 'PSE'
    EFECTIVO = 'EFECTIVO'

    CHOICES = [
        (TARJETA, 'Tarjeta'),
        (PSE, 'PSE'),
        (EFECTIVO, 'Efectivo'),
    ]


@dataclass
class OrderItemEntity:
    id: Optional[int] = None
    order_id: Optional[int] = None
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    quantity: int = 1
    price: Decimal = Decimal('0.00')
    created_at: Optional[datetime] = None

    @property
    def subtotal(self) -> Decimal:
        return self.price * self.quantity


@dataclass
class OrderEntity:
    id: Optional[int] = None
    order_number: Optional[str] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    subtotal: Decimal = Decimal('0.00')
    tax: Decimal = Decimal('0.00')
    total: Decimal = Decimal('0.00')
    status: str = OrderStatus.PENDING
    shipping_address: str = ''
    billing_address: str = ''
    phone: Optional[str] = None
    payment_method: str = PaymentMethod.TARJETA
    notes: Optional[str] = None
    is_active: bool = True
    items: List[OrderItemEntity] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
