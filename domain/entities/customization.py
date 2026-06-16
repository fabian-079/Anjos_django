from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class CustomizationEntity:
    id: Optional[int] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    jewelry_type: str = ''
    design: str = ''
    stones: str = ''
    finish: str = ''
    color: str = ''
    material: str = ''
    size: Optional[str] = None
    engraving: Optional[str] = None
    special_instructions: Optional[str] = None
    estimated_price: Optional[Decimal] = None
    status: str = 'pending'
    assigned_technician: Optional[str] = None
    cost_accepted: Optional[bool] = None
    client_counter_offer: Optional[Decimal] = None
    client_negotiation_note: Optional[str] = None
    admin_notes: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
