from django.contrib import messages
from django.shortcuts import render, redirect
from adapters.api.decorators import admin_required
from infrastructure.container import get_category_usecases


@admin_required
def category_index(request):
    return render(request, 'categories/index.html', {
        'categories': get_category_usecases().get_all(),
    })


@admin_required
def category_create_form(request):
    return render(request, 'categories/create.html')


@admin_required
def category_create(request):
    if request.method != 'POST':
        return redirect('category_index')
    uc = get_category_usecases()
    try:
        uc.create(
            name=request.POST.get('name', '').strip(),
            description=request.POST.get('description', '').strip() or None,
            image=request.POST.get('image', '').strip() or None,
            is_active=request.POST.get('is_active', 'true') == 'true',
        )
        messages.success(request, 'Categoría creada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('category_index')


@admin_required
def category_edit_form(request, pk):
    uc = get_category_usecases()
    category = uc.get_by_id(pk)
    if not category:
        messages.error(request, 'Categoría no encontrada.')
        return redirect('category_index')
    return render(request, 'categories/edit.html', {'category': category})


@admin_required
def category_update(request, pk):
    if request.method != 'POST':
        return redirect('category_index')
    uc = get_category_usecases()
    try:
        uc.update(
            category_id=pk,
            name=request.POST.get('name', '').strip(),
            description=request.POST.get('description', '').strip() or None,
            image=request.POST.get('image', '').strip() or None,
            is_active=request.POST.get('is_active', 'true') == 'true',
        )
        messages.success(request, 'Categoría actualizada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('category_index')


@admin_required
def category_delete(request, pk):
    if request.method == 'POST':
        try:
            get_category_usecases().deactivate(pk)
            messages.success(request, 'Categoría desactivada exitosamente.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('category_index')
