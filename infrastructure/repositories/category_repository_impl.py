from typing import List, Optional
from domain.entities.category import CategoryEntity
from domain.repositories.category_repository import CategoryRepository
from infrastructure.models.category_model import Category


def _to_entity(c: Category) -> CategoryEntity:
    return CategoryEntity(
        id=c.id, name=c.name, description=c.description,
        image=c.image, is_active=c.is_active,
        created_at=c.created_at, updated_at=c.updated_at,
    )


class CategoryRepositoryImpl(CategoryRepository):

    def find_all(self) -> List[CategoryEntity]:
        return [_to_entity(c) for c in Category.objects.all()]

    def find_active(self) -> List[CategoryEntity]:
        return [_to_entity(c) for c in Category.objects.filter(is_active=True)]

    def find_by_id(self, category_id: int) -> Optional[CategoryEntity]:
        try:
            return _to_entity(Category.objects.get(pk=category_id))
        except Category.DoesNotExist:
            return None

    def save(self, category: CategoryEntity) -> CategoryEntity:
        if category.id:
            db = Category.objects.get(pk=category.id)
            db.name = category.name
            db.description = category.description
            db.is_active = category.is_active
            if category.image:
                db.image = category.image
            db.save()
        else:
            db = Category.objects.create(
                name=category.name,
                description=category.description,
                image=category.image,
                is_active=category.is_active,
            )
        return _to_entity(db)

    def delete(self, category_id: int) -> None:
        Category.objects.filter(pk=category_id).update(is_active=False)
