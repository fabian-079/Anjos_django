import csv
import io
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from adapters.api.decorators import admin_required
from infrastructure.models import Category, Product, User, Role


# ---------------------------------------------------------------------------
# Helpers: datos predefinidos
# ---------------------------------------------------------------------------

def _seed_categories():
    categories_data = [
        {'name': 'Anillos',   'description': 'Anillos de oro, plata y piedras preciosas'},
        {'name': 'Collares',  'description': 'Collares elegantes y modernos'},
        {'name': 'Pulseras',  'description': 'Pulseras de diversos materiales'},
        {'name': 'Aretes',    'description': 'Aretes para toda ocasión'},
        {'name': 'Relojes',   'description': 'Relojes de lujo'},
        {'name': 'Dijes',     'description': 'Dijes y accesorios'},
    ]
    created = 0
    for cat in categories_data:
        _, was_created = Category.objects.get_or_create(
            name=cat['name'],
            defaults={'description': cat['description'], 'is_active': True},
        )
        if was_created:
            created += 1
    return len(categories_data), created


def _seed_products():
    categories = {cat.name: cat for cat in Category.objects.all()}
    products_data = [
        {'name': 'Anillo de Compromiso Diamante', 'description': 'Hermoso anillo de compromiso con diamante central de 1 quilate', 'price': Decimal('2500000.00'), 'stock': 5,  'category': categories.get('Anillos'),  'material': 'Oro blanco 18k',   'color': 'Plateado', 'finish': 'Pulido', 'stones': 'Diamante',  'is_featured': True},
        {'name': 'Anillo de Oro Rosa',             'description': 'Elegante anillo de oro rosa con detalles grabados',              'price': Decimal('980000.00'),  'stock': 12, 'category': categories.get('Anillos'),  'material': 'Oro rosa 14k',     'color': 'Rosa',     'finish': 'Mate',   'is_featured': False},
        {'name': 'Collar de Perlas',               'description': 'Elegante collar de perlas naturales',                            'price': Decimal('850000.00'),  'stock': 10, 'category': categories.get('Collares'), 'material': 'Perlas naturales', 'color': 'Blanco',   'finish': 'Natural','is_featured': True},
        {'name': 'Collar de Oro con Zafiro',       'description': 'Collar de oro amarillo con zafiro azul central',                 'price': Decimal('1650000.00'), 'stock': 7,  'category': categories.get('Collares'), 'material': 'Oro amarillo 18k', 'color': 'Azul',     'finish': 'Pulido', 'stones': 'Zafiro',   'is_featured': True},
        {'name': 'Pulsera de Oro',                 'description': 'Pulsera clásica de oro amarillo',                                'price': Decimal('1200000.00'), 'stock': 8,  'category': categories.get('Pulseras'), 'material': 'Oro amarillo 14k', 'color': 'Dorado',   'finish': 'Pulido', 'is_featured': True},
        {'name': 'Pulsera de Plata con Dijes',     'description': 'Pulsera de plata 925 con dijes intercambiables',                 'price': Decimal('450000.00'),  'stock': 15, 'category': categories.get('Pulseras'), 'material': 'Plata 925',        'color': 'Plateado', 'finish': 'Pulido', 'is_featured': False},
        {'name': 'Aretes de Esmeralda',            'description': 'Aretes con esmeraldas colombianas',                              'price': Decimal('1800000.00'), 'stock': 6,  'category': categories.get('Aretes'),   'material': 'Oro blanco 18k',   'color': 'Verde',    'finish': 'Pulido', 'stones': 'Esmeralda','is_featured': True},
        {'name': 'Aretes de Perla',                'description': 'Aretes clásicos de perla cultivada',                             'price': Decimal('320000.00'),  'stock': 18, 'category': categories.get('Aretes'),   'material': 'Oro amarillo 14k', 'color': 'Blanco',   'finish': 'Pulido', 'stones': 'Perla',    'is_featured': False},
        {'name': 'Reloj Clásico',                  'description': 'Reloj de lujo con movimiento suizo',                             'price': Decimal('3500000.00'), 'stock': 3,  'category': categories.get('Relojes'),  'material': 'Acero inoxidable', 'color': 'Plateado', 'finish': 'Pulido'},
        {'name': 'Reloj de Oro para Dama',         'description': 'Reloj elegante de oro con esfera de nácar',                      'price': Decimal('4200000.00'), 'stock': 2,  'category': categories.get('Relojes'),  'material': 'Oro amarillo 18k', 'color': 'Dorado',   'finish': 'Pulido', 'is_featured': True},
        {'name': 'Dije Corazón',                   'description': 'Dije en forma de corazón con zirconia',                          'price': Decimal('180000.00'),  'stock': 20, 'category': categories.get('Dijes'),    'material': 'Plata 925',        'color': 'Plateado', 'finish': 'Pulido', 'stones': 'Zirconia'},
        {'name': 'Dije Infinito',                  'description': 'Dije símbolo de infinito en oro blanco',                         'price': Decimal('550000.00'),  'stock': 14, 'category': categories.get('Dijes'),    'material': 'Oro blanco 14k',   'color': 'Plateado', 'finish': 'Pulido', 'is_featured': False},
    ]
    total = 0
    created = 0
    for prod in products_data:
        if prod.get('category'):
            _, was_created = Product.objects.get_or_create(name=prod['name'], defaults=prod)
            total += 1
            if was_created:
                created += 1
    return total, created


