from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class PaymentMethod(Enum):
    STRIPE_CARD = "stripe_card"
    PAYPAL = "paypal"
    PSE = "pse"
    EFECTY = "efecty"
    NEQUI = "nequi"
    BANCOLOMBIA_TRANSFER = "bancolombia_transfer"

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Currency(Enum):
    COP = "COP"
    USD = "USD"
    EUR = "EUR"

@dataclass
class PaymentItem:
    name: str
    description: str
    quantity: int
    unit_price: float
    total_price: float

@dataclass
class PaymentRequest:
    amount: float
    currency: Currency
    description: str
    items: list[PaymentItem]
    customer_email: str
    customer_name: str
    customer_phone: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PaymentResponse:
    payment_id: str
    status: PaymentStatus
    payment_url: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Payment:
    id: str
    request: PaymentRequest
    response: PaymentResponse
    created_at: datetime
    updated_at: datetime
    provider: str
    provider_payment_id: Optional[str] = None
    failure_reason: Optional[str] = None
