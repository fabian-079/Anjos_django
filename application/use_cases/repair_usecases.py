import time
from decimal import Decimal
from typing import List, Optional
from domain.entities.repair import RepairEntity, RepairStatus
from domain.repositories.repair_repository import RepairRepository
from domain.repositories.user_repository import UserRepository
from domain.repositories.notification_repository import NotificationRepository
from domain.entities.notification import NotificationEntity, NotificationType


class RepairUseCases:
    def __init__(self, repair_repo: RepairRepository, user_repo: UserRepository,
                 notification_repo: NotificationRepository):
        self._repair_repo = repair_repo
        self._user_repo = user_repo
        self._notification_repo = notification_repo

    def get_all(self) -> List[RepairEntity]:
        return self._repair_repo.find_all()

    def get_by_id(self, repair_id: int) -> Optional[RepairEntity]:
        return self._repair_repo.find_by_id(repair_id)

    def get_by_user(self, user_id: int) -> List[RepairEntity]:
        return self._repair_repo.find_by_user(user_id)

    def get_by_technician(self, technician_id: int) -> List[RepairEntity]:
        return self._repair_repo.find_by_technician(technician_id)

    def get_by_repair_number(self, repair_number: str) -> Optional[RepairEntity]:
        return self._repair_repo.find_by_repair_number(repair_number)

    def create(self, user_id: int, customer_name: str, description: str,
               phone: str, image: str = None, notes: str = None) -> RepairEntity:
        repair_number = f'REP-{int(time.time() * 1000)}'
        repair = RepairEntity(
            repair_number=repair_number,
            user_id=user_id,
            customer_name=customer_name,
            description=description,
            phone=phone,
            image=image,
            notes=notes,
            status=RepairStatus.PENDING,
        )
        saved = self._repair_repo.save(repair)

        admins = self._user_repo.find_admins()
        user = self._user_repo.find_by_id(user_id)
        for admin in admins:
            try:
                msg = (f'Nueva solicitud de reparación de {user.name if user else user_id}. '
                       f'N° {saved.repair_number}')
                notif = NotificationEntity(
                    user_id=admin.id, repair_id=saved.id,
                    message=msg, notification_type=NotificationType.NEW_REPAIR,
                )
                self._notification_repo.save(notif)
            except Exception:
                pass

        return saved

    def update(self, repair_id: int, customer_name: str, description: str,
               phone: str, status: str, estimated_cost: Decimal = None,
               technician_notes: str = None, notes: str = None,
               image: str = None, assigned_technician_text: str = None) -> RepairEntity:
        repair = self._repair_repo.find_by_id(repair_id)
        if not repair:
            raise ValueError(f'Reparación no encontrada con id: {repair_id}')
        old_status = repair.status
        old_cost = repair.estimated_cost
        old_technician = repair.assigned_technician_text
        repair.customer_name = customer_name
        repair.description = description
        repair.phone = phone
        repair.status = status
        if estimated_cost is not None:
            repair.estimated_cost = estimated_cost
        repair.technician_notes = technician_notes
        repair.notes = notes
        repair.assigned_technician_text = assigned_technician_text or repair.assigned_technician_text
        if image:
            repair.image = image
        if estimated_cost and estimated_cost != old_cost and repair.status == RepairStatus.PENDING:
            repair.status = RepairStatus.QUOTED
        saved = self._repair_repo.save(repair)

        if repair.user_id:
            if old_status != repair.status:
                try:
                    msg = f'El estado de tu reparación N° {repair.repair_number} cambió a: {repair.status}'
                    self._notification_repo.save(NotificationEntity(
                        user_id=repair.user_id, repair_id=repair_id,
                        message=msg, notification_type=NotificationType.REPAIR_STATUS_CHANGE,
                    ))
                except Exception:
                    pass
            if estimated_cost and estimated_cost != old_cost:
                try:
                    msg = f'El costo estimado de tu reparación N° {repair.repair_number} fue actualizado a ${estimated_cost:,.0f}'
                    self._notification_repo.save(NotificationEntity(
                        user_id=repair.user_id, repair_id=repair_id,
                        message=msg, notification_type=NotificationType.REPAIR_UPDATE,
                    ))
                except Exception:
                    pass
            if assigned_technician_text and assigned_technician_text != old_technician:
                try:
                    msg = f'Se asignó el técnico {assigned_technician_text} a tu reparación N° {repair.repair_number}'
                    self._notification_repo.save(NotificationEntity(
                        user_id=repair.user_id, repair_id=repair_id,
                        message=msg, notification_type=NotificationType.REPAIR_UPDATE,
                    ))
                except Exception:
                    pass

        return saved

    def assign_technician(self, repair_id: int, technician_id: int) -> RepairEntity:
        repair = self._repair_repo.find_by_id(repair_id)
        if not repair:
            raise ValueError(f'Reparación no encontrada con id: {repair_id}')
        technician = self._user_repo.find_by_id(technician_id)
        if not technician:
            raise ValueError(f'Técnico no encontrado con id: {technician_id}')
        repair.assigned_technician_id = technician_id
        repair.assigned_technician_name = technician.name
        return self._repair_repo.save(repair)

    def update_status(self, repair_id: int, status: str) -> RepairEntity:
        repair = self._repair_repo.find_by_id(repair_id)
        if not repair:
            raise ValueError(f'Reparación no encontrada con id: {repair_id}')
        repair.status = status
        return self._repair_repo.save(repair)

    def deactivate(self, repair_id: int) -> None:
        repair = self._repair_repo.find_by_id(repair_id)
        if not repair:
            raise ValueError(f'Reparación no encontrada con id: {repair_id}')
        repair.is_active = False
        self._repair_repo.save(repair)
