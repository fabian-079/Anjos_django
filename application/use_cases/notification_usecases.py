from typing import List
from domain.entities.notification import NotificationEntity, NotificationType
from domain.repositories.notification_repository import NotificationRepository
from domain.repositories.user_repository import UserRepository


class NotificationUseCases:
    def __init__(self, notification_repo: NotificationRepository, user_repo: UserRepository):
        self._repo = notification_repo
        self._user_repo = user_repo

    def get_by_user(self, user_id: int) -> List[NotificationEntity]:
        return self._repo.find_by_user(user_id)

    def get_unread_by_user(self, user_id: int) -> List[NotificationEntity]:
        return self._repo.find_unread_by_user(user_id)

    def count_unread(self, user_id: int) -> int:
        return self._repo.count_unread_by_user(user_id)

    def mark_as_read(self, notification_id: int) -> None:
        self._repo.mark_as_read(notification_id)

    def mark_all_as_read(self, user_id: int) -> None:
        self._repo.mark_all_as_read(user_id)

    def get_by_customization(self, user_id: int, customization_id: int) -> List[NotificationEntity]:
        return self._repo.find_by_user_and_customization(user_id, customization_id)

    def get_by_repair(self, user_id: int, repair_id: int) -> List[NotificationEntity]:
        return self._repo.find_by_user_and_repair(user_id, repair_id)

    def get_by_order(self, user_id: int, order_id: int) -> List[NotificationEntity]:
        return self._repo.find_by_user_and_order(user_id, order_id)
