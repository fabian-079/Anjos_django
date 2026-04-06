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
    can_edit = request.user.is_admin() or item.user_id == request.user.id
    return render(request, 'personalizacion/show.html', {'customization': item, 'can_edit': can_edit})


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
    TECHNICIANS = ['Carlos Mendoza', 'Luisa Fernández', 'Andrés Gómez', 'María Torres', 'Felipe Rojas']
    return render(request, 'personalizacion/edit.html', {'customization': item, 'technicians': TECHNICIANS})


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
            assigned_technician=request.POST.get('assigned_technician', '').strip() if request.user.is_admin() else None,
        )
        messages.success(request, 'Personalización actualizada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('customization_show', pk=pk)


@login_required
def customization_respond_cost(request, pk):
    if request.method != 'POST':
        return redirect('customization_show', pk=pk)
    item = get_customization_usecases().get_by_id(pk)
    if not item or item.user_id != request.user.id:
        messages.error(request, 'Sin permiso.')
        return redirect('customization_index')
    if not item.estimated_price:
        messages.error(request, 'No hay precio estimado para responder.')
        return redirect('customization_show', pk=pk)
    accepted = request.POST.get('response') == 'accept'
    try:
        from infrastructure.repositories.customization_repository_impl import CustomizationRepositoryImpl
        from infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl
        from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
        from domain.entities.notification import NotificationEntity, NotificationType
        item.cost_accepted = accepted
        item.status = 'in_progress' if accepted else 'quoted'
        CustomizationRepositoryImpl().save(item)
        label = 'aceptado' if accepted else 'rechazado'
        admins = UserRepositoryImpl().find_admins()
        for admin in admins:
            NotificationRepositoryImpl().save(NotificationEntity(
                user_id=admin.id, customization_id=pk,
                message=f'El cliente {request.user.name} ha {label} el precio estimado de ${item.estimated_price:,.0f} de la personalización #{pk}',
                notification_type=NotificationType.CUSTOMIZATION_UPDATE,
            ))
        messages.success(request, f'Has {label} el precio estimado.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('customization_show', pk=pk)


@login_required
def customization_negotiate(request, pk):
    if request.method != 'POST':
        return redirect('customization_show', pk=pk)
    item = get_customization_usecases().get_by_id(pk)
    if not item or item.user_id != request.user.id:
        messages.error(request, 'Sin permiso.')
        return redirect('customization_index')
    counter_offer_raw = request.POST.get('counter_offer', '').strip()
    note = request.POST.get('negotiation_note', '').strip()
    if not counter_offer_raw:
        messages.error(request, 'Debes indicar un monto propuesto.')
        return redirect('customization_show', pk=pk)
    try:
        from decimal import Decimal
        from infrastructure.repositories.customization_repository_impl import CustomizationRepositoryImpl
        from infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl
        from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
        from domain.entities.notification import NotificationEntity, NotificationType
        item.client_counter_offer = Decimal(counter_offer_raw.replace(',', '.'))
        item.client_negotiation_note = note or None
        item.cost_accepted = False
        CustomizationRepositoryImpl().save(item)
        admins = UserRepositoryImpl().find_admins()
        for admin in admins:
            NotificationRepositoryImpl().save(NotificationEntity(
                user_id=admin.id, customization_id=pk,
                message=f'El cliente {request.user.name} propone ${item.client_counter_offer:,.0f} para la personalización #{pk}' + (f': "{note}"' if note else ''),
                notification_type=NotificationType.CUSTOMIZATION_UPDATE,
            ))
        messages.success(request, 'Tu contrapropuesta fue enviada al equipo.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('customization_show', pk=pk)


@admin_required
def customization_respond_counter(request, pk):
    if request.method != 'POST':
        return redirect('customization_show', pk=pk)
    try:
        from infrastructure.repositories.customization_repository_impl import CustomizationRepositoryImpl
        from infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl
        from domain.entities.notification import NotificationEntity, NotificationType
        item = get_customization_usecases().get_by_id(pk)
        if not item or not item.client_counter_offer:
            messages.error(request, 'No hay contrapropuesta para responder.')
            return redirect('customization_show', pk=pk)
        accepted = request.POST.get('response') == 'accept'
        if accepted:
            item.estimated_price = item.client_counter_offer
            item.cost_accepted = True
            item.client_counter_offer = None
            item.client_negotiation_note = None
            item.status = 'in_progress'
            msg_cliente = f'¡Buenas noticias! Tu propuesta de ${item.estimated_price:,.0f} para la personalización #{pk} fue aceptada.'
            flash = 'Contrapropuesta aceptada. El precio fue actualizado.'
        else:
            item.client_counter_offer = None
            item.client_negotiation_note = None
            item.cost_accepted = None
            item.status = 'quoted'
            msg_cliente = f'Tu propuesta para la personalización #{pk} no fue aceptada. El precio estimado original de ${item.estimated_price:,.0f} sigue vigente.'
            flash = 'Contrapropuesta rechazada. El precio original sigue vigente.'
        CustomizationRepositoryImpl().save(item)
        if item.user_id:
            NotificationRepositoryImpl().save(NotificationEntity(
                user_id=item.user_id, customization_id=pk,
                message=msg_cliente,
                notification_type=NotificationType.CUSTOMIZATION_UPDATE,
            ))
        messages.success(request, flash)
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('customization_show', pk=pk)


@admin_required
def customization_set_price(request, pk):
    if request.method == 'POST':
        price_str = request.POST.get('estimated_price', '').strip()
        try:
            from decimal import Decimal
            from infrastructure.repositories.customization_repository_impl import CustomizationRepositoryImpl
            from infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl
            from domain.entities.notification import NotificationEntity, NotificationType
            item = get_customization_usecases().get_by_id(pk)
            if item and price_str:
                item.estimated_price = Decimal(price_str)
                if item.status == 'pending':
                    item.status = 'quoted'
                item.cost_accepted = None
                CustomizationRepositoryImpl().save(item)
                if item.user_id:
                    NotificationRepositoryImpl().save(NotificationEntity(
                        user_id=item.user_id, customization_id=pk,
                        message=f'El precio estimado de tu personalización #{pk} fue establecido en ${item.estimated_price:,.0f}',
                        notification_type=NotificationType.CUSTOMIZATION_UPDATE,
                    ))
                messages.success(request, 'Precio estimado establecido exitosamente.')
            else:
                messages.error(request, 'Debes ingresar un precio válido.')
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
