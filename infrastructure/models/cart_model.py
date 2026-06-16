from django.conf import settings
from django.db import models
from infrastructure.models.product_model import Product


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'infrastructure'
        db_table = 'cart_items'
        unique_together = [('user', 'product')]

    def __str__(self):
        return f'{self.user.email} - {self.product.name} x{self.quantity}'

    @property
    def subtotal(self):
        return self.product.price * self.quantity
