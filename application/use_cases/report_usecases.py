from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from domain.repositories.order_repository import OrderRepository
from domain.repositories.product_repository import ProductRepository
from domain.repositories.user_repository import UserRepository
from domain.repositories.repair_repository import RepairRepository

_STATUS_ES = {
    'PENDING': 'Pendiente', 'PROCESSING': 'En proceso',
    'SHIPPED': 'Enviado', 'DELIVERED': 'Entregado', 'CANCELLED': 'Cancelado',
    'pending': 'Pendiente', 'in_progress': 'En proceso',
    'quoted': 'Cotizado', 'completed': 'Completado', 'cancelled': 'Cancelado',
    'QUOTED': 'Cotizado', 'IN_PROGRESS': 'En proceso', 'COMPLETED': 'Completado',
}

_CHART_COLORS = [
    colors.HexColor('#c9a84c'), colors.HexColor('#3a5bd9'),
    colors.HexColor('#2d7d2d'), colors.HexColor('#c0392b'),
    colors.HexColor('#8e44ad'), colors.HexColor('#e67e22'),
    colors.HexColor('#16a085'), colors.HexColor('#2c3e50'),
]

def _pie(labels, data, w=360, h=210):
    if not data or sum(data) == 0:
        return None
    d = Drawing(w, h)
    pie = Pie()
    pie.x = w // 2 - 75
    pie.y = 25
    pie.width = 150
    pie.height = 150
    pie.data = list(data)
    pie.labels = [str(l) for l in labels]
    pie.sideLabels = 1
    pie.slices.strokeWidth = 0.5
    pie.slices.strokeColor = colors.white
    pie.slices.label_simple_pointer = 1
    for i in range(len(data)):
        pie.slices[i].fillColor = _CHART_COLORS[i % len(_CHART_COLORS)]
    d.add(pie)
    return d


def _vbar(labels, data, w=460, h=200, bar_color=None):
    if not data:
        return None
    bar_color = bar_color or colors.HexColor('#c9a84c')
    d = Drawing(w, h)
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 40
    bc.height = 130
    bc.width = w - 80
    bc.data = [list(data)]
    bc.categoryAxis.categoryNames = [str(l)[:14] for l in labels]
    bc.categoryAxis.labels.angle = 20
    bc.categoryAxis.labels.fontSize = 7
    bc.categoryAxis.labels.dx = -6
    bc.valueAxis.valueMin = 0
    bc.bars[0].fillColor = bar_color
    bc.bars[0].strokeColor = None
    d.add(bc)
    return d


def _tbl_style(header_color):
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ])


