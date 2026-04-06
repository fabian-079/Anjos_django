from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from adapters.api.views import (
    login_view, register_view, logout_view,
    home_view, catalogo_view, producto_detalle_view, buscar_view,
    dashboard_admin_view, dashboard_cliente_view,
)
from adapters.api.product_views import (
    product_index, product_create_form, product_create,
    product_edit_form, product_update, product_delete,
    add_to_cart, toggle_favorite,
)
from adapters.api.category_views import (
    category_index, category_create_form, category_create,
    category_edit_form, category_update, category_delete,
)
from adapters.api.user_views import (
    user_index, user_create_form, user_create,
    user_edit_form, user_update, user_delete,
)
from adapters.api.cart_views import cart_view, cart_update, cart_remove
from adapters.api.order_views import (
    order_index, order_show, checkout_view, order_create,
    order_edit_form, order_update, order_delete,
)
from adapters.api.repair_views import (
    repair_index, repair_show, repair_create_form, repair_create,
    repair_edit_form, repair_update, repair_assign, repair_delete,
    repair_respond_cost, repair_negotiate, repair_respond_counter,
    repair_set_cost,
)
from adapters.api.customization_views import (
    customization_index, customization_show,
    customization_create_form, customization_create,
    customization_edit_form, customization_update, customization_delete,
    customization_respond_cost, customization_negotiate, customization_respond_counter,
    customization_set_price,
)
from adapters.api.notification_views import (
    notification_index, notification_mark_read, notification_mark_all_read,
)
from adapters.api.favorite_views import favoritos_view, favorite_remove
from adapters.api.email_views import (
    email_mass_send_form, email_mass_send, email_new_products_notification, email_test_send
)
from adapters.api.report_views import (
    reports_index, report_sales_pdf, report_inventory_pdf, report_users_pdf, report_preview
)
from adapters.api.webservice_views import (
    webservice_dashboard, api_exchange_rates, api_convert_currency, api_gold_price,
    api_location_info, api_calculate_shipping, webservice_test_page, api_weather_info
)

