from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from adapters.api.decorators import admin_required
from infrastructure.container import get_email_usecases

@admin_required
def email_mass_send_form(request):
    return render(request, 'emails/mass_send.html')

def email_mass_send_debug(request):
    """Vista de debug sin decoradores para probar si llega la petición"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🚨🚨🚨 VISTA DEBUG SIN DECORADORES LLAMADA")
    logger.info(f"   Método: {request.method}")
    logger.info(f"   User: {request.user}")
    logger.info(f"   Headers: {dict(request.headers)}")
    
    if request.method == 'POST':
        logger.info("   Es POST - procesando...")
        return JsonResponse({"status": "debug_received", "method": "POST"})
    else:
        logger.info("   No es POST")
        return JsonResponse({"status": "debug_received", "method": "GET"})

@admin_required
def email_mass_send(request):
    print("🔥🔥🔥 VISTA email_mass_send LLAMADA - RAILWAY")
    print(f"   Método: {request.method}")
    
    if request.method != 'POST':
        print("   No es POST - redirigiendo")
        return redirect('email_mass_send_form')
    
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()
    recipient_type = request.POST.get('recipient_type', 'all')
    
    print(f"   Datos recibidos: subject='{subject}', message_length={len(message)}, recipient_type='{recipient_type}'")
    
    if not subject or not message:
        print("   ❌ Faltan datos - subject o message vacíos")
        messages.error(request, 'Asunto y mensaje son requeridos.')
        return redirect('email_mass_send_form')
    
    print("   Obteniendo email use cases...")
    email_uc = get_email_usecases()
    role = 'cliente' if recipient_type == 'clients' else ('admin' if recipient_type == 'admins' else None)
    
    print(f"   Role determinado: '{role}'")
    print("   Llamando a send_mass_promotional_email...")
    
    try:
        # Llamada asíncrona con cola
        result = email_uc.send_mass_promotional_email(subject, message, role)
        print(f"   ✅ Tarea agregada a cola: {result}")
        
        # Obtener estado de la cola
        from application.services.email_queue_service import email_queue
        status = email_queue.get_queue_status()
        
        messages.success(request, f'Envío masivo agregado a la cola. Pendientes: {status["pending"]}, Procesando: {status["processing"]}, Completados: {status["completed"]}')
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        messages.error(request, f'Error al agregar a la cola: {e}')
    
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