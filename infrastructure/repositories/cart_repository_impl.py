from typing import List, Optional
from domain.entities.cart_item import CartItemEntity
from domain.repositories.cart_repository import CartRepository
from infrastructure.models.cart_model import CartItem


def _to_entity(c: CartItem) -> CartItemEntity:
    return CartItemEntity(
        id=c.id, user_id=c.user_id, product_id=c.product_id,
        product_name=c.product.name if c.product else None,
        product_price=c.product.price if c.product else 0,
        product_image=c.product.image if c.product else None,
        quantity=c.quantity,
        created_at=c.created_at,
    )


class CartRepositoryImpl(CartRepository):

    def find_by_user(self, user_id: int) -> List[CartItemEntity]:
        qs = CartItem.objects.select_related('product__category').filter(user_id=user_id)
        return [_to_entity(c) for c in qs]

    def find_by_user_and_product(self, user_id: int, product_id: int) -> Optional[CartItemEntity]:
        try:
            c = CartItem.objects.select_related('product').get(user_id=user_id, product_id=product_id)
            return _to_entity(c)
        except CartItem.DoesNotExist:
            return None

    def find_by_id(self, cart_item_id: int) -> Optional[CartItemEntity]:
        try:
            c = CartItem.objects.select_related('product').get(pk=cart_item_id)
            return _to_entity(c)
        except CartItem.DoesNotExist:
            return None

    def save(self, cart_item: CartItemEntity) -> CartItemEntity:
        if cart_item.id:
            CartItem.objects.filter(pk=cart_item.id).update(quantity=cart_item.quantity)
            c = CartItem.objects.select_related('product').get(pk=cart_item.id)
        else:
            c = CartItem.objects.create(
                user_id=cart_item.user_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
            )
            c = CartItem.objects.select_related('product').get(pk=c.id)
        return _to_entity(c)

    def delete(self, cart_item_id: int) -> None:
        CartItem.objects.filter(pk=cart_item_id).delete()

    def clear_by_user(self, user_id: int) -> None:
        CartItem.objects.filter(user_id=user_id).delete()
