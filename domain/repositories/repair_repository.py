from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.repair import RepairEntity


class RepairRepository(ABC):

    @abstractmethod
    def find_all(self) -> List[RepairEntity]:
        pass

    @abstractmethod
    def find_by_id(self, repair_id: int) -> Optional[RepairEntity]:
        pass

    @abstractmethod
    def find_by_user(self, user_id: int) -> List[RepairEntity]:
        pass

    @abstractmethod
    def find_by_technician(self, technician_id: int) -> List[RepairEntity]:
        pass

    @abstractmethod
    def find_by_repair_number(self, repair_number: str) -> Optional[RepairEntity]:
        pass

    @abstractmethod
    def save(self, repair: RepairEntity) -> RepairEntity:
        pass

    @abstractmethod
    def delete(self, repair_id: int) -> None:
        pass
