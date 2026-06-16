from typing import List, Optional
from domain.entities.user import UserEntity
from domain.repositories.user_repository import UserRepository


class UserUseCases:
    def __init__(self, user_repo: UserRepository):
        self._repo = user_repo

    def get_all_users(self) -> List[UserEntity]:
        return self._repo.find_all()

    def get_user_by_id(self, user_id: int) -> Optional[UserEntity]:
        return self._repo.find_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        return self._repo.find_by_email(email)

    def create_user(self, name: str, email: str, password: str,
                    phone: str = None, address: str = None, role: str = 'cliente') -> UserEntity:
        if self._repo.exists_by_email(email):
            raise ValueError(f'El email {email} ya está registrado')
        user = UserEntity(
            name=name, email=email, password=password,
            phone=phone, address=address, roles=[role], is_active=True,
        )
        return self._repo.save(user)

    def update_user(self, user_id: int, name: str, email: str,
                    phone: str = None, address: str = None,
                    is_active: bool = True, password: str = None) -> UserEntity:
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError(f'Usuario no encontrado con id: {user_id}')
        user.name = name
        user.email = email
        user.phone = phone
        user.address = address
        user.is_active = is_active
        if password:
            user.password = password
        return self._repo.save(user)

    def deactivate_user(self, user_id: int) -> None:
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError(f'Usuario no encontrado con id: {user_id}')
        user.is_active = False
        self._repo.save(user)

    def assign_role(self, user_id: int, role_name: str) -> UserEntity:
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError(f'Usuario no encontrado con id: {user_id}')
        if role_name not in user.roles:
            user.roles.append(role_name)
        return self._repo.save(user)

    def remove_role(self, user_id: int, role_name: str) -> UserEntity:
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError(f'Usuario no encontrado con id: {user_id}')
        user.roles = [r for r in user.roles if r != role_name]
        return self._repo.save(user)

    def get_admins(self) -> List[UserEntity]:
        return self._repo.find_admins()
