from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.favorite import FavoriteEntity


class FavoriteRepository(ABC):

    @abstractmethod
    def find_by_user(self, user_id: int) -> List[FavoriteEntity]:
        pass

    @abstractmethod
    def find_by_user_and_product(self, user_id: int, product_id: int) -> Optional[FavoriteEntity]:
        pass

    @abstractmethod
    def find_by_user_and_customization(self, user_id: int, customization_id: int) -> Optional[FavoriteEntity]:
        pass

    @abstractmethod
    def find_by_id(self, favorite_id: int) -> Optional[FavoriteEntity]:
        pass

    @abstractmethod
    def save(self, favorite: FavoriteEntity) -> FavoriteEntity:
        pass

    @abstractmethod
    def delete(self, favorite_id: int) -> None:
        pass

    @abstractmethod
    def exists_by_user_and_product(self, user_id: int, product_id: int) -> bool:
        pass

    @abstractmethod
    def exists_by_user_and_customization(self, user_id: int, customization_id: int) -> bool:
        pass
