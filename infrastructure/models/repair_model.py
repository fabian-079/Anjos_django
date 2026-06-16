from django.conf import settings
from django.db import models


class Repair(models.Model):
    class RepairStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        IN_PROGRESS = 'IN_PROGRESS', 'En proceso'
        COMPLETED = 'COMPLETED', 'Completado'
        CANCELLED = 'CANCELLED', 'Cancelado'

    repair_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='repairs'
    )
    customer_name = models.CharField(max_length=255)
    description = models.TextField()
    phone = models.CharField(max_length=50)
    image = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=RepairStatus.choices, default=RepairStatus.PENDING
    )
    assigned_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_repairs'
    )
    estimated_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    assigned_technician_text = models.CharField(max_length=100, null=True, blank=True)
    cost_accepted = models.BooleanField(null=True, blank=True)
    client_counter_offer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    client_negotiation_note = models.TextField(null=True, blank=True)
    technician_notes = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'infrastructure'
        db_table = 'repairs'
        ordering = ['-created_at']

    def __str__(self):
        return f'Reparación {self.repair_number}'
