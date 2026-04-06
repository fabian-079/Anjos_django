from typing import List, Optional
from domain.entities.order import OrderEntity, OrderItemEntity
from domain.repositories.order_repository import OrderRepository
from infrastructure.models.order_model import Order, OrderItem


def _item_to_entity(item: OrderItem) -> OrderItemEntity:
    return OrderItemEntity(
        id=item.id, order_id=item.order_id,
        product_id=item.product_id,
        product_name=item.product.name if item.product else None,
        product_image=item.product.image if item.product else None,
        quantity=item.quantity, price=item.price,
        created_at=item.created_at,
    )


def _to_entity(o: Order) -> OrderEntity:
    items = [_item_to_entity(i) for i in o.items.select_related('product').all()]
    return OrderEntity(
        id=o.id, order_number=o.order_number,
        user_id=o.user_id,
        user_name=o.user.name if o.user else None,
        subtotal=o.subtotal, tax=o.tax, total=o.total,
        status=o.status,
        shipping_address=o.shipping_address,
        billing_address=o.billing_address,
        phone=o.phone, payment_method=o.payment_method,
        notes=o.notes, is_active=o.is_active,
        items=items,
        created_at=o.created_at, updated_at=o.updated_at,
    )


class OrderRepositoryImpl(OrderRepository):

    def find_all(self) -> List[OrderEntity]:
        return [_to_entity(o) for o in Order.objects.select_related('user').prefetch_related('items__product').all()]

    def find_by_id(self, order_id: int) -> Optional[OrderEntity]:
        try:
            o = Order.objects.select_related('user').prefetch_related('items__product').get(pk=order_id)
            return _to_entity(o)
        except Order.DoesNotExist:
            return None

    def find_by_user(self, user_id: int) -> List[OrderEntity]:
        qs = Order.objects.select_related('user').prefetch_related('items__product').filter(user_id=user_id)
        return [_to_entity(o) for o in qs]

    def find_by_order_number(self, order_number: str) -> Optional[OrderEntity]:
        try:
            o = Order.objects.select_related('user').prefetch_related('items__product').get(order_number=order_number)
            return _to_entity(o)
        except Order.DoesNotExist:
            return None

    def save(self, order: OrderEntity) -> OrderEntity:
        if order.id:
            db = Order.objects.get(pk=order.id)
            db.status = order.status
            db.shipping_address = order.shipping_address
            db.billing_address = order.billing_address
            db.phone = order.phone
            db.payment_method = order.payment_method
            db.notes = order.notes
            db.is_active = order.is_active
            db.save()
        else:
            db = Order.objects.create(
                order_number=order.order_number,
                user_id=order.user_id,
                subtotal=order.subtotal,
                tax=order.tax,
                total=order.total,
                status=order.status,
                shipping_address=order.shipping_address,
                billing_address=order.billing_address,
                phone=order.phone,
                payment_method=order.payment_method,
                notes=order.notes,
                is_active=order.is_active,
            )
            for item in order.items:
                OrderItem.objects.create(
                    order=db,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price,
                )

        db.refresh_from_db()
        return _to_entity(
            Order.objects.select_related('user').prefetch_related('items__product').get(pk=db.id)
        )

    def delete(self, order_id: int) -> None:
        Order.objects.filter(pk=order_id).update(is_active=False)
