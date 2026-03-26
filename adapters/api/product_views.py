import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from adapters.api.decorators import admin_required
from infrastructure.container import (
    get_product_usecases, get_category_usecases,
    get_cart_usecases, get_favorite_usecases,
)


@admin_required
def product_index(request):
    products_uc = get_product_usecases()
    categories_uc = get_category_usecases()
    return render(request, 'products/index.html', {
        'products': products_uc.get_all_products(),
        'categories': categories_uc.get_active(),
    })


@admin_required
def product_create_form(request):
    categories_uc = get_category_usecases()
    return render(request, 'products/create.html', {
        'categories': categories_uc.get_active(),
    })


@admin_required
def product_create(request):
    if request.method != 'POST':
        return redirect('product_index')
    products_uc = get_product_usecases()
    categories_uc = get_category_usecases()
    try:
        from decimal import Decimal
        category_id = request.POST.get('category_id')
        image_path = _handle_image(request)
        products_uc.create_product(
            name=request.POST.get('name', '').strip(),
            description=request.POST.get('description', '').strip(),
            price=Decimal(request.POST.get('price', '0')),
            stock=int(request.POST.get('stock', 0)),
            category_id=int(category_id) if category_id else None,
            material=request.POST.get('material') or None,
            color=request.POST.get('color') or None,
            finish=request.POST.get('finish') or None,
            stones=request.POST.get('stones') or None,
            size=request.POST.get('size') or None,
            image=image_path or request.POST.get('image') or None,
            is_featured=bool(request.POST.get('is_featured')),
            is_active=request.POST.get('is_active', 'true') == 'true',
        )
        messages.success(request, 'Producto creado exitosamente.')
        return redirect('product_index')
    except Exception as e:
        messages.error(request, f'Error al crear producto: {e}')
        return render(request, 'products/create.html', {
            'categories': categories_uc.get_active(),
        })


@admin_required
def product_edit_form(request, pk):
    products_uc = get_product_usecases()
    categories_uc = get_category_usecases()
    product = products_uc.get_product_by_id(pk)
    if not product:
        messages.error(request, 'Producto no encontrado.')
        return redirect('product_index')
    return render(request, 'products/edit.html', {
        'product': product,
        'categories': categories_uc.get_active(),
    })


@admin_required
def product_update(request, pk):
    if request.method != 'POST':
        return redirect('product_index')
    products_uc = get_product_usecases()
    categories_uc = get_category_usecases()
    try:
        from decimal import Decimal
        category_id = request.POST.get('category_id')
        image_path = _handle_image(request)
        products_uc.update_product(
            product_id=pk,
            name=request.POST.get('name', '').strip(),
            description=request.POST.get('description', '').strip(),
            price=Decimal(request.POST.get('price', '0')),
            stock=int(request.POST.get('stock', 0)),
            category_id=int(category_id) if category_id else None,
            material=request.POST.get('material') or None,
            color=request.POST.get('color') or None,
            finish=request.POST.get('finish') or None,
            stones=request.POST.get('stones') or None,
            size=request.POST.get('size') or None,
            image=image_path or request.POST.get('image') or None,
            is_featured=bool(request.POST.get('is_featured')),
            is_active=request.POST.get('is_active', 'true') == 'true',
        )
        messages.success(request, 'Producto actualizado exitosamente.')
        return redirect('product_index')
    except Exception as e:
        messages.error(request, f'Error al actualizar producto: {e}')
        product = products_uc.get_product_by_id(pk)
        return render(request, 'products/edit.html', {
            'product': product,
            'categories': categories_uc.get_active(),
        })


@admin_required
def product_delete(request, pk):
    if request.method == 'POST':
        try:
            get_product_usecases().deactivate_product(pk)
            messages.success(request, 'Producto desactivado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('product_index')


@login_required
def add_to_cart(request, pk):
    if request.method != 'POST':
        return redirect('producto_detalle', pk=pk)
    try:
        quantity = int(request.POST.get('quantity', 1))
        get_cart_usecases().add_to_cart(request.user.id, pk, quantity)
        messages.success(request, 'Producto agregado al carrito.')
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('producto_detalle', pk=pk)


@login_required
def toggle_favorite(request, pk):
    if request.method != 'POST':
        return redirect('producto_detalle', pk=pk)
    try:
        result = get_favorite_usecases().toggle_product_favorite(request.user.id, pk)
        if result:
            messages.success(request, 'Producto agregado a favoritos.')
        else:
            messages.success(request, 'Producto removido de favoritos.')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('producto_detalle', pk=pk)


def _handle_image(request):
    image_file = request.FILES.get('image_file')
    if not image_file:
        return None
    from django.conf import settings
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'products')
    os.makedirs(upload_dir, exist_ok=True)
    filename = image_file.name
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, 'wb+') as f:
        for chunk in image_file.chunks():
            f.write(chunk)
    return f'/uploads/products/{filename}'
