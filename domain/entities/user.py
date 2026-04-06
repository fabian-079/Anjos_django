from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class UserEntity:
    id: Optional[int] = None
    name: str = ''
    email: str = ''
    password: str = ''
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True
    email_verified_at: Optional[datetime] = None
    roles: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    

    def is_admin(self) -> bool:
        return 'admin' in [r.lower() for r in self.roles]

    def is_client(self) -> bool:
        return 'cliente' in [r.lower() for r in self.roles]
