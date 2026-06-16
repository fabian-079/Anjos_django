from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional
from domain.entities.product import ProductEntity


class ProductRepository(ABC):

    @abstractmethod
    def find_all(self) -> List[ProductEntity]:
        pass

    @abstractmethod
    def find_by_id(self, product_id: int) -> Optional[ProductEntity]:
        pass

    @abstractmethod
    def find_by_category(self, category_id: int) -> List[ProductEntity]:
        pass

    @abstractmethod
    def find_featured(self) -> List[ProductEntity]:
        pass

    @abstractmethod
    def search(self, category_id=None, material=None, color=None,
               finish=None, stones=None, min_price=None, max_price=None,
               search=None, page=1, page_size=12):
        pass

    @abstractmethod
    def save(self, product: ProductEntity) -> ProductEntity:
        pass

    @abstractmethod
    def delete(self, product_id: int) -> None:
        pass

    @abstractmethod
    def find_related(self, category_id: int, product_id: int, limit: int) -> List[ProductEntity]:
        pass

    @abstractmethod
    def find_distinct_materials(self) -> List[str]:
        pass

    @abstractmethod
    def find_distinct_colors(self) -> List[str]:
        pass

    @abstractmethod
    def find_distinct_finishes(self) -> List[str]:
        pass

    @abstractmethod
    def find_distinct_stones(self) -> List[str]:
        pass
