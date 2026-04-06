from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from adapters.api.decorators import admin_required
from infrastructure.container import get_email_usecases, get_user_usecases



@admin_required
def email_mass_send_form(request):
    """Formulario para envío masivo de correos"""
    return render(request, 'emails/mass_send.html')




@admin_required
def email_mass_send(request):
    """Enviar correos masivos"""
    if request.method != 'POST':
        return redirect('email_mass_send_form')
    
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()
    recipient_type = request.POST.get('recipient_type', 'all')
    
    if not subject or not message:
        messages.error(request, 'Asunto y mensaje son requeridos.')
        return redirect('email_mass_send_form')
    
    email_uc = get_email_usecases()
    
    # Determinar destinatarios
    role = None
    if recipient_type == 'clients':
        role = 'cliente'
    elif recipient_type == 'admins':
        role = 'admin'
    
    try:
        count = email_uc.send_mass_promotional_email(subject, message, role)
        messages.success(request, f'Correos enviados exitosamente a {count} usuarios.')
    except Exception as e:
        messages.error(request, f'Error enviando correos: {e}')
    
    return redirect('email_mass_send_form')


@admin_required
def email_new_products_notification(request):
    """Notificar nuevos productos a clientes"""
    if request.method != 'POST':
        return redirect('product_index')
    
    product_ids = request.POST.getlist('product_ids')
    if not product_ids:
        messages.error(request, 'Selecciona al menos un producto.')
        return redirect('product_index')
    
    from infrastructure.container import get_product_usecases
    product_uc = get_product_usecases()
    
    product_names = []
    for pid in product_ids:
        product = product_uc.get_product_by_id(int(pid))
        if product:
            product_names.append(product.name)
    
    if product_names:
        email_uc = get_email_usecases()
        count = email_uc.send_new_products_notification(product_names)
        messages.success(request, f'Notificación enviada a {count} clientes.')
    
    return redirect('product_index')



@login_required
def email_test_send(request):
    """Enviar correo de prueba al usuario actual"""
    email_uc = get_email_usecases()
    success = email_uc.send_welcome_email(request.user.id)
    
    if success:
        messages.success(request, f'Correo de prueba enviado a {request.user.email}')
    else:
        messages.error(request, 'Error enviando correo de prueba.')
    
    return redirect('dashboard_admin' if request.user.is_admin() else 'dashboard_cliente')
