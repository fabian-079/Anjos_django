from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.category import CategoryEntity


class CategoryRepository(ABC):

    @abstractmethod
    def find_all(self) -> List[CategoryEntity]:
        pass

    @abstractmethod
    def find_active(self) -> List[CategoryEntity]:
        pass

    @abstractmethod
    def find_by_id(self, category_id: int) -> Optional[CategoryEntity]:
        pass

    @abstractmethod
    def save(self, category: CategoryEntity) -> CategoryEntity:
        pass

    @abstractmethod
    def delete(self, category_id: int) -> None:
        pass
