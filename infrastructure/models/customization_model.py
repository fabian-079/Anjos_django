from django.conf import settings
from django.db import models


class Customization(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='customizations'
    )
    jewelry_type = models.CharField(max_length=100)
    design = models.CharField(max_length=255)
    stones = models.CharField(max_length=100)
    finish = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    size = models.CharField(max_length=50, null=True, blank=True)
    engraving = models.CharField(max_length=255, null=True, blank=True)
    special_instructions = models.TextField(null=True, blank=True)
    estimated_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(max_length=50, default='pending')
    assigned_technician = models.CharField(max_length=100, null=True, blank=True)
    cost_accepted = models.BooleanField(null=True, blank=True)
    client_counter_offer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    client_negotiation_note = models.TextField(null=True, blank=True)
    admin_notes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'infrastructure'
        db_table = 'customizations'
        ordering = ['-created_at']

    def __str__(self):
        return f'Personalización {self.jewelry_type} - {self.user.email}'
