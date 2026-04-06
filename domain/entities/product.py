from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class ProductEntity:
    id: Optional[int] = None
    name: str = ''
    description: str = ''
    price: Decimal = Decimal('0.00')
    stock: int = 0
    material: Optional[str] = None
    color: Optional[str] = None
    finish: Optional[str] = None
    stones: Optional[str] = None
    size: Optional[str] = None
    image: Optional[str] = None
    gallery: Optional[str] = None
    is_featured: bool = False
    is_active: bool = True
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def get_image_url(self) -> str:
        if self.image:
            if self.image.startswith('http'):
                return self.image
            return self.image
        if self.category_name:
            cat = self.category_name.lower()
            if 'anillo' in cat:
                return 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&h=800&fit=crop'
            elif 'collar' in cat:
                return 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&h=800&fit=crop'
            elif 'pulsera' in cat:
                return 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&h=800&fit=crop'
            elif 'arete' in cat:
                return 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&h=800&fit=crop'
            elif 'reloj' in cat:
                return 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=800&fit=crop'
            elif 'dije' in cat:
                return 'https://images.unsplash.com/photo-1603561596111-7c8cd67663aa?w=800&h=800&fit=crop'
        return 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&h=800&fit=crop'
