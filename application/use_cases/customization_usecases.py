from decimal import Decimal
from typing import List, Optional
from domain.entities.customization import CustomizationEntity
from domain.repositories.customization_repository import CustomizationRepository
from domain.repositories.user_repository import UserRepository
from domain.repositories.notification_repository import NotificationRepository
from domain.entities.notification import NotificationEntity, NotificationType


class CustomizationUseCases:
    def __init__(self, customization_repo: CustomizationRepository,
                 user_repo: UserRepository, notification_repo: NotificationRepository):
        self._repo = customization_repo
        self._user_repo = user_repo
        self._notification_repo = notification_repo

    def get_all(self) -> List[CustomizationEntity]:
        return self._repo.find_all()

    def get_by_id(self, customization_id: int) -> Optional[CustomizationEntity]:
        return self._repo.find_by_id(customization_id)

    def get_by_user(self, user_id: int) -> List[CustomizationEntity]:
        return self._repo.find_by_user(user_id)

    def create(self, user_id: int, jewelry_type: str, design: str, stones: str,
               finish: str, color: str, material: str, size: str = None,
               engraving: str = None, special_instructions: str = None) -> CustomizationEntity:
        customization = CustomizationEntity(
            user_id=user_id, jewelry_type=jewelry_type, design=design,
            stones=stones, finish=finish, color=color, material=material,
            size=size, engraving=engraving, special_instructions=special_instructions,
            status='pending',
        )
        saved = self._repo.save(customization)

        admins = self._user_repo.find_admins()
        user = self._user_repo.find_by_id(user_id)
        for admin in admins:
            try:
                msg = (f'Nueva personalización de {user.name if user else user_id}: '
                       f'{jewelry_type} - {design}')
                notif = NotificationEntity(
                    user_id=admin.id, customization_id=saved.id,
                    message=msg, notification_type=NotificationType.NEW_CUSTOMIZATION,
                )
                self._notification_repo.save(notif)
            except Exception:
                pass

        return saved

    def update(self, customization_id: int, jewelry_type: str, design: str,
               stones: str, finish: str, color: str, material: str,
               size: str = None, engraving: str = None,
               special_instructions: str = None, estimated_price: Decimal = None,
               status: str = None, admin_notes: str = None,
               assigned_technician: str = None) -> CustomizationEntity:
        customization = self._repo.find_by_id(customization_id)
        if not customization:
            raise ValueError(f'Personalización no encontrada con id: {customization_id}')
        old_status = customization.status
        old_price = customization.estimated_price
        old_technician = customization.assigned_technician
        customization.jewelry_type = jewelry_type
        customization.design = design
        customization.stones = stones
        customization.finish = finish
        customization.color = color
        customization.material = material
        customization.size = size
        customization.engraving = engraving
        customization.special_instructions = special_instructions
        if estimated_price is not None:
            customization.estimated_price = estimated_price
        if status:
            customization.status = status
        if estimated_price and estimated_price != old_price and customization.status == 'pending':
            customization.status = 'quoted'
        if admin_notes is not None:
            customization.admin_notes = admin_notes
        if assigned_technician is not None:
            customization.assigned_technician = assigned_technician
        saved = self._repo.save(customization)

        if customization.user_id:
            if status and status != old_status:
                try:
                    msg = f'El estado de tu personalización #{customization_id} cambió a: {status}'
                    self._notification_repo.save(NotificationEntity(
                        user_id=customization.user_id, customization_id=customization_id,
                        message=msg, notification_type=NotificationType.CUSTOMIZATION_UPDATE,
                    ))
                except Exception:
                    pass
            if assigned_technician and assigned_technician != old_technician:
                try:
                    msg = f'Se asignó el técnico {assigned_technician} a tu personalización #{customization_id}'
                    self._notification_repo.save(NotificationEntity(
                        user_id=customization.user_id, customization_id=customization_id,
                        message=msg, notification_type=NotificationType.CUSTOMIZATION_UPDATE,
                    ))
                except Exception:
                    pass

        if estimated_price and estimated_price != old_price and customization.user_id:
            try:
                msg = (f'El precio estimado de tu personalización fue actualizado a '
                       f'${estimated_price:,.2f}')
                notif = NotificationEntity(
                    user_id=customization.user_id, customization_id=customization_id,
                    message=msg, notification_type=NotificationType.PRICE_UPDATE,
                )
                self._notification_repo.save(notif)
            except Exception:
                pass

        return saved

    def deactivate(self, customization_id: int) -> None:
        customization = self._repo.find_by_id(customization_id)
        if not customization:
            raise ValueError(f'Personalización no encontrada con id: {customization_id}')
        customization.is_active = False
        self._repo.save(customization)
