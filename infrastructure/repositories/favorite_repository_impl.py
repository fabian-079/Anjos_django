from typing import List, Optional
from domain.entities.favorite import FavoriteEntity
from domain.repositories.favorite_repository import FavoriteRepository
from infrastructure.models.favorite_model import Favorite


def _to_entity(f: Favorite) -> FavoriteEntity:
    return FavoriteEntity(
        id=f.id, user_id=f.user_id,
        product_id=f.product_id,
        product_name=f.product.name if f.product else None,
        product_image=f.product.get_image_url() if f.product else None,
        product_price=float(f.product.price) if f.product and f.product.price else None,
        product_category_name=f.product.category.name if f.product and f.product.category else None,
        customization_id=f.customization_id,
        created_at=f.created_at,
    )


class FavoriteRepositoryImpl(FavoriteRepository):

    def find_by_user(self, user_id: int) -> List[FavoriteEntity]:
        qs = Favorite.objects.select_related('product__category', 'customization').filter(user_id=user_id)
        return [_to_entity(f) for f in qs]

    def find_by_user_and_product(self, user_id: int, product_id: int) -> Optional[FavoriteEntity]:
        try:
            f = Favorite.objects.get(user_id=user_id, product_id=product_id)
            return _to_entity(f)
        except Favorite.DoesNotExist:
            return None

    def find_by_user_and_customization(self, user_id: int, customization_id: int) -> Optional[FavoriteEntity]:
        try:
            f = Favorite.objects.get(user_id=user_id, customization_id=customization_id)
            return _to_entity(f)
        except Favorite.DoesNotExist:
            return None

    def find_by_id(self, favorite_id: int) -> Optional[FavoriteEntity]:
        try:
            return _to_entity(Favorite.objects.select_related('product').get(pk=favorite_id))
        except Favorite.DoesNotExist:
            return None

    def save(self, favorite: FavoriteEntity) -> FavoriteEntity:
        db = Favorite.objects.create(
            user_id=favorite.user_id,
            product_id=favorite.product_id,
            customization_id=favorite.customization_id,
        )
        return _to_entity(Favorite.objects.select_related('product').get(pk=db.id))

    def delete(self, favorite_id: int) -> None:
        Favorite.objects.filter(pk=favorite_id).delete()

    def exists_by_user_and_product(self, user_id: int, product_id: int) -> bool:
        return Favorite.objects.filter(user_id=user_id, product_id=product_id).exists()

    def exists_by_user_and_customization(self, user_id: int, customization_id: int) -> bool:
        return Favorite.objects.filter(user_id=user_id, customization_id=customization_id).exists()
