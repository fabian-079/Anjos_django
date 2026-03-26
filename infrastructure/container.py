"""
Dependency injection container — instantiates all use cases with their repository implementations.
Import get_* functions in views instead of instantiating directly.
"""
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.repositories.product_repository_impl import ProductRepositoryImpl
from infrastructure.repositories.category_repository_impl import CategoryRepositoryImpl
from infrastructure.repositories.order_repository_impl import OrderRepositoryImpl
from infrastructure.repositories.cart_repository_impl import CartRepositoryImpl
from infrastructure.repositories.favorite_repository_impl import FavoriteRepositoryImpl
from infrastructure.repositories.repair_repository_impl import RepairRepositoryImpl
from infrastructure.repositories.customization_repository_impl import CustomizationRepositoryImpl
from infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl

from application.use_cases.user_usecases import UserUseCases
from application.use_cases.product_usecases import ProductUseCases
from application.use_cases.category_usecases import CategoryUseCases
from application.use_cases.order_usecases import OrderUseCases
from application.use_cases.cart_usecases import CartUseCases
from application.use_cases.favorite_usecases import FavoriteUseCases
from application.use_cases.repair_usecases import RepairUseCases
from application.use_cases.customization_usecases import CustomizationUseCases
from application.use_cases.notification_usecases import NotificationUseCases


def get_user_usecases() -> UserUseCases:
    return UserUseCases(UserRepositoryImpl())


def get_product_usecases() -> ProductUseCases:
    return ProductUseCases(ProductRepositoryImpl(), CategoryRepositoryImpl())


def get_category_usecases() -> CategoryUseCases:
    return CategoryUseCases(CategoryRepositoryImpl())


def get_cart_usecases() -> CartUseCases:
    return CartUseCases(CartRepositoryImpl(), ProductRepositoryImpl())


def get_order_usecases() -> OrderUseCases:
    return OrderUseCases(
        OrderRepositoryImpl(),
        CartRepositoryImpl(),
        ProductRepositoryImpl(),
        NotificationRepositoryImpl(),
        UserRepositoryImpl(),
    )


def get_favorite_usecases() -> FavoriteUseCases:
    return FavoriteUseCases(
        FavoriteRepositoryImpl(),
        ProductRepositoryImpl(),
        CustomizationRepositoryImpl(),
    )


def get_repair_usecases() -> RepairUseCases:
    return RepairUseCases(
        RepairRepositoryImpl(),
        UserRepositoryImpl(),
        NotificationRepositoryImpl(),
    )


def get_customization_usecases() -> CustomizationUseCases:
    return CustomizationUseCases(
        CustomizationRepositoryImpl(),
        UserRepositoryImpl(),
        NotificationRepositoryImpl(),
    )


def get_notification_usecases() -> NotificationUseCases:
    return NotificationUseCases(NotificationRepositoryImpl(), UserRepositoryImpl())