class ReportUseCases:
    def __init__(self, order_repo: OrderRepository, product_repo: ProductRepository,
                 user_repo: UserRepository, repair_repo: RepairRepository):
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._user_repo = user_repo
        self._repair_repo = repair_repo

    def generate_sales_report_pdf(self, start_date=None, end_date=None) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                leftMargin=0.75*inch, rightMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)
        elements = []
        styles = getSampleStyleSheet()
        BLUE = colors.HexColor('#1a237e')

        title_style = ParagraphStyle('T', parent=styles['Heading1'],
                                     fontSize=22, textColor=BLUE,
                                     spaceAfter=20, alignment=TA_CENTER)
        section_style = ParagraphStyle('S', parent=styles['Heading2'],
                                       fontSize=13, textColor=BLUE, spaceBefore=16, spaceAfter=6)

        elements.append(Paragraph("Reporte de Ventas — ANJOS", title_style))

        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()

        elements.append(Paragraph(
            f"Período: {start_date.strftime('%d/%m/%Y')} — {end_date.strftime('%d/%m/%Y')}",
            styles['Normal']))
        elements.append(Spacer(1, 14))

        all_orders = self._order_repo.find_all()
        orders = [o for o in all_orders
                  if o.created_at and start_date <= o.created_at <= end_date and o.is_active]

        total_orders = len(orders)
        total_sales = sum(o.total for o in orders)
        avg_order = total_sales / total_orders if total_orders > 0 else Decimal('0')

        # ── Resumen general ──────────────────────────────────────
        elements.append(Paragraph("Resumen general", section_style))
        stats_tbl = Table([
            ['Indicador', 'Valor'],
            ['Total de pedidos', str(total_orders)],
            ['Ventas totales', f'${total_sales:,.0f}'],
            ['Promedio por pedido', f'${avg_order:,.0f}'],
        ], colWidths=[3*inch, 2*inch])
        stats_tbl.setStyle(_tbl_style(BLUE))
        elements.append(stats_tbl)
        elements.append(Spacer(1, 20))

        # ── Pedidos por estado ────────────────────────────────────
        elements.append(Paragraph("Pedidos por estado", section_style))
        status_count = {}
        for o in orders:
            lbl = _STATUS_ES.get(o.status, o.status)
            status_count[lbl] = status_count.get(lbl, 0) + 1

        if status_count:
            chart = _pie(list(status_count.keys()), list(status_count.values()))
            if chart:
                elements.append(chart)
                elements.append(Spacer(1, 6))

        st_tbl = Table(
            [['Estado', 'Cantidad']] + [[k, str(v)] for k, v in status_count.items()],
            colWidths=[3*inch, 2*inch])
        st_tbl.setStyle(_tbl_style(colors.HexColor('#455a64')))
        elements.append(st_tbl)
        elements.append(Spacer(1, 20))

        # ── Diez pedidos de mayor valor ───────────────────────────
        elements.append(Paragraph("Diez pedidos de mayor valor", section_style))
        top_orders = sorted(orders, key=lambda x: x.total, reverse=True)[:10]

        if top_orders:
            bar_labels = [o.order_number or f'#{i+1}' for i, o in enumerate(top_orders)]
            bar_data = [float(o.total) for o in top_orders]
            chart = _vbar(bar_labels, bar_data, w=460, h=190)
            if chart:
                elements.append(chart)
                elements.append(Spacer(1, 6))

        top_tbl = Table(
            [['N° Pedido', 'Cliente', 'Total', 'Estado']] + [
                [o.order_number or '—',
                 (o.user_name or 'Sin nombre')[:24],
                 f'${o.total:,.0f}',
                 _STATUS_ES.get(o.status, o.status)]
                for o in top_orders],
            colWidths=[1.5*inch, 2.2*inch, 1.3*inch, 1.5*inch])
        top_tbl.setStyle(_tbl_style(BLUE))
        elements.append(top_tbl)

        elements.append(Spacer(1, 24))
        elements.append(Paragraph(
            f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M')}",
            styles['Normal']))
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def generate_inventory_report_pdf(self) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                leftMargin=0.75*inch, rightMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)
        elements = []
        styles = getSampleStyleSheet()
        BLUE = colors.HexColor('#1a237e')
        GREEN = colors.HexColor('#2d7d2d')
        RED = colors.HexColor('#c0392b')

        title_style = ParagraphStyle('T', parent=styles['Heading1'],
                                     fontSize=22, textColor=BLUE,
                                     spaceAfter=20, alignment=TA_CENTER)
        section_style = ParagraphStyle('S', parent=styles['Heading2'],
                                       fontSize=13, textColor=BLUE, spaceBefore=16, spaceAfter=6)

        elements.append(Paragraph("Reporte de Inventario — ANJOS", title_style))
        elements.append(Spacer(1, 10))

        products = self._product_repo.find_all()
        active_products = [p for p in products if p.is_active]
        total_products = len(active_products)
        total_stock = sum(p.stock for p in active_products)
        total_value = sum(p.price * p.stock for p in active_products)
        low_stock = [p for p in active_products if p.stock < 5]

        # ── Resumen ──────────────────────────────────────────────
        elements.append(Paragraph("Resumen general", section_style))
        stats_tbl = Table([
            ['Indicador', 'Valor'],
            ['Total de productos', str(total_products)],
            ['Unidades en stock', str(total_stock)],
            ['Valor total del inventario', f'${total_value:,.0f}'],
            ['Productos con stock bajo', str(len(low_stock))],
        ], colWidths=[3*inch, 2*inch])
        stats_tbl.setStyle(_tbl_style(BLUE))
        elements.append(stats_tbl)
        elements.append(Spacer(1, 20))

        # ── Gráfica stock por categoría ───────────────────────────
        cat_stock = {}
        for p in active_products:
            cat = p.category_name or 'Sin categoría'
            cat_stock[cat] = cat_stock.get(cat, 0) + p.stock

        if cat_stock:
            elements.append(Paragraph("Stock por categoría", section_style))
            chart = _vbar(list(cat_stock.keys()), list(cat_stock.values()),
                          w=460, h=200, bar_color=GREEN)
            if chart:
                elements.append(chart)
                elements.append(Spacer(1, 6))

            cat_tbl = Table(
                [['Categoría', 'Unidades en stock']] +
                [[k, str(v)] for k, v in sorted(cat_stock.items(), key=lambda x: -x[1])],
                colWidths=[3.5*inch, 2*inch])
            cat_tbl.setStyle(_tbl_style(GREEN))
            elements.append(cat_tbl)
            elements.append(Spacer(1, 20))

        # ── Distribución por categoría (gráfica circular) ────────
        if cat_stock:
            elements.append(Paragraph("Distribución de productos por categoría", section_style))
            cat_counts = {}
            for p in active_products:
                cat = p.category_name or 'Sin categoría'
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
            chart = _pie(list(cat_counts.keys()), list(cat_counts.values()), w=380, h=220)
            if chart:
                elements.append(chart)
                elements.append(Spacer(1, 10))

        # ── Productos con stock bajo ──────────────────────────────
        if low_stock:
            elements.append(Paragraph(
                "Productos con stock bajo (menos de 5 unidades)", section_style))
            low_tbl = Table(
                [['Producto', 'Categoría', 'Stock', 'Precio']] + [
                    [p.name[:30], p.category_name or 'Sin categoría',
                     str(p.stock), f'${p.price:,.0f}']
                    for p in sorted(low_stock, key=lambda x: x.stock)],
                colWidths=[2.5*inch, 1.5*inch, 1*inch, 1.5*inch])
            low_tbl.setStyle(_tbl_style(RED))
            elements.append(low_tbl)
            elements.append(Spacer(1, 20))

        # ── Inventario completo ───────────────────────────────────
        elements.append(Paragraph("Inventario completo", section_style))
        inv_tbl = Table(
            [['Producto', 'Categoría', 'Stock', 'Precio', 'Valor total']] + [
                [p.name[:24], p.category_name or 'Sin categoría',
                 str(p.stock), f'${p.price:,.0f}', f'${p.price * p.stock:,.0f}']
                for p in sorted(active_products, key=lambda x: x.stock)],
            colWidths=[2*inch, 1.4*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        inv_tbl.setStyle(_tbl_style(BLUE))
        elements.append(inv_tbl)

        elements.append(Spacer(1, 20))
        elements.append(Paragraph(
            f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M')}",
            styles['Normal']))
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def generate_users_report_pdf(self) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                leftMargin=0.75*inch, rightMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)
        elements = []
        styles = getSampleStyleSheet()
        BLUE = colors.HexColor('#1a237e')

        title_style = ParagraphStyle('T', parent=styles['Heading1'],
                                     fontSize=22, textColor=BLUE,
                                     spaceAfter=20, alignment=TA_CENTER)
        section_style = ParagraphStyle('S', parent=styles['Heading2'],
                                       fontSize=13, textColor=BLUE, spaceBefore=16, spaceAfter=6)

        elements.append(Paragraph("Reporte de Clientes — ANJOS", title_style))
        elements.append(Spacer(1, 10))

        users = self._user_repo.find_all()
        active_users = [u for u in users if u.is_active]
        admin_count = sum(1 for u in active_users if u.roles and 'admin' in u.roles)
        client_count = len(active_users) - admin_count

        # ── Resumen ──────────────────────────────────────────────
        elements.append(Paragraph("Resumen general", section_style))
        stats_tbl = Table([
            ['Indicador', 'Valor'],
            ['Total de usuarios', str(len(users))],
            ['Usuarios activos', str(len(active_users))],
            ['Usuarios inactivos', str(len(users) - len(active_users))],
            ['Administradores', str(admin_count)],
            ['Clientes', str(client_count)],
        ], colWidths=[3*inch, 2*inch])
        stats_tbl.setStyle(_tbl_style(BLUE))
        elements.append(stats_tbl)
        elements.append(Spacer(1, 20))

        # ── Gráfica distribución ──────────────────────────────────
        elements.append(Paragraph("Distribución de usuarios", section_style))
        pie_labels = ['Activos', 'Inactivos']
        pie_data = [len(active_users), len(users) - len(active_users)]
        chart = _pie(pie_labels, pie_data, w=340, h=220)
        if chart:
            elements.append(chart)
            elements.append(Spacer(1, 10))

        # ── Gráfica por rol ───────────────────────────────────────
        if admin_count > 0 or client_count > 0:
            elements.append(Paragraph("Usuarios activos por rol", section_style))
            chart2 = _pie(['Administradores', 'Clientes'], [admin_count, client_count],
                          w=340, h=220)
            if chart2:
                elements.append(chart2)
                elements.append(Spacer(1, 10))

        # ── Lista de usuarios ─────────────────────────────────────
        elements.append(Paragraph("Lista de usuarios activos", section_style))
        usr_tbl = Table(
            [['Nombre', 'Correo electrónico', 'Rol', 'Teléfono']] + [
                [u.name[:24], u.email[:28],
                 'Administrador' if u.roles and 'admin' in u.roles else 'Cliente',
                 u.phone or '—']
                for u in active_users],
            colWidths=[1.8*inch, 2.2*inch, 1.5*inch, 1.5*inch])
        usr_tbl.setStyle(_tbl_style(BLUE))
        elements.append(usr_tbl)

        elements.append(Spacer(1, 20))
        elements.append(Paragraph(
            f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M')}",
            styles['Normal']))
        doc.build(elements)
        buffer.seek(0)
        return buffer
