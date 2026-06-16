from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.customization import CustomizationEntity


class CustomizationRepository(ABC):

    @abstractmethod
    def find_all(self) -> List[CustomizationEntity]:
        pass

    @abstractmethod
    def find_by_id(self, customization_id: int) -> Optional[CustomizationEntity]:
        pass

    @abstractmethod
    def find_by_user(self, user_id: int) -> List[CustomizationEntity]:
        pass

    @abstractmethod
    def save(self, customization: CustomizationEntity) -> CustomizationEntity:
        pass

    @abstractmethod
    def delete(self, customization_id: int) -> None:
        pass
