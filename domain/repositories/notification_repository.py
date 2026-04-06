from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.notification import NotificationEntity


class NotificationRepository(ABC):

    @abstractmethod
    def find_by_user(self, user_id: int) -> List[NotificationEntity]:
        pass

    @abstractmethod
    def find_unread_by_user(self, user_id: int) -> List[NotificationEntity]:
        pass

    @abstractmethod
    def count_unread_by_user(self, user_id: int) -> int:
        pass

    @abstractmethod
    def save(self, notification: NotificationEntity) -> NotificationEntity:
        pass

    @abstractmethod
    def mark_as_read(self, notification_id: int) -> None:
        pass

    @abstractmethod
    def mark_all_as_read(self, user_id: int) -> None:
        pass

    @abstractmethod
    def find_by_user_and_customization(self, user_id: int, customization_id: int) -> List[NotificationEntity]:
        pass

    @abstractmethod
    def find_by_user_and_repair(self, user_id: int, repair_id: int) -> List[NotificationEntity]:
        pass

    @abstractmethod
    def find_by_user_and_order(self, user_id: int, order_id: int) -> List[NotificationEntity]:
        pass
