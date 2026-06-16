from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class NotificationType:
    PRICE_UPDATE = 'PRICE_UPDATE'
    CUSTOMIZATION_UPDATE = 'CUSTOMIZATION_UPDATE'
    STATUS_CHANGE = 'STATUS_CHANGE'
    NEW_CUSTOMIZATION = 'NEW_CUSTOMIZATION'
    NEW_REPAIR = 'NEW_REPAIR'
    REPAIR_UPDATE = 'REPAIR_UPDATE'
    REPAIR_STATUS_CHANGE = 'REPAIR_STATUS_CHANGE'
    NEW_ORDER = 'NEW_ORDER'
    ORDER_STATUS_CHANGE = 'ORDER_STATUS_CHANGE'

    CHOICES = [
        (PRICE_UPDATE, 'Actualización de precio'),
        (CUSTOMIZATION_UPDATE, 'Actualización de personalización'),
        (STATUS_CHANGE, 'Cambio de estado'),
        (NEW_CUSTOMIZATION, 'Nueva personalización'),
        (NEW_REPAIR, 'Nueva reparación'),
        (REPAIR_UPDATE, 'Actualización de reparación'),
        (REPAIR_STATUS_CHANGE, 'Cambio de estado de reparación'),
        (NEW_ORDER, 'Nueva orden'),
        (ORDER_STATUS_CHANGE, 'Cambio de estado de orden'),
    ]


@dataclass
class NotificationEntity:
    id: Optional[int] = None
    user_id: Optional[int] = None
    customization_id: Optional[int] = None
    repair_id: Optional[int] = None
    order_id: Optional[int] = None
    message: str = ''
    is_read: bool = False
    notification_type: str = NotificationType.NEW_ORDER
    created_at: Optional[datetime] = None
