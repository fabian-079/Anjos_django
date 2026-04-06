from django.conf import settings
from django.db import models
from infrastructure.models.product_model import Product


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='favorites', null=True, blank=True
    )
    customization = models.ForeignKey(
        'infrastructure.Customization', on_delete=models.CASCADE,
        related_name='favorites', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'infrastructure'
        db_table = 'favorites'

    def __str__(self):
        if self.product:
            return f'{self.user.email} - {self.product.name}'
        return f'{self.user.email} - customization {self.customization_id}'
