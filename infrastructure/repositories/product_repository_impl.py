from decimal import Decimal
from typing import List, Optional
from django.core.paginator import Paginator
from django.db.models import Q
from domain.entities.product import ProductEntity
from domain.repositories.product_repository import ProductRepository
from infrastructure.models.product_model import Product
from infrastructure.models.category_model import Category


def _to_entity(p: Product) -> ProductEntity:
    return ProductEntity(
        id=p.id, name=p.name, description=p.description,
        price=p.price, stock=p.stock, material=p.material,
        color=p.color, finish=p.finish, stones=p.stones, size=p.size,
        image=p.image, gallery=str(p.gallery) if p.gallery else None,
        is_featured=p.is_featured, is_active=p.is_active,
        category_id=p.category_id,
        category_name=p.category.name if p.category else None,
        created_at=p.created_at, updated_at=p.updated_at,
    )


class ProductRepositoryImpl(ProductRepository):

    def find_all(self) -> List[ProductEntity]:
        return [_to_entity(p) for p in Product.objects.select_related('category').all()]

    def find_by_id(self, product_id: int) -> Optional[ProductEntity]:
        try:
            return _to_entity(Product.objects.select_related('category').get(pk=product_id))
        except Product.DoesNotExist:
            return None

    def find_by_category(self, category_id: int) -> List[ProductEntity]:
        qs = Product.objects.select_related('category').filter(
            category_id=category_id, is_active=True
        )
        return [_to_entity(p) for p in qs]

    def find_featured(self) -> List[ProductEntity]:
        qs = Product.objects.select_related('category').filter(
            is_featured=True, is_active=True
        )
        return [_to_entity(p) for p in qs]

    def search(self, category_id=None, material=None, color=None,
               finish=None, stones=None, min_price=None, max_price=None,
               search=None, page=1, page_size=12):
        qs = Product.objects.select_related('category').filter(is_active=True)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if material:
            qs = qs.filter(material__icontains=material)
        if color:
            qs = qs.filter(color__icontains=color)
        if finish:
            qs = qs.filter(finish__icontains=finish)
        if stones:
            qs = qs.filter(stones__icontains=stones)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)
        return {
            'items': [_to_entity(p) for p in page_obj.object_list],
            'total': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }

    def save(self, product: ProductEntity) -> ProductEntity:
        if product.id:
            db = Product.objects.get(pk=product.id)
            db.name = product.name
            db.description = product.description
            db.price = product.price
            db.stock = product.stock
            db.material = product.material
            db.color = product.color
            db.finish = product.finish
            db.stones = product.stones
            db.size = product.size
            db.is_featured = product.is_featured
            db.is_active = product.is_active
            if product.category_id:
                db.category_id = product.category_id
            if product.image:
                db.image = product.image
            db.save()
        else:
            db = Product.objects.create(
                name=product.name, description=product.description,
                price=product.price, stock=product.stock,
                material=product.material, color=product.color,
                finish=product.finish, stones=product.stones, size=product.size,
                image=product.image, is_featured=product.is_featured,
                is_active=product.is_active, category_id=product.category_id,
            )
        db.refresh_from_db()
        return _to_entity(db)

    def delete(self, product_id: int) -> None:
        Product.objects.filter(pk=product_id).update(is_active=False)

    def find_related(self, category_id: int, product_id: int, limit: int) -> List[ProductEntity]:
        qs = Product.objects.select_related('category').filter(
            category_id=category_id, is_active=True
        ).exclude(pk=product_id)[:limit]
        return [_to_entity(p) for p in qs]

    def find_distinct_materials(self) -> List[str]:
        return list(
            Product.objects.filter(is_active=True, material__isnull=False)
            .exclude(material='').values_list('material', flat=True).distinct()
        )

    def find_distinct_colors(self) -> List[str]:
        return list(
            Product.objects.filter(is_active=True, color__isnull=False)
            .exclude(color='').values_list('color', flat=True).distinct()
        )

    def find_distinct_finishes(self) -> List[str]:
        return list(
            Product.objects.filter(is_active=True, finish__isnull=False)
            .exclude(finish='').values_list('finish', flat=True).distinct()
        )

    def find_distinct_stones(self) -> List[str]:
        return list(
            Product.objects.filter(is_active=True, stones__isnull=False)
            .exclude(stones='').values_list('stones', flat=True).distinct()
        )
