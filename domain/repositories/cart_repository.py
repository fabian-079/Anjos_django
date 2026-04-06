from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.cart_item import CartItemEntity


class CartRepository(ABC):

    
    @abstractmethod
    def find_by_user(self, user_id: int) -> List[CartItemEntity]:
        pass

    @abstractmethod
    def find_by_user_and_product(self, user_id: int, product_id: int) -> Optional[CartItemEntity]:
        pass

    @abstractmethod
    def find_by_id(self, cart_item_id: int) -> Optional[CartItemEntity]:
        pass

    @abstractmethod
    def save(self, cart_item: CartItemEntity) -> CartItemEntity:
        pass

    @abstractmethod
    def delete(self, cart_item_id: int) -> None:
        pass

    @abstractmethod
    def clear_by_user(self, user_id: int) -> None:
        pass
