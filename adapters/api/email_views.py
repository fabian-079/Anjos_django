from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from adapters.api.decorators import admin_required
from infrastructure.container import get_email_usecases

@admin_required
def email_mass_send_form(request):
    return render(request, 'emails/mass_send.html')

@admin_required
def email_mass_send(request):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🔥 VISTA email_mass_send LLAMADA")
    logger.info(f"   Método: {request.method}")
    
    if request.method != 'POST':
        logger.info("   No es POST - redirigiendo")
        return redirect('email_mass_send_form')
    
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()
    recipient_type = request.POST.get('recipient_type', 'all')
    
    logger.info(f"   Datos recibidos: subject='{subject}', message_length={len(message)}, recipient_type='{recipient_type}'")
    
    if not subject or not message:
        logger.warning("   Faltan datos - subject o message vacíos")
        messages.error(request, 'Asunto y mensaje son requeridos.')
        return redirect('email_mass_send_form')
    
    logger.info("   Obteniendo email use cases...")
    email_uc = get_email_usecases()
    role = 'cliente' if recipient_type == 'clients' else ('admin' if recipient_type == 'admins' else None)
    
    logger.info(f"   Role determinado: '{role}'")
    logger.info("   Llamando a send_mass_promotional_email...")
    
    try:
        # Llamada directa para evitar problemas
        result = email_uc.send_mass_promotional_email(subject, message, role)
        logger.info(f"   ✅ Resultado: {result}")
        messages.success(request, f'Envío masivo completado: {result} correos procesados.')
    except Exception as e:
        logger.error(f"   ❌ Error: {str(e)}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        messages.error(request, f'Error al iniciar el envío: {e}')
    
    return redirect('email_mass_send_form')

@admin_required
def email_new_products_notification(request):
    if request.method != 'POST':
        return redirect('product_index')
    
    product_ids = request.POST.getlist('product_ids')
    if not product_ids:
        messages.error(request, 'Selecciona al menos un producto.')
        return redirect('product_index')
    
    from infrastructure.container import get_product_usecases
    product_uc = get_product_usecases()
    product_names = [product.name for pid in product_ids if (product := product_uc.get_product_by_id(int(pid)))]
    
    if product_names:
        email_uc = get_email_usecases()
        count = email_uc.send_new_products_notification(product_names)
        messages.success(request, f'Notificación enviada a {count} clientes.')
    
    return redirect('product_index')

@login_required
def email_test_send(request):
    email_uc = get_email_usecases()
    success = email_uc.send_welcome_email(request.user.id)
    if success:
        messages.success(request, f'Correo de prueba enviado a {request.user.email}')
    else:
        messages.error(request, 'Error enviando correo de prueba.')
    return redirect('dashboard_admin' if request.user.is_admin() else 'dashboard_cliente')