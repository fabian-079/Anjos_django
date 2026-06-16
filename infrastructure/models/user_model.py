from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    guard_name = models.CharField(max_length=50, default='web')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'infrastructure'
        db_table = 'roles'

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es requerido')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    roles = models.ManyToManyField(
        Role,
        through='ModelHasRole',
        related_name='users',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        app_label = 'infrastructure'
        db_table = 'users'

    def __str__(self):
        return self.email

    def is_admin(self):
        return self.roles.filter(name__iexact='admin').exists()

    def is_client(self):
        return self.roles.filter(name__iexact='cliente').exists()

    def get_role_names(self):
        return list(self.roles.values_list('name', flat=True))


class ModelHasRole(models.Model):
    model = models.ForeignKey(User, on_delete=models.CASCADE, db_column='model_id')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        app_label = 'infrastructure'
        db_table = 'model_has_roles'
        unique_together = [('model', 'role')]