def _seed_users():
    cliente_role, _ = Role.objects.get_or_create(name='cliente')
    test_users = [
        {'email': 'cliente@test.com', 'name': 'Cliente Prueba', 'password': 'cliente123', 'role': cliente_role},
    ]
    created = 0
    for u in test_users:
        if not User.objects.filter(email=u['email']).exists():
            user = User.objects.create_user(email=u['email'], name=u['name'], password=u['password'])
            user.roles.add(u['role'])
            created += 1
    return len(test_users), created


# ---------------------------------------------------------------------------
# Helpers: parseo de archivos
# ---------------------------------------------------------------------------

def _parse_csv(uploaded_file):
    content = uploaded_file.read().decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(content))
    return [row for row in reader]


def _parse_excel(uploaded_file):
    try:
        import openpyxl
    except ImportError:
        raise ImportError('openpyxl no está instalado. Ejecuta: pip install openpyxl')
    wb = openpyxl.load_workbook(uploaded_file, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.rows)
    if not rows:
        return []
    headers = [str(cell.value).strip() if cell.value is not None else '' for cell in rows[0]]
    result = []
    for row in rows[1:]:
        values = [cell.value for cell in row]
        if any(v is not None for v in values):
            result.append(dict(zip(headers, values)))
    wb.close()
    return result


def _get(row, *keys, default=''):
    """Fetch the first matching key (supports Spanish and English column names)"""
    for k in keys:
        if k in row and row[k] is not None:
            return str(row[k])
    return default


def _import_categories(rows):
    created = 0
    errors = []
    for i, row in enumerate(rows, start=2):
        name = _get(row, 'nombre', 'name').strip()
        if not name:
            errors.append(f'Fila {i}: el campo "nombre" es requerido.')
            continue
        description = _get(row, 'descripcion', 'descripción', 'description').strip()
        is_active_raw = _get(row, 'activo', 'is_active', default='True').strip().lower()
        is_active = is_active_raw in ('true', '1', 'si', 'sí', 'yes')
        _, was_created = Category.objects.get_or_create(
            name=name,
            defaults={'description': description, 'is_active': is_active},
        )
        if was_created:
            created += 1
    return created, errors


def _import_products(rows):
    created = 0
    errors = []
    categories = {cat.name.lower(): cat for cat in Category.objects.all()}
    for i, row in enumerate(rows, start=2):
        name = _get(row, 'nombre', 'name').strip()
        if not name:
            errors.append(f'Fila {i}: el campo "nombre" es requerido.')
            continue
        category_name = _get(row, 'categoria', 'categoría', 'category').strip()
        category = categories.get(category_name.lower())
        if not category:
            errors.append(f'Fila {i} ("{name}"): categoría "{category_name}" no encontrada.')
            continue
        try:
            price = Decimal(_get(row, 'precio', 'price', default='0').replace(',', '.'))
        except InvalidOperation:
            errors.append(f'Fila {i} ("{name}"): precio inválido.')
            continue
        try:
            stock = int(_get(row, 'stock', default='0').split('.')[0])
        except ValueError:
            stock = 0
        is_featured = _get(row, 'destacado', 'is_featured').strip().lower() in ('true', '1', 'si', 'sí', 'yes')
        is_active = _get(row, 'activo', 'is_active', default='True').strip().lower() in ('true', '1', 'si', 'sí', 'yes')
        defaults = {
            'description': _get(row, 'descripcion', 'descripción', 'description').strip(),
            'price': price,
            'stock': stock,
            'category': category,
            'material': _get(row, 'material').strip() or None,
            'color': _get(row, 'color').strip() or None,
            'finish': _get(row, 'acabado', 'finish').strip() or None,
            'stones': _get(row, 'piedras', 'stones').strip() or None,
            'size': _get(row, 'talla', 'size').strip() or None,
            'is_featured': is_featured,
            'is_active': is_active,
        }
        _, was_created = Product.objects.get_or_create(name=name, defaults=defaults)
        if was_created:
            created += 1
    return created, errors


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

