from typing import List
from domain.entities.notification import NotificationEntity
from domain.repositories.notification_repository import NotificationRepository
from infrastructure.models.notification_model import Notification


def _to_entity(n: Notification) -> NotificationEntity:
    return NotificationEntity(
        id=n.id, user_id=n.user_id,
        customization_id=n.customization_id,
        repair_id=n.repair_id,
        order_id=n.order_id,
        message=n.message,
        is_read=n.is_read,
        notification_type=n.notification_type,
        created_at=n.created_at,
    )


class NotificationRepositoryImpl(NotificationRepository):

    def find_by_user(self, user_id: int) -> List[NotificationEntity]:
        qs = Notification.objects.filter(user_id=user_id).order_by('-created_at')
        return [_to_entity(n) for n in qs]

    def find_unread_by_user(self, user_id: int) -> List[NotificationEntity]:
        qs = Notification.objects.filter(user_id=user_id, is_read=False).order_by('-created_at')
        return [_to_entity(n) for n in qs]

    def count_unread_by_user(self, user_id: int) -> int:
        return Notification.objects.filter(user_id=user_id, is_read=False).count()

    def save(self, notification: NotificationEntity) -> NotificationEntity:
        db = Notification.objects.create(
            user_id=notification.user_id,
            customization_id=notification.customization_id,
            repair_id=notification.repair_id,
            order_id=notification.order_id,
            message=notification.message,
            is_read=notification.is_read,
            notification_type=notification.notification_type,
        )
        return _to_entity(db)

    def mark_as_read(self, notification_id: int) -> None:
        Notification.objects.filter(pk=notification_id).update(is_read=True)

    def mark_all_as_read(self, user_id: int) -> None:
        Notification.objects.filter(user_id=user_id, is_read=False).update(is_read=True)

    def find_by_user_and_customization(self, user_id: int, customization_id: int) -> List[NotificationEntity]:
        qs = Notification.objects.filter(
            user_id=user_id, customization_id=customization_id
        ).order_by('-created_at')
        return [_to_entity(n) for n in qs]

    def find_by_user_and_repair(self, user_id: int, repair_id: int) -> List[NotificationEntity]:
        qs = Notification.objects.filter(
            user_id=user_id, repair_id=repair_id
        ).order_by('-created_at')
        return [_to_entity(n) for n in qs]

    def find_by_user_and_order(self, user_id: int, order_id: int) -> List[NotificationEntity]:
        qs = Notification.objects.filter(
            user_id=user_id, order_id=order_id
        ).order_by('-created_at')
        return [_to_entity(n) for n in qs]
