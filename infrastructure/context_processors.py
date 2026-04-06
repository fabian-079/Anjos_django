def unread_notifications(request):
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}
    try:
        from infrastructure.models.notification_model import Notification
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    except Exception:
        count = 0
    return {'unread_notifications_count': count}
