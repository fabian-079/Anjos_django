from django.db import models
from infrastructure.models.category_model import Category


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    material = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    finish = models.CharField(max_length=100, null=True, blank=True)
    stones = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    image = models.CharField(max_length=500, null=True, blank=True)
    gallery = models.JSONField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'infrastructure'
        db_table = 'products'

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            if self.image.startswith('http'):
                return self.image
            return self.image
        if self.category:
            cat = self.category.name.lower()
            if 'anillo' in cat:
                return 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&h=800&fit=crop'
            elif 'collar' in cat:
                return 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&h=800&fit=crop'
            elif 'pulsera' in cat:
                return 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&h=800&fit=crop'
            elif 'arete' in cat:
                return 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&h=800&fit=crop'
            elif 'reloj' in cat:
                return 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=800&fit=crop'
            elif 'dije' in cat:
                return 'https://images.unsplash.com/photo-1603561596111-7c8cd67663aa?w=800&h=800&fit=crop'
        return 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&h=800&fit=crop'