urlpatterns = [
    # Django admin
    path('django-admin/', admin.site.urls),

    # Auth
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    # Home & public
    path('', home_view, name='home'),
    path('catalogo/', catalogo_view, name='catalogo'),
    path('buscar/', buscar_view, name='buscar'),
    path('producto/<int:pk>/', producto_detalle_view, name='producto_detalle'),

    # Dashboard
    path('dashboard/admin/', dashboard_admin_view, name='dashboard_admin'),
    path('dashboard/cliente/', dashboard_cliente_view, name='dashboard_cliente'),

    # Products (admin CRUD)
    path('products/', product_index, name='product_index'),
    path('products/create/', product_create_form, name='product_create_form'),
    path('products/store/', product_create, name='product_create'),
    path('products/<int:pk>/edit/', product_edit_form, name='product_edit_form'),
    path('products/<int:pk>/update/', product_update, name='product_update'),
    path('products/<int:pk>/delete/', product_delete, name='product_delete'),
    path('products/<int:pk>/carrito/', add_to_cart, name='add_to_cart'),
    path('products/<int:pk>/favoritos/', toggle_favorite, name='toggle_favorite'),

    # Categories
    path('categories/', category_index, name='category_index'),
    path('categories/create/', category_create_form, name='category_create_form'),
    path('categories/store/', category_create, name='category_create'),
    path('categories/<int:pk>/edit/', category_edit_form, name='category_edit_form'),
    path('categories/<int:pk>/update/', category_update, name='category_update'),
    path('categories/<int:pk>/delete/', category_delete, name='category_delete'),

    # Users (admin)
    path('users/', user_index, name='user_index'),
    path('users/create/', user_create_form, name='user_create_form'),
    path('users/store/', user_create, name='user_create'),
    path('users/<int:pk>/edit/', user_edit_form, name='user_edit_form'),
    path('users/<int:pk>/update/', user_update, name='user_update'),
    path('users/<int:pk>/delete/', user_delete, name='user_delete'),

    # Cart
    path('carrito/', cart_view, name='carrito'),
    path('carrito/<int:pk>/update/', cart_update, name='cart_update'),
    path('carrito/<int:pk>/remove/', cart_remove, name='cart_remove'),

    # Orders
    path('orders/', order_index, name='order_index'),
    path('orders/checkout/', checkout_view, name='checkout'),
    path('orders/create/', order_create, name='order_create'),
    path('orders/<int:pk>/', order_show, name='order_show'),
    path('orders/<int:pk>/edit/', order_edit_form, name='order_edit_form'),
    path('orders/<int:pk>/update/', order_update, name='order_update'),
    path('orders/<int:pk>/delete/', order_delete, name='order_delete'),

    # Repairs
    path('reparaciones/', repair_index, name='repair_index'),
    path('reparaciones/create/', repair_create_form, name='repair_create_form'),
    path('reparaciones/store/', repair_create, name='repair_create'),
    path('reparaciones/<int:pk>/', repair_show, name='repair_show'),
    path('reparaciones/<int:pk>/edit/', repair_edit_form, name='repair_edit_form'),
    path('reparaciones/<int:pk>/update/', repair_update, name='repair_update'),
    path('reparaciones/<int:pk>/asignar/', repair_assign, name='repair_assign'),
    path('reparaciones/<int:pk>/responder-costo/', repair_respond_cost, name='repair_respond_cost'),
    path('reparaciones/<int:pk>/negociar/', repair_negotiate, name='repair_negotiate'),
    path('reparaciones/<int:pk>/responder-contrapropuesta/', repair_respond_counter, name='repair_respond_counter'),
    path('reparaciones/<int:pk>/set-cost/', repair_set_cost, name='repair_set_cost'),
    path('reparaciones/<int:pk>/delete/', repair_delete, name='repair_delete'),

    # Customizations
    path('personalizacion/', customization_index, name='customization_index'),
    path('personalizacion/create/', customization_create_form, name='customization_create_form'),
    path('personalizacion/store/', customization_create, name='customization_create'),
    path('personalizacion/<int:pk>/', customization_show, name='customization_show'),
    path('personalizacion/<int:pk>/edit/', customization_edit_form, name='customization_edit_form'),
    path('personalizacion/<int:pk>/update/', customization_update, name='customization_update'),
    path('personalizacion/<int:pk>/responder-costo/', customization_respond_cost, name='customization_respond_cost'),
    path('personalizacion/<int:pk>/negociar/', customization_negotiate, name='customization_negotiate'),
    path('personalizacion/<int:pk>/responder-contrapropuesta/', customization_respond_counter, name='customization_respond_counter'),
    path('personalizacion/<int:pk>/set-price/', customization_set_price, name='customization_set_price'),
    path('personalizacion/<int:pk>/delete/', customization_delete, name='customization_delete'),

    # Notifications
    path('notifications/', notification_index, name='notification_index'),
    path('notifications/<int:pk>/read/', notification_mark_read, name='notification_mark_read'),
    path('notifications/read-all/', notification_mark_all_read, name='notification_mark_all_read'),

    # Favorites
    path('favoritos/', favoritos_view, name='favoritos'),
    path('favoritos/<int:pk>/remove/', favorite_remove, name='favorite_remove'),

    # Email masivo
    path('emails/mass-send/', email_mass_send_form, name='email_mass_send_form'),
    path('emails/mass-send/send/', email_mass_send, name='email_mass_send'),
    path('emails/new-products/', email_new_products_notification, name='email_new_products'),
    path('emails/test/', email_test_send, name='email_test_send'),

    # Reportes PDF
    path('reports/', reports_index, name='reports_index'),
    path('reports/preview/', report_preview, name='report_preview'),
    path('reports/sales/pdf/', report_sales_pdf, name='report_sales_pdf'),
    path('reports/inventory/pdf/', report_inventory_pdf, name='report_inventory_pdf'),
    path('reports/users/pdf/', report_users_pdf, name='report_users_pdf'),

    # Web Services / APIs
    path('webservices/', webservice_dashboard, name='webservice_dashboard'),
    path('webservices/test/', webservice_test_page, name='webservice_test_page'),
    path('api/exchange-rates/', api_exchange_rates, name='api_exchange_rates'),
    path('api/convert-currency/', api_convert_currency, name='api_convert_currency'),
    path('api/gold-price/', api_gold_price, name='api_gold_price'),
    path('api/location/', api_location_info, name='api_location_info'),
    path('api/shipping/', api_calculate_shipping, name='api_calculate_shipping'),
    path('api/weather/', api_weather_info, name='api_weather_info'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
