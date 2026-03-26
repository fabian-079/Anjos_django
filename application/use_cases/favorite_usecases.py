from typing import List, Optional
from domain.entities.favorite import FavoriteEntity
from domain.repositories.favorite_repository import FavoriteRepository
from domain.repositories.product_repository import ProductRepository
from domain.repositories.customization_repository import CustomizationRepository


class FavoriteUseCases:
    def __init__(self, favorite_repo: FavoriteRepository,
                 product_repo: ProductRepository,
                 customization_repo: CustomizationRepository):
        self._repo = favorite_repo
        self._product_repo = product_repo
        self._customization_repo = customization_repo

    def get_user_favorites(self, user_id: int) -> List[FavoriteEntity]:
        return self._repo.find_by_user(user_id)

    def toggle_product_favorite(self, user_id: int, product_id: int) -> Optional[FavoriteEntity]:
        existing = self._repo.find_by_user_and_product(user_id, product_id)
        if existing:
            self._repo.delete(existing.id)
            return None
        product = self._product_repo.find_by_id(product_id)
        if not product:
            raise ValueError(f'Producto no encontrado con id: {product_id}')
        favorite = FavoriteEntity(
            user_id=user_id, product_id=product_id,
            product_name=product.name, product_image=product.image,
        )
        return self._repo.save(favorite)

    def toggle_customization_favorite(self, user_id: int, customization_id: int) -> Optional[FavoriteEntity]:
        existing = self._repo.find_by_user_and_customization(user_id, customization_id)
        if existing:
            self._repo.delete(existing.id)
            return None
        customization = self._customization_repo.find_by_id(customization_id)
        if not customization:
            raise ValueError(f'Personalización no encontrada con id: {customization_id}')
        favorite = FavoriteEntity(
            user_id=user_id, customization_id=customization_id,
        )
        return self._repo.save(favorite)

    def remove_favorite(self, favorite_id: int) -> None:
        self._repo.delete(favorite_id)

    def is_product_favorite(self, user_id: int, product_id: int) -> bool:
        return self._repo.exists_by_user_and_product(user_id, product_id)

    def is_customization_favorite(self, user_id: int, customization_id: int) -> bool:
        return self._repo.exists_by_user_and_customization(user_id, customization_id)
