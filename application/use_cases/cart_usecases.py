from decimal import Decimal
from typing import List
from domain.entities.cart_item import CartItemEntity
from domain.repositories.cart_repository import CartRepository
from domain.repositories.product_repository import ProductRepository


class CartUseCases:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository):
        self._cart_repo = cart_repo
        self._product_repo = product_repo

    def get_cart_items(self, user_id: int) -> List[CartItemEntity]:
        return self._cart_repo.find_by_user(user_id)

    def add_to_cart(self, user_id: int, product_id: int, quantity: int) -> CartItemEntity:
        product = self._product_repo.find_by_id(product_id)
        if not product:
            raise ValueError(f'Producto no encontrado con id: {product_id}')
        if product.stock < quantity:
            raise ValueError(f'Stock insuficiente para "{product.name}". Disponible: {product.stock}')

        existing = self._cart_repo.find_by_user_and_product(user_id, product_id)
        if existing:
            new_qty = existing.quantity + quantity
            if product.stock < new_qty:
                raise ValueError(f'Stock insuficiente para "{product.name}". Disponible: {product.stock}')
            existing.quantity = new_qty
            return self._cart_repo.save(existing)
        else:
            item = CartItemEntity(
                user_id=user_id, product_id=product_id,
                product_name=product.name, product_price=product.price,
                product_image=product.image, quantity=quantity,
            )
            return self._cart_repo.save(item)

    def update_quantity(self, cart_item_id: int, quantity: int) -> CartItemEntity:
        item = self._cart_repo.find_by_id(cart_item_id)
        if not item:
            raise ValueError(f'Item del carrito no encontrado con id: {cart_item_id}')
        product = self._product_repo.find_by_id(item.product_id)
        if product and product.stock < quantity:
            raise ValueError(f'Stock insuficiente para "{product.name}". Disponible: {product.stock}')
        item.quantity = quantity
        return self._cart_repo.save(item)

    def remove_from_cart(self, cart_item_id: int) -> None:
        self._cart_repo.delete(cart_item_id)

    def clear_cart(self, user_id: int) -> None:
        self._cart_repo.clear_by_user(user_id)

    def get_cart_total(self, user_id: int) -> Decimal:
        items = self._cart_repo.find_by_user(user_id)
        return sum((item.subtotal for item in items), Decimal('0.00'))

    def get_cart_count(self, user_id: int) -> int:
        items = self._cart_repo.find_by_user(user_id)
        return sum(item.quantity for item in items)
