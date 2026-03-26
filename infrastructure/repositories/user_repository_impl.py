from typing import List, Optional
from domain.entities.user import UserEntity
from domain.repositories.user_repository import UserRepository
from infrastructure.models.user_model import User, Role


def _to_entity(user: User) -> UserEntity:
    return UserEntity(
        id=user.id,
        name=user.name,
        email=user.email,
        password=user.password,
        phone=user.phone,
        address=user.address,
        is_active=user.is_active,
        email_verified_at=user.email_verified_at,
        roles=list(user.roles.values_list('name', flat=True)),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


class UserRepositoryImpl(UserRepository):

    def find_all(self) -> List[UserEntity]:
        return [_to_entity(u) for u in User.objects.prefetch_related('roles').all()]

    def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        try:
            user = User.objects.prefetch_related('roles').get(pk=user_id)
            return _to_entity(user)
        except User.DoesNotExist:
            return None

    def find_by_email(self, email: str) -> Optional[UserEntity]:
        try:
            user = User.objects.prefetch_related('roles').get(email=email)
            return _to_entity(user)
        except User.DoesNotExist:
            return None

    def save(self, user: UserEntity) -> UserEntity:
        if user.id:
            db_user = User.objects.get(pk=user.id)
            db_user.name = user.name
            db_user.email = user.email
            db_user.phone = user.phone
            db_user.address = user.address
            db_user.is_active = user.is_active
            db_user.email_verified_at = user.email_verified_at
            if user.password and not user.password.startswith('pbkdf2_'):
                db_user.set_password(user.password)
            db_user.save()
        else:
            db_user = User(
                name=user.name, email=user.email,
                phone=user.phone, address=user.address,
                is_active=user.is_active,
            )
            if user.password and not user.password.startswith('pbkdf2_'):
                db_user.set_password(user.password)
            else:
                db_user.password = user.password
            db_user.save()

        if user.roles is not None:
            roles = Role.objects.filter(name__in=user.roles)
            db_user.roles.set(roles)

        db_user.refresh_from_db()
        return _to_entity(db_user)

    def delete(self, user_id: int) -> None:
        User.objects.filter(pk=user_id).update(is_active=False)

    def exists_by_email(self, email: str) -> bool:
        return User.objects.filter(email=email).exists()

    def find_admins(self) -> List[UserEntity]:
        return [
            _to_entity(u) for u in
            User.objects.prefetch_related('roles').filter(
                roles__name__iexact='admin', is_active=True
            )
        ]
