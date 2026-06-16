from django import template

register = template.Library()

_STATUS_MAP = {
    'pending': 'Pendiente',
    'processing': 'En proceso',
    'in_progress': 'En proceso',
    'shipped': 'Enviado',
    'delivered': 'Entregado',
    'completed': 'Completado',
    'complete': 'Completado',
    'cancelled': 'Cancelado',
    'canceled': 'Cancelado',
    'active': 'Activo',
    'inactive': 'Inactivo',
    'quoted': 'Cotizado',
    'approved': 'Aprobado',
    'rejected': 'Rechazado',
}


@register.filter
def status_es(value):
    if not value:
        return value
    return _STATUS_MAP.get(str(value).lower(), str(value).capitalize())
