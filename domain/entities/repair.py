from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


class RepairStatus:
    PENDING = 'PENDING'
    QUOTED = 'QUOTED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

    CHOICES = [
        (PENDING, 'Pendiente'),
        (QUOTED, 'Cotizado'),
        (IN_PROGRESS, 'En proceso'),
        (COMPLETED, 'Completado'),
        (CANCELLED, 'Cancelado'),
    ]


@dataclass
class RepairEntity:
    id: Optional[int] = None
    repair_number: Optional[str] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    customer_name: str = ''
    description: str = ''
    phone: str = ''
    image: Optional[str] = None
    status: str = RepairStatus.PENDING
    assigned_technician_id: Optional[int] = None
    assigned_technician_name: Optional[str] = None
    assigned_technician_text: Optional[str] = None
    cost_accepted: Optional[bool] = None
    client_counter_offer: Optional[Decimal] = None
    client_negotiation_note: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    technician_notes: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
