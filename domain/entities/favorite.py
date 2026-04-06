from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FavoriteEntity:
    id: Optional[int] = None
    user_id: Optional[int] = None
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    product_price: Optional[float] = None
    product_category_name: Optional[str] = None
    customization_id: Optional[int] = None
    created_at: Optional[datetime] = None
