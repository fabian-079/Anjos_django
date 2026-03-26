from django.contrib import messages
from django.shortcuts import render, redirect
from adapters.api.decorators import admin_required
from infrastructure.container import get_user_usecases
from infrastructure.models.user_model import Role


@admin_required
def user_index(request):
    return render(request, 'users/index.html', {
        'users': get_user_usecases().get_all_users(),
    })


@admin_required
def user_create_form(request):
    return render(request, 'users/create.html', {'roles': Role.objects.filter(is_active=True)})


@admin_required
def user_create(request):
    if request.method != 'POST':
        return redirect('user_index')
    uc = get_user_usecases()
    try:
        role = request.POST.get('role', 'cliente')
        uc.create_user(
            name=request.POST.get('name', '').strip(),
            email=request.POST.get('email', '').strip(),
            password=request.POST.get('password', ''),
            phone=request.POST.get('phone', '').strip() or None,
            address=request.POST.get('address', '').strip() or None,
            role=role,
        )
        messages.success(request, 'Usuario creado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('user_index')


@admin_required
def user_edit_form(request, pk):
    uc = get_user_usecases()
    user = uc.get_user_by_id(pk)
    if not user:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('user_index')
    return render(request, 'users/edit.html', {
        'user': user,
        'roles': Role.objects.filter(is_active=True),
    })


@admin_required
def user_update(request, pk):
    if request.method != 'POST':
        return redirect('user_index')
    uc = get_user_usecases()
    try:
        is_active = request.POST.get('is_active', 'true') == 'true'
        password = request.POST.get('password', '').strip() or None
        uc.update_user(
            user_id=pk,
            name=request.POST.get('name', '').strip(),
            email=request.POST.get('email', '').strip(),
            phone=request.POST.get('phone', '').strip() or None,
            address=request.POST.get('address', '').strip() or None,
            is_active=is_active,
            password=password,
        )
        messages.success(request, 'Usuario actualizado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('user_index')


@admin_required
def user_delete(request, pk):
    if request.method == 'POST':
        try:
            get_user_usecases().deactivate_user(pk)
            messages.success(request, 'Usuario desactivado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('user_index')
