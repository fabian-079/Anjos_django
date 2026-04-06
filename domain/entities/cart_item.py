from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class CartItemEntity:
    id: Optional[int] = None
    user_id: Optional[int] = None
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    product_price: Decimal = Decimal('0.00')
    product_image: Optional[str] = None
    quantity: int = 1
    created_at: Optional[datetime] = None

    @property
    def subtotal(self) -> Decimal:
        return self.product_price * self.quantity
