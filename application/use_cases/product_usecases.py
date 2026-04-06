from decimal import Decimal
from typing import List, Optional
from domain.entities.product import ProductEntity
from domain.repositories.product_repository import ProductRepository
from domain.repositories.category_repository import CategoryRepository

class ProductUseCases:
    def __init__(self, product_repo: ProductRepository, category_repo: CategoryRepository):
        self._repo = product_repo
        self._category_repo = category_repo

    def get_all_products(self) -> List[ProductEntity]:
        return self._repo.find_all()

    
    def get_product_by_id(self, product_id: int) -> Optional[ProductEntity]:
        return self._repo.find_by_id(product_id)

    def get_featured_products(self) -> List[ProductEntity]:
        return self._repo.find_featured()

    def get_products_by_category(self, category_id: int) -> List[ProductEntity]:
        return self._repo.find_by_category(category_id)

    def search_products(self, category_id=None, material=None, color=None,
                        finish=None, stones=None, min_price=None, max_price=None,
                        search=None, page=1, page_size=12):
        return self._repo.search(
            category_id=category_id, material=material, color=color,
            finish=finish, stones=stones, min_price=min_price,
            max_price=max_price, search=search, page=page, page_size=page_size
        )

    def get_related_products(self, category_id: int, product_id: int, limit: int = 4) -> List[ProductEntity]:
        return self._repo.find_related(category_id, product_id, limit)

    def create_product(self, name: str, description: str, price: Decimal,
                       stock: int, category_id: int, material=None, color=None,
                       finish=None, stones=None, size=None, image=None,
                       is_featured=False, is_active=True) -> ProductEntity:
        category = self._category_repo.find_by_id(category_id)
        if not category:
            raise ValueError(f'Categoría no encontrada con id: {category_id}')
        product = ProductEntity(
            name=name, description=description, price=price, stock=stock,
            category_id=category_id, category_name=category.name,
            material=material, color=color, finish=finish, stones=stones,
            size=size, image=image, is_featured=is_featured, is_active=is_active,
        )
        return self._repo.save(product)

    def update_product(self, product_id: int, name: str, description: str,
                       price: Decimal, stock: int, category_id: int,
                       material=None, color=None, finish=None, stones=None,
                       size=None, image=None, is_featured=False, is_active=True) -> ProductEntity:
        product = self._repo.find_by_id(product_id)
        if not product:
            raise ValueError(f'Producto no encontrado con id: {product_id}')
        category = self._category_repo.find_by_id(category_id)
        if not category:
            raise ValueError(f'Categoría no encontrada con id: {category_id}')
        product.name = name
        product.description = description
        product.price = price
        product.stock = stock
        product.category_id = category_id
        product.category_name = category.name
        product.material = material
        product.color = color
        product.finish = finish
        product.stones = stones
        product.size = size
        product.is_featured = is_featured
        product.is_active = is_active
        if image:
            product.image = image
        return self._repo.save(product)

    def deactivate_product(self, product_id: int) -> None:
        product = self._repo.find_by_id(product_id)
        if not product:
            raise ValueError(f'Producto no encontrado con id: {product_id}')
        product.is_active = False
        self._repo.save(product)

    def get_distinct_materials(self) -> List[str]:
        return self._repo.find_distinct_materials()

    def get_distinct_colors(self) -> List[str]:
        return self._repo.find_distinct_colors()

    def get_distinct_finishes(self) -> List[str]:
        return self._repo.find_distinct_finishes()

    def get_distinct_stones(self) -> List[str]:
        return self._repo.find_distinct_stones()
