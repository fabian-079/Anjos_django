#!/usr/bin/env python
"""
Script para inicializar la base de datos con datos de prueba
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from infrastructure.models import Category, Product, User, Role
from decimal import Decimal


def create_categories():
    """Crear categorías de productos"""
    categories_data = [
        {'name': 'Anillos', 'description': 'Anillos de oro, plata y piedras preciosas'},
        {'name': 'Collares', 'description': 'Collares elegantes y modernos'},
        {'name': 'Pulseras', 'description': 'Pulseras de diversos materiales'},
        {'name': 'Aretes', 'description': 'Aretes para toda ocasión'},
        {'name': 'Relojes', 'description': 'Relojes de lujo'},
        {'name': 'Dijes', 'description': 'Dijes y accesorios'},
    ]
    
    for cat_data in categories_data:
        Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description'], 'is_active': True}
        )
    print(f"✓ {len(categories_data)} categorías creadas")


def create_sample_products():
    """Crear productos de ejemplo"""
    categories = {cat.name: cat for cat in Category.objects.all()}
    
    products_data = [
        # Anillos
        {
            'name': 'Anillo de Compromiso Diamante',
            'description': 'Hermoso anillo de compromiso con diamante central de 1 quilate',
            'price': Decimal('2500000.00'),
            'stock': 5,
            'category': categories.get('Anillos'),
            'material': 'Oro blanco 18k',
            'color': 'Plateado',
            'finish': 'Pulido',
            'stones': 'Diamante',
            'is_featured': True,
        },
        {
            'name': 'Anillo de Oro Rosa',
            'description': 'Elegante anillo de oro rosa con detalles grabados',
            'price': Decimal('980000.00'),
            'stock': 12,
            'category': categories.get('Anillos'),
            'material': 'Oro rosa 14k',
            'color': 'Rosa',
            'finish': 'Mate',
            'is_featured': False,
        },
        # Collares
        {
            'name': 'Collar de Perlas',
            'description': 'Elegante collar de perlas naturales',
            'price': Decimal('850000.00'),
            'stock': 10,
            'category': categories.get('Collares'),
            'material': 'Perlas naturales',
            'color': 'Blanco',
            'finish': 'Natural',
            'is_featured': True,
        },
        {
            'name': 'Collar de Oro con Zafiro',
            'description': 'Collar de oro amarillo con zafiro azul central',
            'price': Decimal('1650000.00'),
            'stock': 7,
            'category': categories.get('Collares'),
            'material': 'Oro amarillo 18k',
            'color': 'Azul',
            'finish': 'Pulido',
            'stones': 'Zafiro',
            'is_featured': True,
        },
        # Pulseras
        {
            'name': 'Pulsera de Oro',
            'description': 'Pulsera clásica de oro amarillo',
            'price': Decimal('1200000.00'),
            'stock': 8,
            'category': categories.get('Pulseras'),
            'material': 'Oro amarillo 14k',
            'color': 'Dorado',
            'finish': 'Pulido',
            'is_featured': True,
        },
        {
            'name': 'Pulsera de Plata con Dijes',
            'description': 'Pulsera de plata 925 con dijes intercambiables',
            'price': Decimal('450000.00'),
            'stock': 15,
            'category': categories.get('Pulseras'),
            'material': 'Plata 925',
            'color': 'Plateado',
            'finish': 'Pulido',
            'is_featured': False,
        },
        # Aretes
        {
            'name': 'Aretes de Esmeralda',
            'description': 'Aretes con esmeraldas colombianas',
            'price': Decimal('1800000.00'),
            'stock': 6,
            'category': categories.get('Aretes'),
            'material': 'Oro blanco 18k',
            'color': 'Verde',
            'finish': 'Pulido',
            'stones': 'Esmeralda',
            'is_featured': True,
        },
        {
            'name': 'Aretes de Perla',
            'description': 'Aretes clásicos de perla cultivada',
            'price': Decimal('320000.00'),
            'stock': 18,
            'category': categories.get('Aretes'),
            'material': 'Oro amarillo 14k',
            'color': 'Blanco',
            'finish': 'Pulido',
            'stones': 'Perla',
            'is_featured': False,
        },
        # Relojes
        {
            'name': 'Reloj Clásico',
            'description': 'Reloj de lujo con movimiento suizo',
            'price': Decimal('3500000.00'),
            'stock': 3,
            'category': categories.get('Relojes'),
            'material': 'Acero inoxidable',
            'color': 'Plateado',
            'finish': 'Pulido',
        },
        {
            'name': 'Reloj de Oro para Dama',
            'description': 'Reloj elegante de oro con esfera de nácar',
            'price': Decimal('4200000.00'),
            'stock': 2,
            'category': categories.get('Relojes'),
            'material': 'Oro amarillo 18k',
            'color': 'Dorado',
            'finish': 'Pulido',
            'is_featured': True,
        },
        # Dijes
        {
            'name': 'Dije Corazón',
            'description': 'Dije en forma de corazón con zirconia',
            'price': Decimal('180000.00'),
            'stock': 20,
            'category': categories.get('Dijes'),
            'material': 'Plata 925',
            'color': 'Plateado',
            'finish': 'Pulido',
            'stones': 'Zirconia',
        },
        {
            'name': 'Dije Infinito',
            'description': 'Dije símbolo de infinito en oro blanco',
            'price': Decimal('550000.00'),
            'stock': 14,
            'category': categories.get('Dijes'),
            'material': 'Oro blanco 14k',
            'color': 'Plateado',
            'finish': 'Pulido',
            'is_featured': False,
        },
    ]
    
    created = 0
    for prod_data in products_data:
        if prod_data['category']:
            Product.objects.get_or_create(
                name=prod_data['name'],
                defaults=prod_data
            )
            created += 1
    
    print(f"✓ {created} productos de ejemplo creados")


def create_test_users():
    """Crear usuarios de prueba"""
    cliente_role, _ = Role.objects.get_or_create(name='cliente')
    
    test_users = [
        {
            'email': 'cliente@test.com',
            'name': 'Cliente Prueba',
            'password': 'cliente123',
            'role': cliente_role,
        },
    ]
    
    for user_data in test_users:
        if not User.objects.filter(email=user_data['email']).exists():
            user = User.objects.create_user(
                email=user_data['email'],
                name=user_data['name'],
                password=user_data['password'],
            )
            user.roles.add(user_data['role'])
            print(f"✓ Usuario creado: {user_data['email']} / {user_data['password']}")


def main():
    print("Inicializando base de datos con datos de prueba...\n")
    
    create_categories()
    create_sample_products()
    create_test_users()
    
    print("\n✓ Base de datos inicializada correctamente")
    print("\nCredenciales de acceso:")
    print("  Admin: admin@anjos.com / admin123")
    print("  Cliente: cliente@test.com / cliente123")


if __name__ == '__main__':
    main()
