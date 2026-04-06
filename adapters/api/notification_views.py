from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from infrastructure.container import get_notification_usecases


@login_required
def notification_index(request):
    uc = get_notification_usecases()
    notifications = uc.get_by_user(request.user.id)
    unread_count = sum(1 for n in notifications if not n.is_read)
    return render(request, 'notifications/index.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def notification_mark_read(request, pk):
    if request.method == 'POST':
        try:
            get_notification_usecases().mark_as_read(pk)
            new_count = get_notification_usecases().count_unread(request.user.id)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'unread_count': new_count})
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False})
            messages.error(request, str(e))
    return redirect('notification_index')


@login_required
def notification_mark_all_read(request):
    if request.method == 'POST':
        try:
            get_notification_usecases().mark_all_as_read(request.user.id)
            messages.success(request, 'Todas las notificaciones marcadas como leídas.')
        except Exception as e:
            messages.error(request, str(e))
    return redirect('notification_index')
