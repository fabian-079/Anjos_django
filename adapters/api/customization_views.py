from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from adapters.api.decorators import admin_required
from infrastructure.container import get_customization_usecases


@login_required
def customization_index(request):
    uc = get_customization_usecases()
    if request.user.is_admin():
        items = uc.get_all()
    else:
        items = uc.get_by_user(request.user.id)
    return render(request, 'personalizacion/index.html', {'customizations': items})


@login_required
def customization_show(request, pk):
    item = get_customization_usecases().get_by_id(pk)
    if not item:
        messages.error(request, 'Personalización no encontrada.')
        return redirect('customization_index')
    if not request.user.is_admin() and item.user_id != request.user.id:
        messages.error(request, 'Sin permiso.')
        return redirect('customization_index')
    return render(request, 'personalizacion/show.html', {'customization': item})


@login_required
def customization_create_form(request):
    return render(request, 'personalizacion/create.html')


@login_required
def customization_create(request):
    if request.method != 'POST':
        return redirect('customization_index')
    uc = get_customization_usecases()
    try:
        uc.create(
            user_id=request.user.id,
            jewelry_type=request.POST.get('jewelry_type', '').strip(),
            design=request.POST.get('design', '').strip(),
            stones=request.POST.get('stones', '').strip(),
            finish=request.POST.get('finish', '').strip(),
            color=request.POST.get('color', '').strip(),
            material=request.POST.get('material', '').strip(),
            size=request.POST.get('size', '').strip() or None,
            engraving=request.POST.get('engraving', '').strip() or None,
            special_instructions=request.POST.get('special_instructions', '').strip() or None,
        )
        messages.success(request, 'Personalización enviada exitosamente.')
        return redirect('customization_index')
    except Exception as e:
        messages.error(request, f'Error: {e}')
        return render(request, 'personalizacion/create.html')


@login_required
def customization_edit_form(request, pk):
    uc = get_customization_usecases()
    item = uc.get_by_id(pk)
    if not item:
        messages.error(request, 'Personalización no encontrada.')
        return redirect('customization_index')
    if not request.user.is_admin() and item.user_id != request.user.id:
        messages.error(request, 'Sin permiso.')
        return redirect('customization_index')
    return render(request, 'personalizacion/edit.html', {'customization': item})


@login_required
def customization_update(request, pk):
    if request.method != 'POST':
        return redirect('customization_index')
    uc = get_customization_usecases()
    try:
        from decimal import Decimal
        ep_str = request.POST.get('estimated_price', '').strip()
        status = request.POST.get('status') if request.user.is_admin() else None
        admin_notes = request.POST.get('admin_notes', '').strip() if request.user.is_admin() else None
        uc.update(
            customization_id=pk,
            jewelry_type=request.POST.get('jewelry_type', '').strip(),
            design=request.POST.get('design', '').strip(),
            stones=request.POST.get('stones', '').strip(),
            finish=request.POST.get('finish', '').strip(),
            color=request.POST.get('color', '').strip(),
            material=request.POST.get('material', '').strip(),
            size=request.POST.get('size', '').strip() or None,
            engraving=request.POST.get('engraving', '').strip() or None,
            special_instructions=request.POST.get('special_instructions', '').strip() or None,
            estimated_price=Decimal(ep_str) if ep_str else None,
            status=status,
            admin_notes=admin_notes,
        )
        messages.success(request, 'Personalización actualizada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('customization_show', pk=pk)


@admin_required
def customization_delete(request, pk):
    if request.method == 'POST':
        try:
            get_customization_usecases().deactivate(pk)
            messages.success(request, 'Personalización desactivada.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('customization_index')
