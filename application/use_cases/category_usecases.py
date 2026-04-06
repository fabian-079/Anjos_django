from typing import List, Optional
from domain.entities.category import CategoryEntity
from domain.repositories.category_repository import CategoryRepository


class CategoryUseCases:
    def __init__(self, category_repo: CategoryRepository):
        self._repo = category_repo

    def get_all(self) -> List[CategoryEntity]:
        return self._repo.find_all()

    def get_active(self) -> List[CategoryEntity]:
        return self._repo.find_active()

    def get_by_id(self, category_id: int) -> Optional[CategoryEntity]:
        return self._repo.find_by_id(category_id)

    def create(self, name: str, description: str = None,
               image: str = None, is_active: bool = True) -> CategoryEntity:
        category = CategoryEntity(
            name=name, description=description,
            image=image, is_active=is_active,
        )
        return self._repo.save(category)

    def update(self, category_id: int, name: str, description: str = None,
               image: str = None, is_active: bool = True) -> CategoryEntity:
        category = self._repo.find_by_id(category_id)
        if not category:
            raise ValueError(f'Categoría no encontrada con id: {category_id}')
        category.name = name
        category.description = description
        category.is_active = is_active
        if image:
            category.image = image
        return self._repo.save(category)

    def deactivate(self, category_id: int) -> None:
        category = self._repo.find_by_id(category_id)
        if not category:
            raise ValueError(f'Categoría no encontrada con id: {category_id}')
        category.is_active = False
        self._repo.save(category)
