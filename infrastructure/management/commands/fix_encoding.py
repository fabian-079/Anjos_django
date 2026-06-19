"""
Arregla problemas de codificacion (acentos y caracteres especiales)
en los nombres y descripciones de productos.

Uso:
    python manage.py fix_encoding --dry-run   (ver cambios sin aplicar)
    python manage.py fix_encoding             (aplicar cambios)
"""

from django.core.management.base import BaseCommand
from infrastructure.models import Product, Category, User


# Reemplazos especificos conocidos
# Si ves caracteres raros en la web, agregalos aqui.
_SPECIFIC_REPLACEMENTS = {
    # MySQL latin1 -> PostgreSQL UTF-8 corrompido
    '\xbe': 'ó',      # ¾ -> ó (ej: Coraz¾n -> Corazón)
    '\u2534': 'Á',    # ┴ -> Á (ej: ┴ngel -> Ángel)
    '\xdf': 'á',      # ß -> á (ej: Guardißn -> Guardián)
    '\xcb': 'Ó',      # Ë -> Ó (ej: Ëpalo -> Ópalo)
    '\xdd': 'í',      # Ý -> í (ej: RubÝ -> Rubí)
    '\xc3\x83\xc2\xb3': 'ó',
    '\xc3\x83\xc2\xa1': 'á',
    '\xc3\x83\xc2\xa9': 'é',
    '\xc3\x83\xc2\xad': 'í',
    '\xc3\x83\xc2\xb3': 'ó',
    '\xc3\x83\xc2\xba': 'ú',
    '\xc3\x83\xc2\xb1': 'ñ',
    '\xc3\x82': '',   # byte fantasma
}


def _fix_double_utf8(text):
    """
    Arregla 'Mojibake': cuando bytes UTF-8 fueron leidos como Latin-1
    y luego guardados como UTF-8 de nuevo.
    Ej: 'Ã³' (dos chars UTF-8) -> 'ó' (un char correcto)
    """
    if not text:
        return text
    try:
        # 1) Codificar el texto actual como latin-1 recupera los bytes originales
        raw_bytes = text.encode('latin-1')
        # 2) Decodificar esos bytes como UTF-8 devuelve el texto correcto
        fixed = raw_bytes.decode('utf-8')
        return fixed
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Si falla, no era doble UTF-8
        return text


def _fix_specific(text):
    """Aplica reemplazos especificos de caracteres conocidos."""
    if not text:
        return text
    for bad, good in _SPECIFIC_REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text


def _fix_text(text):
    """Intenta arreglar el texto con todas las estrategias."""
    if not text:
        return text
    original = text

    # Estrategia 1: reemplazos especificos
    text = _fix_specific(text)

    # Estrategia 2: doble UTF-8 (mojibake)
    text = _fix_double_utf8(text)

    # Estrategia 3: reintentar reemplazos especificos despues del doble UTF-8
    text = _fix_specific(text)

    return text


class Command(BaseCommand):
    help = 'Arregla caracteres corruptos (acentos) en productos, categorias y usuarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra los cambios sin aplicarlos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        mode = ' (MODO SIMULACION)' if dry_run else ''

        self.stdout.write(self.style.NOTICE(f'Arreglando codificacion{mode}...'))

        total_changed = 0
        total_items = 0

        # --- Productos ---
        self.stdout.write('\nProductos:')
        for product in Product.objects.all():
            original_name = product.name
            original_desc = product.description or ''
            original_material = product.material or ''
            original_color = product.color or ''
            original_finish = product.finish or ''
            original_stones = product.stones or ''

            product.name = _fix_text(product.name)
            product.description = _fix_text(product.description)
            product.material = _fix_text(product.material)
            product.color = _fix_text(product.color)
            product.finish = _fix_text(product.finish)
            product.stones = _fix_text(product.stones)

            changed = (
                product.name != original_name or
                product.description != original_desc or
                product.material != original_material or
                product.color != original_color or
                product.finish != original_finish or
                product.stones != original_stones
            )

            if changed:
                total_changed += 1
                if not dry_run:
                    product.save()
                self.stdout.write(
                    f'  {product.id}: {original_name!r} -> {product.name!r}'
                )

        total_items += Product.objects.count()

        # --- Categorias ---
        self.stdout.write('\nCategorias:')
        for cat in Category.objects.all():
            original = cat.name
            cat.name = _fix_text(cat.name)
            if cat.name != original:
                total_changed += 1
                if not dry_run:
                    cat.save()
                self.stdout.write(f'  {cat.id}: {original!r} -> {cat.name!r}')

        total_items += Category.objects.count()

        # --- Usuarios ---
        self.stdout.write('\nUsuarios:')
        for user in User.objects.all():
            original = user.name
            user.name = _fix_text(user.name)
            if user.name != original:
                total_changed += 1
                if not dry_run:
                    user.save()
                self.stdout.write(f'  {user.id}: {original!r} -> {user.name!r}')

        total_items += User.objects.count()

        self.stdout.write('')
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'Simulacion completa. Se cambiarian {total_changed} de {total_items} registros.'
                )
            )
            self.stdout.write('Ejecuta sin --dry-run para aplicar los cambios.')
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Listo! Se arreglaron {total_changed} de {total_items} registros.'
                )
            )
