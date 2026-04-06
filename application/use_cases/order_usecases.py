import time
from decimal import Decimal
from typing import List, Optional
from domain.entities.order import OrderEntity, OrderItemEntity, OrderStatus, PaymentMethod
from domain.repositories.order_repository import OrderRepository
from domain.repositories.cart_repository import CartRepository
from domain.repositories.product_repository import ProductRepository
from domain.repositories.notification_repository import NotificationRepository
from domain.repositories.user_repository import UserRepository
from domain.entities.notification import NotificationEntity, NotificationType


class OrderUseCases:
    def __init__(self, order_repo: OrderRepository, cart_repo: CartRepository,
                 product_repo: ProductRepository, notification_repo: NotificationRepository,
                 user_repo: UserRepository):
        self._order_repo = order_repo
        self._cart_repo = cart_repo
        self._product_repo = product_repo
        self._notification_repo = notification_repo
        self._user_repo = user_repo

    def get_all_orders(self) -> List[OrderEntity]:
        return self._order_repo.find_all()

    def get_order_by_id(self, order_id: int) -> Optional[OrderEntity]:
        return self._order_repo.find_by_id(order_id)

    def get_orders_by_user(self, user_id: int) -> List[OrderEntity]:
        return self._order_repo.find_by_user(user_id)

    def get_by_order_number(self, order_number: str) -> Optional[OrderEntity]:
        return self._order_repo.find_by_order_number(order_number)

    def create_order(self, user_id: int, shipping_address: str, billing_address: str,
                     phone: str, payment_method: str, notes: str = None) -> OrderEntity:
        cart_items = self._cart_repo.find_by_user(user_id)
        if not cart_items:
            raise ValueError('El carrito está vacío')

        subtotal = sum((item.subtotal for item in cart_items), Decimal('0.00'))
        if subtotal <= 0:
            raise ValueError('El total del carrito debe ser mayor a cero')

        tax = subtotal * Decimal('0.19')
        total = subtotal + tax

        order_number = f'ORD-{int(time.time() * 1000)}'
        order = OrderEntity(
            order_number=order_number,
            user_id=user_id,
            subtotal=subtotal,
            tax=tax,
            total=total,
            shipping_address=shipping_address,
            billing_address=billing_address,
            phone=phone,
            payment_method=payment_method.upper(),
            notes=notes,
            status=OrderStatus.PENDING,
        )

        for cart_item in cart_items:
            product = self._product_repo.find_by_id(cart_item.product_id)
            if not product:
                continue
            if product.stock < cart_item.quantity:
                raise ValueError(f'Stock insuficiente para el producto: {product.name}')
            item = OrderItemEntity(
                product_id=product.id,
                product_name=product.name,
                product_image=product.image,
                quantity=cart_item.quantity,
                price=product.price,
            )
            order.items.append(item)
            product.stock -= cart_item.quantity
            self._product_repo.save(product)

        saved_order = self._order_repo.save(order)
        self._cart_repo.clear_by_user(user_id)

        user = self._user_repo.find_by_id(user_id)
        admins = self._user_repo.find_admins()
        for admin in admins:
            try:
                msg = (f'Nueva orden creada por {user.name if user else user_id}. '
                       f'Número de orden: {saved_order.order_number}. '
                       f'Total: ${saved_order.total:,.2f}')
                notif = NotificationEntity(
                    user_id=admin.id, order_id=saved_order.id,
                    message=msg, notification_type=NotificationType.NEW_ORDER,
                )
                self._notification_repo.save(notif)
            except Exception:
                pass

        return saved_order

    def update_order_status(self, order_id: int, status: str) -> OrderEntity:
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f'Orden no encontrada con id: {order_id}')
        old_status = order.status
        order.status = status
        saved = self._order_repo.save(order)
        if old_status != status and order.user_id:
            try:
                msg = f'El estado de tu orden {order.order_number} cambió a: {status}'
                notif = NotificationEntity(
                    user_id=order.user_id, order_id=order_id,
                    message=msg, notification_type=NotificationType.ORDER_STATUS_CHANGE,
                )
                self._notification_repo.save(notif)
            except Exception:
                pass
        return saved

    def update_order(self, order_id: int, status: str, shipping_address: str,
                     billing_address: str, phone: str, payment_method: str,
                     notes: str = None) -> OrderEntity:
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f'Orden no encontrada con id: {order_id}')
        old_status = order.status
        order.status = status
        order.shipping_address = shipping_address
        order.billing_address = billing_address
        order.phone = phone
        order.payment_method = payment_method
        order.notes = notes
        saved = self._order_repo.save(order)
        if old_status != status and order.user_id:
            try:
                msg = f'El estado de tu orden {order.order_number} cambió a: {status}'
                notif = NotificationEntity(
                    user_id=order.user_id, order_id=order_id,
                    message=msg, notification_type=NotificationType.ORDER_STATUS_CHANGE,
                )
                self._notification_repo.save(notif)
            except Exception:
                pass
        return saved

    def deactivate_order(self, order_id: int) -> None:
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f'Orden no encontrada con id: {order_id}')
        order.is_active = False
        self._order_repo.save(order)