@admin_required
def seeder_form(request):
    """Página principal de carga masiva de datos"""
    return render(request, 'seeder/index.html')


@admin_required
def seeder_run(request):
    """Carga predefinida de datos de prueba"""
    if request.method != 'POST':
        return redirect('seeder_form')
    sections = request.POST.getlist('sections')
    if not sections:
        messages.warning(request, 'Selecciona al menos una sección para cargar.')
        return redirect('seeder_form')
    results = []
    if 'categories' in sections:
        total, created = _seed_categories()
        results.append(f'{created} categorías nuevas (de {total} disponibles).')
    if 'products' in sections:
        total, created = _seed_products()
        results.append(f'{created} productos nuevos (de {total} disponibles).')
    if 'users' in sections:
        total, created = _seed_users()
        results.append(f'{created} usuarios de prueba nuevos (de {total} disponibles).')
    if results:
        messages.success(request, 'Carga rápida completada: ' + ' | '.join(results))
    else:
        messages.info(request, 'No se realizaron cambios (los datos ya existen).')
    return redirect('seeder_form')


@admin_required
def seeder_upload_csv(request):
    """Carga masiva desde archivo CSV o Excel"""
    if request.method != 'POST':
        return redirect('seeder_form')
    data_type = request.POST.get('data_type', '')
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        messages.error(request, 'Selecciona un archivo para cargar.')
        return redirect('seeder_form')
    if data_type not in ('categories', 'products'):
        messages.error(request, 'Tipo de datos no válido.')
        return redirect('seeder_form')
    filename = uploaded_file.name.lower()
    try:
        if filename.endswith('.csv'):
            rows = _parse_csv(uploaded_file)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            rows = _parse_excel(uploaded_file)
        else:
            messages.error(request, 'Formato no soportado. Usa CSV (.csv) o Excel (.xlsx).')
            return redirect('seeder_form')
    except Exception as e:
        messages.error(request, f'Error leyendo el archivo: {e}')
        return redirect('seeder_form')
    if not rows:
        messages.warning(request, 'El archivo está vacío o no tiene datos válidos.')
        return redirect('seeder_form')
    if data_type == 'categories':
        created, errors = _import_categories(rows)
        label = 'categorías'
    else:
        created, errors = _import_products(rows)
        label = 'productos'
    if created:
        messages.success(request, f'{created} {label} importados correctamente desde el archivo.')
    if errors:
        for err in errors[:5]:
            messages.warning(request, err)
        if len(errors) > 5:
            messages.warning(request, f'… y {len(errors) - 5} errores más.')
    if not created and not errors:
        messages.info(request, f'No se importaron {label} nuevos (ya existen todos los registros).')
    return redirect('seeder_form')


@admin_required
def seeder_template_download(request):
    """Descargar plantilla CSV para categorías o productos"""
    data_type = request.GET.get('type', 'categories')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="plantilla_{data_type}.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    if data_type == 'categories':
        writer.writerow(['nombre', 'descripcion', 'activo'])
        writer.writerow(['Anillos', 'Anillos de oro y plata', 'Si'])
        writer.writerow(['Collares', 'Collares elegantes', 'Si'])
    else:
        writer.writerow(['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'material', 'color', 'acabado', 'piedras', 'talla', 'destacado', 'activo'])
        writer.writerow(['Anillo de Ejemplo', 'Descripción del producto', '500000', '10', 'Anillos', 'Oro 18k', 'Dorado', 'Pulido', '', '', 'Si', 'Si'])
        writer.writerow(['Collar de Ejemplo', 'Otro producto de muestra', '350000', '5', 'Collares', 'Plata 925', 'Plateado', 'Pulido', 'Zirconia', '', 'No', 'Si'])
    return response
