from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.user import UserEntity


class UserRepository(ABC):

    @abstractmethod
    def find_all(self) -> List[UserEntity]:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def save(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        pass

    @abstractmethod
    def find_admins(self) -> List[UserEntity]:
        pass
