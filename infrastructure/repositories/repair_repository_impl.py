from typing import List, Optional
from domain.entities.repair import RepairEntity
from domain.repositories.repair_repository import RepairRepository
from infrastructure.models.repair_model import Repair


def _to_entity(r: Repair) -> RepairEntity:
    return RepairEntity(
        id=r.id, repair_number=r.repair_number,
        user_id=r.user_id,
        user_name=r.user.name if r.user else None,
        customer_name=r.customer_name,
        description=r.description,
        phone=r.phone, image=r.image,
        status=r.status,
        assigned_technician_id=r.assigned_technician_id,
        assigned_technician_name=r.assigned_technician.name if r.assigned_technician else None,
        assigned_technician_text=r.assigned_technician_text,
        cost_accepted=r.cost_accepted,
        client_counter_offer=r.client_counter_offer,
        client_negotiation_note=r.client_negotiation_note,
        estimated_cost=r.estimated_cost,
        technician_notes=r.technician_notes,
        notes=r.notes, is_active=r.is_active,
        created_at=r.created_at, updated_at=r.updated_at,
    )


class RepairRepositoryImpl(RepairRepository):

    def find_all(self) -> List[RepairEntity]:
        qs = Repair.objects.select_related('user', 'assigned_technician').all()
        return [_to_entity(r) for r in qs]

    def find_by_id(self, repair_id: int) -> Optional[RepairEntity]:
        try:
            r = Repair.objects.select_related('user', 'assigned_technician').get(pk=repair_id)
            return _to_entity(r)
        except Repair.DoesNotExist:
            return None

    def find_by_user(self, user_id: int) -> List[RepairEntity]:
        qs = Repair.objects.select_related('user', 'assigned_technician').filter(user_id=user_id)
        return [_to_entity(r) for r in qs]

    def find_by_technician(self, technician_id: int) -> List[RepairEntity]:
        qs = Repair.objects.select_related('user', 'assigned_technician').filter(
            assigned_technician_id=technician_id
        )
        return [_to_entity(r) for r in qs]

    def find_by_repair_number(self, repair_number: str) -> Optional[RepairEntity]:
        try:
            r = Repair.objects.select_related('user', 'assigned_technician').get(repair_number=repair_number)
            return _to_entity(r)
        except Repair.DoesNotExist:
            return None

    def save(self, repair: RepairEntity) -> RepairEntity:
        if repair.id:
            db = Repair.objects.get(pk=repair.id)
            db.customer_name = repair.customer_name
            db.description = repair.description
            db.phone = repair.phone
            db.status = repair.status
            db.assigned_technician_id = repair.assigned_technician_id
            db.assigned_technician_text = repair.assigned_technician_text
            db.cost_accepted = repair.cost_accepted
            db.client_counter_offer = repair.client_counter_offer
            db.client_negotiation_note = repair.client_negotiation_note
            db.estimated_cost = repair.estimated_cost
            db.technician_notes = repair.technician_notes
            db.notes = repair.notes
            db.is_active = repair.is_active
            if repair.image:
                db.image = repair.image
            db.save()
        else:
            db = Repair.objects.create(
                repair_number=repair.repair_number,
                user_id=repair.user_id,
                customer_name=repair.customer_name,
                description=repair.description,
                phone=repair.phone,
                image=repair.image,
                status=repair.status,
                assigned_technician_id=repair.assigned_technician_id,
                assigned_technician_text=repair.assigned_technician_text,
                cost_accepted=repair.cost_accepted,
                client_counter_offer=repair.client_counter_offer,
                client_negotiation_note=repair.client_negotiation_note,
                estimated_cost=repair.estimated_cost,
                technician_notes=repair.technician_notes,
                notes=repair.notes,
                is_active=repair.is_active,
            )
        db.refresh_from_db()
        return _to_entity(
            Repair.objects.select_related('user', 'assigned_technician').get(pk=db.id)
        )

    def delete(self, repair_id: int) -> None:
        Repair.objects.filter(pk=repair_id).update(is_active=False)
