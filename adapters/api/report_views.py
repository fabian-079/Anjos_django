from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect
from adapters.api.decorators import admin_required
from infrastructure.container import get_report_usecases


@admin_required
def reports_index(request):
    import json
    from collections import defaultdict
    from infrastructure.models.order_model import Order as OrderModel
    from infrastructure.models.product_model import Product as ProductModel
    from infrastructure.models.repair_model import Repair as RepairModel
    from infrastructure.models.customization_model import Customization as CustomModel
    from django.db.models import Count, Sum

    now = timezone.now()

    STATUS_ES = {
        'PENDING': 'Pendiente', 'PROCESSING': 'En proceso',
        'SHIPPED': 'Enviado', 'DELIVERED': 'Entregado', 'CANCELLED': 'Cancelado',
        'pending': 'Pendiente', 'in_progress': 'En proceso',
        'quoted': 'Cotizado', 'completed': 'Completado', 'cancelled': 'Cancelado',
        'QUOTED': 'Cotizado', 'IN_PROGRESS': 'En proceso', 'COMPLETED': 'Completado',
    }

    # -- Órdenes por estado --
    orders_by_status = list(
        OrderModel.objects.filter(is_active=True)
        .values('status').annotate(n=Count('id'))
    )
    orders_status_labels = json.dumps([STATUS_ES.get(s['status'], s['status']) for s in orders_by_status])
    orders_status_data   = json.dumps([s['n'] for s in orders_by_status])

    # -- Ingresos por mes (últimos 6 meses) --
    recent_orders = OrderModel.objects.filter(
        is_active=True, created_at__gte=now - timedelta(days=180)
    ).values('created_at', 'total')
    monthly_map = defaultdict(float)
    for o in recent_orders:
        if o['created_at']:
            key = o['created_at'].strftime('%b %Y')
            monthly_map[key] += float(o['total'] or 0)
    month_labels, month_vals = [], []
    for i in range(5, -1, -1):
        dt = now - timedelta(days=30 * i)
        k = dt.strftime('%b %Y')
        month_labels.append(k)
        month_vals.append(round(monthly_map.get(k, 0), 0))
    monthly_labels = json.dumps(month_labels)
    monthly_data   = json.dumps(month_vals)

    # -- Stock por categoría --
    cat_qs = (
        ProductModel.objects.filter(is_active=True)
        .values('category__name').annotate(stock=Sum('stock'), n=Count('id'))
        .order_by('-stock')
    )
    cat_labels = json.dumps([c['category__name'] or 'Sin categoría' for c in cat_qs])
    cat_stock  = json.dumps([c['stock'] or 0 for c in cat_qs])
    cat_count  = json.dumps([c['n'] for c in cat_qs])

    # -- Reparaciones por estado --
    rep_qs = list(
        RepairModel.objects.filter(is_active=True)
        .values('status').annotate(n=Count('id'))
    )
    repair_labels = json.dumps([STATUS_ES.get(s['status'], s['status']) for s in rep_qs])
    repair_data   = json.dumps([s['n'] for s in rep_qs])

    # -- KPIs rápidos --
    kpis = {
        'total_orders':      OrderModel.objects.filter(is_active=True).count(),
        'total_revenue':     OrderModel.objects.filter(is_active=True).aggregate(s=Sum('total'))['s'] or 0,
        'total_products':    ProductModel.objects.filter(is_active=True).count(),
        'low_stock':         ProductModel.objects.filter(is_active=True, stock__lt=5).count(),
        'total_repairs':     RepairModel.objects.filter(is_active=True).count(),
        'pending_repairs':   RepairModel.objects.filter(is_active=True, status='PENDING').count(),
    }

    return render(request, 'reports/index.html', {
        'kpis': kpis,
        'orders_status_labels': orders_status_labels,
        'orders_status_data':   orders_status_data,
        'monthly_labels':       monthly_labels,
        'monthly_data':         monthly_data,
        'cat_labels':           cat_labels,
        'cat_stock':            cat_stock,
        'cat_count':            cat_count,
        'repair_labels':        repair_labels,
        'repair_data':          repair_data,
    })


@admin_required
def report_sales_pdf(request):
    """Generar reporte de ventas en PDF"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            naive = datetime.strptime(start_date_str, '%Y-%m-%d')
            start_date = timezone.make_aware(naive)
        except ValueError:
            pass
    
    if end_date_str:
        try:
            naive = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = timezone.make_aware(naive.replace(hour=23, minute=59, second=59))
        except ValueError:
            pass
    
    # Por defecto: últimos 30 días
    if not start_date:
        start_date = timezone.now() - timedelta(days=30)
    if not end_date:
        end_date = timezone.now()
    
    report_uc = get_report_usecases()
    pdf_buffer = report_uc.generate_sales_report_pdf(start_date, end_date)
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = f'reporte_ventas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@admin_required
def report_inventory_pdf(request):
    """Generar reporte de inventario en PDF"""
    report_uc = get_report_usecases()
    pdf_buffer = report_uc.generate_inventory_report_pdf()
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = f'reporte_inventario_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@admin_required
def report_users_pdf(request):
    """Generar reporte de usuarios en PDF"""
    report_uc = get_report_usecases()
    pdf_buffer = report_uc.generate_users_report_pdf()
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = f'reporte_usuarios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@admin_required
def report_preview(request):
    """Vista previa de reportes disponibles"""
    return render(request, 'reports/preview.html')
