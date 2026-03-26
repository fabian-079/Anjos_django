from typing import List, Optional
from domain.entities.customization import CustomizationEntity
from domain.repositories.customization_repository import CustomizationRepository
from infrastructure.models.customization_model import Customization


def _to_entity(c: Customization) -> CustomizationEntity:
    return CustomizationEntity(
        id=c.id, user_id=c.user_id,
        user_name=c.user.name if c.user else None,
        jewelry_type=c.jewelry_type, design=c.design,
        stones=c.stones, finish=c.finish, color=c.color, material=c.material,
        size=c.size, engraving=c.engraving,
        special_instructions=c.special_instructions,
        estimated_price=c.estimated_price,
        status=c.status, admin_notes=c.admin_notes,
        is_active=c.is_active,
        created_at=c.created_at, updated_at=c.updated_at,
    )


class CustomizationRepositoryImpl(CustomizationRepository):

    def find_all(self) -> List[CustomizationEntity]:
        return [_to_entity(c) for c in Customization.objects.select_related('user').all()]

    def find_by_id(self, customization_id: int) -> Optional[CustomizationEntity]:
        try:
            c = Customization.objects.select_related('user').get(pk=customization_id)
            return _to_entity(c)
        except Customization.DoesNotExist:
            return None

    def find_by_user(self, user_id: int) -> List[CustomizationEntity]:
        qs = Customization.objects.select_related('user').filter(user_id=user_id)
        return [_to_entity(c) for c in qs]

    def save(self, customization: CustomizationEntity) -> CustomizationEntity:
        if customization.id:
            db = Customization.objects.get(pk=customization.id)
            db.jewelry_type = customization.jewelry_type
            db.design = customization.design
            db.stones = customization.stones
            db.finish = customization.finish
            db.color = customization.color
            db.material = customization.material
            db.size = customization.size
            db.engraving = customization.engraving
            db.special_instructions = customization.special_instructions
            db.estimated_price = customization.estimated_price
            db.status = customization.status
            db.admin_notes = customization.admin_notes
            db.is_active = customization.is_active
            db.save()
        else:
            db = Customization.objects.create(
                user_id=customization.user_id,
                jewelry_type=customization.jewelry_type,
                design=customization.design,
                stones=customization.stones,
                finish=customization.finish,
                color=customization.color,
                material=customization.material,
                size=customization.size,
                engraving=customization.engraving,
                special_instructions=customization.special_instructions,
                estimated_price=customization.estimated_price,
                status=customization.status or 'pending',
                admin_notes=customization.admin_notes,
                is_active=customization.is_active,
            )
        db.refresh_from_db()
        return _to_entity(Customization.objects.select_related('user').get(pk=db.id))

    def delete(self, customization_id: int) -> None:
        Customization.objects.filter(pk=customization_id).update(is_active=False)
