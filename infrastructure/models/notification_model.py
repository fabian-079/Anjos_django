from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        PRICE_UPDATE = 'PRICE_UPDATE', 'Actualización de precio'
        CUSTOMIZATION_UPDATE = 'CUSTOMIZATION_UPDATE', 'Actualización de personalización'
        STATUS_CHANGE = 'STATUS_CHANGE', 'Cambio de estado'
        NEW_CUSTOMIZATION = 'NEW_CUSTOMIZATION', 'Nueva personalización'
        NEW_REPAIR = 'NEW_REPAIR', 'Nueva reparación'
        REPAIR_UPDATE = 'REPAIR_UPDATE', 'Actualización de reparación'
        REPAIR_STATUS_CHANGE = 'REPAIR_STATUS_CHANGE', 'Cambio de estado de reparación'
        NEW_ORDER = 'NEW_ORDER', 'Nueva orden'
        ORDER_STATUS_CHANGE = 'ORDER_STATUS_CHANGE', 'Cambio de estado de orden'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    customization = models.ForeignKey(
        'infrastructure.Customization', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notifications'
    )
    repair = models.ForeignKey(
        'infrastructure.Repair', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notifications'
    )
    order = models.ForeignKey(
        'infrastructure.Order', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=30, choices=NotificationType.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'infrastructure'
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'Notificación {self.id} - {self.user.email}'
