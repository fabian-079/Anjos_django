from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CategoryEntity:
    id: Optional[int] = None
    name: str = ''
    description: Optional[str] = None
    image: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
