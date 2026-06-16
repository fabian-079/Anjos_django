from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    if sender.name != 'infrastructure':
        return
    _ensure_roles()
    _ensure_admin()


def _ensure_roles():
    from infrastructure.models.user_model import Role
    for role_name in ['admin', 'cliente']:
        Role.objects.get_or_create(name=role_name)


def _ensure_admin():
    from django.conf import settings
    from infrastructure.models.user_model import User, Role

    admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@anjos.com')
    admin_password = getattr(settings, 'ADMIN_PASSWORD', 'admin123')
    admin_name = getattr(settings, 'ADMIN_NAME', 'Administrador')

    if not User.objects.filter(email=admin_email).exists():
        admin_user = User.objects.create_superuser(
            email=admin_email,
            name=admin_name,
            password=admin_password,
        )
        try:
            admin_role = Role.objects.get(name='admin')
            admin_user.roles.add(admin_role)
        except Role.DoesNotExist:
            pass
