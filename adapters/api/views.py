from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from infrastructure.container import (
    get_product_usecases, get_category_usecases,
    get_cart_usecases, get_notification_usecases,
    get_order_usecases, get_repair_usecases,
    get_customization_usecases, get_user_usecases,
    get_email_usecases,
)
from adapters.api.decorators import admin_required


# ─── Auth ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            if not user.is_active:
                messages.error(request, 'Tu cuenta está desactivada.')
            else:
                login(request, user)
                _merge_guest_session(request, user)
                next_url = request.GET.get('next', '')
                if next_url and next_url.startswith('/') and not user.is_admin():
                    return redirect(next_url)
                return _redirect_by_role(user)
        else:
            messages.error(request, 'Email o contraseña incorrectos.')
    return render(request, 'auth/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not name or not email or not password:
            messages.error(request, 'Nombre, email y contraseña son requeridos.')
        elif password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
        else:
            try:
                uc = get_user_usecases()
                new_user = uc.create_user(
                    name=name, email=email, password=password,
                    phone=phone or None, address=address or None, role='cliente',
                )
                get_email_usecases().send_welcome_email(new_user.id)
                user = authenticate(request, username=email, password=password)
                if user:
                    login(request, user)
                    _merge_guest_session(request, user)
                    messages.success(request, f'¡Bienvenido {name}!')
                    next_url = request.GET.get('next', '')
                    if next_url and next_url.startswith('/'):
                        return redirect(next_url)
                    return redirect('dashboard_cliente')
            except ValueError as e:
                messages.error(request, str(e))
    return render(request, 'auth/register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def _merge_guest_session(request, user):
    try:
        guest_cart = request.session.pop('guest_cart', {})
        if guest_cart:
            uc = get_cart_usecases()
            for pid_str, qty in guest_cart.items():
                try:
                    uc.add_to_cart(user.id, int(pid_str), qty)
                except Exception:
                    pass
        guest_favs = request.session.pop('guest_favorites', [])
        if guest_favs:
            from infrastructure.container import get_favorite_usecases
            fav_uc = get_favorite_usecases()
            for pid in guest_favs:
                try:
                    if not fav_uc.is_product_favorite(user.id, pid):
                        fav_uc.toggle_product_favorite(user.id, pid)
                except Exception:
                    pass
    except Exception:
        pass


def _redirect_by_role(user):
    if user.is_admin():
        return redirect('dashboard_admin')
    return redirect('dashboard_cliente')


# ─── Home ─────────────────────────────────────────────────────────────────────

def home_view(request):
    products_uc = get_product_usecases()
    categories_uc = get_category_usecases()
    featured = products_uc.get_featured_products()
    categories = categories_uc.get_active()
    return render(request, 'home/index.html', {
        'featured_products': featured,
        'categories': categories,
    })


def catalogo_view(request):
    products_uc = get_product_usecases()
    categories_uc = get_category_usecases()

    category_id = request.GET.get('category')
    material = request.GET.get('material')
    color = request.GET.get('color')
    finish = request.GET.get('finish')
    stones = request.GET.get('stones')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search = request.GET.get('search')
    page = int(request.GET.get('page', 1))

    result = products_uc.search_products(
        category_id=int(category_id) if category_id else None,
        material=material, color=color, finish=finish, stones=stones,
        min_price=float(min_price) if min_price else None,
        max_price=float(max_price) if max_price else None,
        search=search, page=page, page_size=12,
    )
    return render(request, 'catalogo.html', {
        'products': result['items'],
        'total': result['total'],
        'num_pages': result['num_pages'],
        'current_page': result['current_page'],
        'has_next': result['has_next'],
        'has_previous': result['has_previous'],
        'categories': categories_uc.get_active(),
        'materials': products_uc.get_distinct_materials(),
        'colors': products_uc.get_distinct_colors(),
        'finishes': products_uc.get_distinct_finishes(),
        'stones_list': products_uc.get_distinct_stones(),
        'filters': {
            'category': category_id, 'material': material,
            'color': color, 'finish': finish, 'stones': stones,
            'min_price': min_price, 'max_price': max_price, 'search': search,
        },
    })


def producto_detalle_view(request, pk):
    products_uc = get_product_usecases()
    product = products_uc.get_product_by_id(pk)
    if not product or not product.is_active:
        from django.http import Http404
        raise Http404
    related = products_uc.get_related_products(product.category_id, pk, 4)
    is_favorite = False
    if request.user.is_authenticated:
        fav_uc = get_favorite_usecases_lazy()
        is_favorite = fav_uc.is_product_favorite(request.user.id, pk)
    else:
        is_favorite = pk in request.session.get('guest_favorites', [])
    return render(request, 'producto_detalle.html', {
        'product': product,
        'related_products': related,
        'is_favorite': is_favorite,
    })


def get_favorite_usecases_lazy():
    from infrastructure.container import get_favorite_usecases
    return get_favorite_usecases()


def buscar_view(request):
    products_uc = get_product_usecases()
    categories_uc = get_category_usecases()

    search = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    material = request.GET.get('material', '').strip()
    color = request.GET.get('color', '').strip()
    finish = request.GET.get('finish', '').strip()
    stones_filter = request.GET.get('stones', '').strip()
    min_price = request.GET.get('minPrice', '').strip()
    max_price = request.GET.get('maxPrice', '').strip()
    page = int(request.GET.get('page', 0))

    has_filters = any([search, category_id, material, color, finish, stones_filter, min_price, max_price])
    total_items = None
    total_pages = 1
    current_page = 0
    products = []

    if has_filters:
        result = products_uc.search_products(
            search=search or None,
            category_id=int(category_id) if category_id else None,
            material=material or None,
            color=color or None,
            finish=finish or None,
            stones=stones_filter or None,
            min_price=float(min_price) if min_price else None,
            max_price=float(max_price) if max_price else None,
            page=page, page_size=20,
        )
        products = result['items']
        total_items = result.get('total', 0)
        total_pages = result.get('num_pages', 1)
        current_page = result.get('current_page', 0)

    return render(request, 'buscar.html', {
        'products': products,
        'search_query': search,
        'total_items': total_items,
        'total_pages': total_pages,
        'current_page': current_page,
        'categories': categories_uc.get_active(),
        'materials': products_uc.get_distinct_materials(),
        'colors': products_uc.get_distinct_colors(),
        'finishes': products_uc.get_distinct_finishes(),
        'stones': products_uc.get_distinct_stones(),
    })


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard_admin_view(request):
    from infrastructure.models.user_model import User as UserModel
    from infrastructure.models.order_model import Order as OrderModel
    from infrastructure.models.repair_model import Repair as RepairModel
    from infrastructure.models.product_model import Product as ProductModel

    total_users = UserModel.objects.filter(is_active=True).count()
    total_orders = OrderModel.objects.filter(is_active=True).count()
    total_repairs = RepairModel.objects.filter(is_active=True).count()
    total_products = ProductModel.objects.filter(is_active=True).count()

    recent_orders = get_order_usecases().get_all_orders()[:5]
    recent_repairs = get_repair_usecases().get_all()[:5]

    notif_count = 0
    if request.user.is_authenticated:
        notif_count = get_notification_usecases().count_unread(request.user.id)

    return render(request, 'dashboard/admin.html', {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_repairs': total_repairs,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'recent_repairs': recent_repairs,
        'unread_notifications': notif_count,
    })


@login_required
def dashboard_cliente_view(request):
    orders = get_order_usecases().get_orders_by_user(request.user.id)
    repairs = get_repair_usecases().get_by_user(request.user.id)
    customizations = get_customization_usecases().get_by_user(request.user.id)
    notif_count = get_notification_usecases().count_unread(request.user.id)
    return render(request, 'dashboard/cliente.html', {
        'orders': orders[:5],
        'repairs': repairs[:5],
        'customizations': customizations[:5],
        'unread_notifications': notif_count,
    })
