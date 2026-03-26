import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from adapters.api.decorators import admin_required
from infrastructure.container import get_repair_usecases, get_user_usecases
from domain.entities.repair import RepairStatus


@login_required
def repair_index(request):
    uc = get_repair_usecases()
    if request.user.is_admin():
        repairs = uc.get_all()
    else:
        repairs = uc.get_by_user(request.user.id)
    return render(request, 'reparaciones/index.html', {'repairs': repairs})


@login_required
def repair_show(request, pk):
    repair = get_repair_usecases().get_by_id(pk)
    if not repair:
        messages.error(request, 'Reparación no encontrada.')
        return redirect('repair_index')
    if not request.user.is_admin() and repair.user_id != request.user.id:
        messages.error(request, 'Sin permiso.')
        return redirect('repair_index')
    return render(request, 'reparaciones/show.html', {'repair': repair})


@login_required
def repair_create_form(request):
    return render(request, 'reparaciones/create.html')


@login_required
def repair_create(request):
    if request.method != 'POST':
        return redirect('repair_index')
    uc = get_repair_usecases()
    try:
        image_path = _handle_image(request)
        uc.create(
            user_id=request.user.id,
            customer_name=request.POST.get('customer_name', '').strip(),
            description=request.POST.get('description', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            image=image_path,
            notes=request.POST.get('notes', '').strip() or None,
        )
        messages.success(request, 'Solicitud de reparación enviada exitosamente.')
        return redirect('repair_index')
    except Exception as e:
        messages.error(request, f'Error: {e}')
        return render(request, 'reparaciones/create.html')


@admin_required
def repair_edit_form(request, pk):
    repair = get_repair_usecases().get_by_id(pk)
    if not repair:
        messages.error(request, 'Reparación no encontrada.')
        return redirect('repair_index')
    users = get_user_usecases().get_all_users()
    return render(request, 'reparaciones/edit.html', {
        'repair': repair,
        'status_choices': RepairStatus.CHOICES,
        'users': users,
    })


@admin_required
def repair_update(request, pk):
    if request.method != 'POST':
        return redirect('repair_index')
    uc = get_repair_usecases()
    try:
        from decimal import Decimal
        estimated_cost_str = request.POST.get('estimated_cost', '').strip()
        image_path = _handle_image(request)
        uc.update(
            repair_id=pk,
            customer_name=request.POST.get('customer_name', '').strip(),
            description=request.POST.get('description', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            status=request.POST.get('status', 'PENDING'),
            estimated_cost=Decimal(estimated_cost_str) if estimated_cost_str else None,
            technician_notes=request.POST.get('technician_notes', '').strip() or None,
            notes=request.POST.get('notes', '').strip() or None,
            image=image_path,
        )
        messages.success(request, 'Reparación actualizada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('repair_show', pk=pk)


@admin_required
def repair_assign(request, pk):
    if request.method == 'POST':
        technician_id = request.POST.get('technician_id')
        try:
            get_repair_usecases().assign_technician(pk, int(technician_id))
            messages.success(request, 'Técnico asignado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('repair_show', pk=pk)


@admin_required
def repair_delete(request, pk):
    if request.method == 'POST':
        try:
            get_repair_usecases().deactivate(pk)
            messages.success(request, 'Reparación desactivada.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('repair_index')


def _handle_image(request):
    image_file = request.FILES.get('image_file')
    if not image_file:
        return None
    from django.conf import settings
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'repairs')
    os.makedirs(upload_dir, exist_ok=True)
    filename = image_file.name
    with open(os.path.join(upload_dir, filename), 'wb+') as f:
        for chunk in image_file.chunks():
            f.write(chunk)
    return f'/uploads/repairs/{filename}'
