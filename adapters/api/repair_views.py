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


TECHNICIANS = ['Carlos Mendoza', 'Luisa Fernández', 'Andrés Gómez', 'María Torres', 'Felipe Rojas']


@login_required
def repair_show(request, pk):
    repair = get_repair_usecases().get_by_id(pk)
    if not repair:
        messages.error(request, 'Reparación no encontrada.')
        return redirect('repair_index')
    if not request.user.is_admin() and repair.user_id != request.user.id:
        messages.error(request, 'Sin permiso.')
        return redirect('repair_index')
    return render(request, 'reparaciones/show.html', {'repair': repair, 'technicians': TECHNICIANS})


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
    return render(request, 'reparaciones/edit.html', {
        'repair': repair,
        'status_choices': RepairStatus.CHOICES,
        'technicians': TECHNICIANS,
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
            assigned_technician_text=request.POST.get('assigned_technician_text', '').strip() or None,
        )
        messages.success(request, 'Reparación actualizada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('repair_show', pk=pk)


@admin_required
def repair_assign(request, pk):
    if request.method == 'POST':
        technician_name = request.POST.get('technician_name', '').strip()
        try:
            uc = get_repair_usecases()
            repair = uc.get_by_id(pk)
            if repair:
                old_technician = repair.assigned_technician_text
                repair.assigned_technician_text = technician_name or None
                from infrastructure.repositories.repair_repository_impl import RepairRepositoryImpl
                from infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl
                from domain.entities.notification import NotificationEntity, NotificationType
                RepairRepositoryImpl().save(repair)
                if technician_name and technician_name != old_technician and repair.user_id:
                    NotificationRepositoryImpl().save(NotificationEntity(
                        user_id=repair.user_id, repair_id=pk,
                        message=f'Se asignó el técnico {technician_name} a tu reparación N° {repair.repair_number}',
                        notification_type=NotificationType.REPAIR_UPDATE,
                    ))
                messages.success(request, 'Técnico asignado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('repair_show', pk=pk)


@login_required
def repair_respond_cost(request, pk):
    if request.method != 'POST':
        return redirect('repair_show', pk=pk)
    repair = get_repair_usecases().get_by_id(pk)
    if not repair or repair.user_id != request.user.id:
        messages.error(request, 'Sin permiso.')
        return redirect('repair_index')
    if not repair.estimated_cost:
        messages.error(request, 'No hay costo estimado para responder.')
        return redirect('repair_show', pk=pk)
    accepted = request.POST.get('response') == 'accept'
    try:
        from infrastructure.repositories.repair_repository_impl import RepairRepositoryImpl
        from infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl
        from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
        from domain.entities.notification import NotificationEntity, NotificationType
        from domain.entities.repair import RepairStatus
        repair.cost_accepted = accepted
        repair.status = RepairStatus.IN_PROGRESS if accepted else RepairStatus.QUOTED
        RepairRepositoryImpl().save(repair)
        label = 'aceptado' if accepted else 'rechazado'
        admins = UserRepositoryImpl().find_admins()
        for admin in admins:
            NotificationRepositoryImpl().save(NotificationEntity(
                user_id=admin.id, repair_id=pk,
                message=f'El cliente {request.user.name} ha {label} el costo estimado de ${repair.estimated_cost:,.0f} de la reparación N° {repair.repair_number}',
                notification_type=NotificationType.REPAIR_UPDATE,
            ))
        messages.success(request, f'Has {label} el costo estimado.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('repair_show', pk=pk)


@login_required
def repair_negotiate(request, pk):
    if request.method != 'POST':
        return redirect('repair_show', pk=pk)
    repair = get_repair_usecases().get_by_id(pk)
    if not repair or repair.user_id != request.user.id:
        messages.error(request, 'Sin permiso.')
        return redirect('repair_index')
    counter_offer_raw = request.POST.get('counter_offer', '').strip()
    note = request.POST.get('negotiation_note', '').strip()
    if not counter_offer_raw:
        messages.error(request, 'Debes indicar un monto propuesto.')
        return redirect('repair_show', pk=pk)
    try:
        from decimal import Decimal
        from infrastructure.repositories.repair_repository_impl import RepairRepositoryImpl
        from infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl
        from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
        from domain.entities.notification import NotificationEntity, NotificationType
        repair.client_counter_offer = Decimal(counter_offer_raw.replace(',', '.'))
        repair.client_negotiation_note = note or None
        repair.cost_accepted = False
        RepairRepositoryImpl().save(repair)
        admins = UserRepositoryImpl().find_admins()
        for admin in admins:
            NotificationRepositoryImpl().save(NotificationEntity(
                user_id=admin.id, repair_id=pk,
                message=f'El cliente {request.user.name} propone ${repair.client_counter_offer:,.0f} para la reparación N° {repair.repair_number}' + (f': "{note}"' if note else ''),
                notification_type=NotificationType.REPAIR_UPDATE,
            ))
        messages.success(request, 'Tu contrapropuesta fue enviada al equipo.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('repair_show', pk=pk)


@admin_required
def repair_respond_counter(request, pk):
    if request.method != 'POST':
        return redirect('repair_show', pk=pk)
    try:
        from infrastructure.repositories.repair_repository_impl import RepairRepositoryImpl
        from infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl
        from domain.entities.notification import NotificationEntity, NotificationType
        repair = get_repair_usecases().get_by_id(pk)
        if not repair or not repair.client_counter_offer:
            messages.error(request, 'No hay contrapropuesta para responder.')
            return redirect('repair_show', pk=pk)
        accepted = request.POST.get('response') == 'accept'
        if accepted:
            repair.estimated_cost = repair.client_counter_offer
            repair.cost_accepted = True
            repair.client_counter_offer = None
            repair.client_negotiation_note = None
            repair.status = 'IN_PROGRESS'
            msg_cliente = f'¡Buenas noticias! Tu propuesta de ${repair.estimated_cost:,.0f} para la reparación N° {repair.repair_number} fue aceptada.'
            flash = 'Contrapropuesta aceptada. El costo fue actualizado.'
        else:
            repair.client_counter_offer = None
            repair.client_negotiation_note = None
            repair.cost_accepted = None
            repair.status = 'QUOTED'
            msg_cliente = f'Tu propuesta para la reparación N° {repair.repair_number} no fue aceptada. El costo estimado original de ${repair.estimated_cost:,.0f} sigue vigente.'
            flash = 'Contrapropuesta rechazada. El costo original sigue vigente.'
        RepairRepositoryImpl().save(repair)
        if repair.user_id:
            NotificationRepositoryImpl().save(NotificationEntity(
                user_id=repair.user_id, repair_id=pk,
                message=msg_cliente,
                notification_type=NotificationType.REPAIR_UPDATE,
            ))
        messages.success(request, flash)
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('repair_show', pk=pk)


@admin_required
def repair_set_cost(request, pk):
    if request.method == 'POST':
        cost_str = request.POST.get('estimated_cost', '').strip()
        try:
            from decimal import Decimal
            from infrastructure.repositories.repair_repository_impl import RepairRepositoryImpl
            from infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl
            from domain.entities.notification import NotificationEntity, NotificationType
            repair = get_repair_usecases().get_by_id(pk)
            if repair and cost_str:
                repair.estimated_cost = Decimal(cost_str)
                if repair.status == 'PENDING':
                    repair.status = 'QUOTED'
                repair.cost_accepted = None
                RepairRepositoryImpl().save(repair)
                if repair.user_id:
                    NotificationRepositoryImpl().save(NotificationEntity(
                        user_id=repair.user_id, repair_id=pk,
                        message=f'El costo estimado de tu reparación N° {repair.repair_number} fue establecido en ${repair.estimated_cost:,.0f}',
                        notification_type=NotificationType.REPAIR_UPDATE,
                    ))
                messages.success(request, 'Costo estimado establecido exitosamente.')
            else:
                messages.error(request, 'Debes ingresar un costo válido.')
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
