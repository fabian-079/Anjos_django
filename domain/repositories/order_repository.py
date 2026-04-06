from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.order import OrderEntity


class OrderRepository(ABC):

    @abstractmethod
    def find_all(self) -> List[OrderEntity]:
        pass

    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[OrderEntity]:
        pass

    @abstractmethod
    def find_by_user(self, user_id: int) -> List[OrderEntity]:
        pass

    @abstractmethod
    def find_by_order_number(self, order_number: str) -> Optional[OrderEntity]:
        pass

    @abstractmethod
    def save(self, order: OrderEntity) -> OrderEntity:
        pass

    @abstractmethod
    def delete(self, order_id: int) -> None:
        pass
