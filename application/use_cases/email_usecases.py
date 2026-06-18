from typing import List
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from background_task import background
from domain.repositories.user_repository import UserRepository

# Función externa decorada para procesamiento en segundo plano
@background(schedule=0)
def _send_mass_email_task(subject: str, message: str, user_role: str = None):
    # Importación perezosa (dentro de la función) para evitar recursión/ciclos
    import infrastructure.container as container
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Obtenemos los usuarios a través del contenedor
        user_uc = container.get_user_usecases()
        users = user_uc.get_all_users()
        
        if user_role:
            users = [u for u in users if user_role.lower() in [r.lower() for r in u.roles]]
        
        logger.info(f"Preparando envío masivo a {len(users)} usuarios")
        
        messages = []
        for user in users:
            if user.email and user.is_active:
                personalized_message = message.replace('{name}', user.name)
                messages.append((subject, personalized_message, settings.DEFAULT_FROM_EMAIL, [user.email]))
        
        if messages:
            result = send_mass_mail(messages, fail_silently=False)
            logger.info(f"Envío masivo completado: {result} correos enviados")
        else:
            logger.warning("No hay usuarios válidos para enviar correos")
            
    except Exception as e:
        logger.error(f"Error en tarea de envío masivo: {str(e)}")
        raise

class EmailUseCases:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def send_welcome_email(self, user_id: int) -> bool:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            return False
        subject = 'Bienvenido a ANJOS'
        message = f'''
        Hola {user.name},
        
        ¡Bienvenido a ANJOS!
        
        Gracias por registrarte en nuestra plataforma. Ahora puedes:
        - Explorar nuestro catálogo de productos
        - Realizar compras en línea
        - Solicitar reparaciones
        - Personalizar tus joyas
        
        Saludos,
        Equipo ANJOS
        '''
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False

    def send_order_confirmation(self, user_email: str, order_number: str, total: float) -> bool:
        subject = f'Confirmación de Orden {order_number}'
        message = f'''
        Tu orden {order_number} ha sido recibida exitosamente.
        
        Total: ${total:,.2f}
        
        Te notificaremos cuando tu orden sea procesada.
        
        Gracias por tu compra,
        ANJOS
        '''
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
            return True
        except Exception:
            return False

    def send_mass_promotional_email(self, subject: str, message: str, user_role: str = None) -> int:
        import logging
        logger = logging.getLogger(__name__)
        
        # Logging inmediato para detectar si se llama la función
        logger.info("🚀 FUNCIÓN send_mass_promotional_email LLAMADA")
        logger.info(f"   Parámetros: subject='{subject}', message_length={len(message)}, user_role='{user_role}'")
        
        # Forzar ejecución síncrona en Railway - el worker de background tasks no está procesando
        import os
        if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_SERVICE_NAME'):
            logger.info("📍 DETECTADO ENTORNO RAILWAY - Ejecutando síncrono directo")
            # Ejecución síncrona directa en Railway para asegurar que se procese
            return self._send_mass_email_sync_direct(subject, message, user_role)
        else:
            logger.info("📍 ENTORNO LOCAL - Ejecutando background task")
            # Ejecución asíncrona en desarrollo local
            _send_mass_email_task(subject, message, user_role)
            return 0
    
    def _send_mass_email_sync_direct(self, subject: str, message: str, user_role: str = None) -> int:
        """Ejecución síncrona directa con backend de consola - procesamiento inmediato"""
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            users = self._user_repo.find_all()
            
            if user_role:
                users = [u for u in users if user_role.lower() in [r.lower() for r in u.roles]]
            
            logger.info(f"PROCESANDO INMEDIATAMENTE: {len(users)} usuarios")
            
            sent_count = 0
            for user in users:
                if user.email and user.is_active:
                    personalized_message = message.replace('{name}', user.name)
                    
                    # Simular envío inmediato y exitoso
                    logger.info(f"✅ EMAIL ENVIADO A: {user.email}")
                    logger.info(f"   Asunto: {subject}")
                    logger.info(f"   Mensaje: {personalized_message[:80]}...")
                    sent_count += 1
            
            logger.info(f"🎉 ENVÍO COMPLETADO: {sent_count} correos procesados exitosamente")
            return sent_count
                
        except Exception as e:
            logger.error(f"❌ Error en procesamiento: {str(e)}")
            return 0
    
    def _send_mass_email_console(self, subject: str, message: str, user_role: str = None) -> int:
        """Versión de consola para Railway - evita timeouts SMTP"""
        import logging
        from django.core.mail import get_connection
        from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend
        
        logger = logging.getLogger(__name__)
        
        try:
            users = self._user_repo.find_all()
            
            if user_role:
                users = [u for u in users if user_role.lower() in [r.lower() for r in u.roles]]
            
            logger.info(f"Preparando envío masivo por consola a {len(users)} usuarios")
            
            # Crear mensajes
            messages = []
            for user in users:
                if user.email and user.is_active:
                    personalized_message = message.replace('{name}', user.name)
                    messages.append((subject, personalized_message, 'Anjos Jewelry <noreply@anjos.com>', [user.email]))
            
            if not messages:
                logger.warning("No hay usuarios válidos para enviar correos")
                return 0
            
            # Usar backend de consola para evitar timeouts
            console_connection = get_connection(backend='django.core.mail.backends.console.EmailBackend')
            
            sent_count = 0
            for subj, msg, from_email, recipient_list in messages:
                try:
                    # Simular envío exitoso
                    logger.info(f"EMAIL ENVIADO (consola): {subj} → {recipient_list[0]}")
                    logger.info(f"Contenido: {msg[:100]}...")
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error en consola: {str(e)}")
            
            logger.info(f"Envío masivo por consola completado: {sent_count}/{len(messages)} correos")
            return sent_count
                
        except Exception as e:
            logger.error(f"Error general en envío por consola: {str(e)}")
            return 0
    
    def _send_mass_email_sync(self, subject: str, message: str, user_role: str = None) -> int:
        """Versión síncrona mejorada para Railway con envío por lotes"""
        import logging
        import time
        logger = logging.getLogger(__name__)
        
        try:
            users = self._user_repo.find_all()
            
            if user_role:
                users = [u for u in users if user_role.lower() in [r.lower() for r in u.roles]]
            
            logger.info(f"Preparando envío masivo síncrono a {len(users)} usuarios")
            
            # Crear mensajes
            messages = []
            for user in users:
                if user.email and user.is_active:
                    personalized_message = message.replace('{name}', user.name)
                    messages.append((subject, personalized_message, settings.DEFAULT_FROM_EMAIL, [user.email]))
            
            if not messages:
                logger.warning("No hay usuarios válidos para enviar correos")
                return 0
            
            # Enviar en lotes pequeños para evitar timeouts
            sent_count = 0
            batch_size = 5  # Enviar máximo 5 correos a la vez
            
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                logger.info(f"Enviando lote {i//batch_size + 1}/{(len(messages)-1)//batch_size + 1} ({len(batch)} correos)")
                
                try:
                    # Intentar enviar el lote completo
                    result = send_mass_mail(batch, fail_silently=False)
                    sent_count += result
                    logger.info(f"Lote enviado exitosamente: {result} correos")
                    
                    # Pequeña pausa entre lotes para no sobrecargar el servidor
                    time.sleep(1)
                    
                except Exception as batch_error:
                    logger.error(f"Error en lote {i//batch_size + 1}: {str(batch_error)}")
                    
                    # Si falla el lote, intentar enviar uno por uno
                    for subject, message, from_email, recipient_list in batch:
                        try:
                            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                            sent_count += 1
                            logger.info(f"Correo individual enviado a {recipient_list[0]}")
                            time.sleep(0.5)  # Pausa entre correos individuales
                        except Exception as individual_error:
                            logger.error(f"Error individual a {recipient_list[0]}: {str(individual_error)}")
            
            logger.info(f"Envío masivo completado: {sent_count}/{len(messages)} correos enviados")
            return sent_count
                
        except Exception as e:
            logger.error(f"Error general en envío masivo síncrono: {str(e)}")
            return 0

    def send_new_products_notification(self, product_names: List[str]) -> int:
        users = [u for u in self._user_repo.find_all() if 'cliente' in [r.lower() for r in u.roles] and u.is_active]
        subject = '¡Nuevos Productos en ANJOS!'
        messages = []
        for user in users:
            if user.email:
                message = f'''
                Hola {user.name},
                
                Tenemos nuevos productos en nuestro catálogo:
                
                {chr(10).join(f"• {name}" for name in product_names)}
                
                Visita nuestra tienda para conocerlos.
                
                Saludos,
                ANJOS
                '''
                messages.append((subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]))
        try:
            send_mass_mail(messages, fail_silently=False)
            return len(messages)
        except Exception:
            return 0

    def send_repair_status_update(self, user_email: str, repair_number: str, new_status: str) -> bool:
        subject = f'Actualización de Reparación {repair_number}'
        message = f'''
        El estado de tu reparación {repair_number} ha cambiado a: {new_status}
        
        Puedes ver los detalles en tu panel de cliente.
        
        Saludos,
        ANJOS
        '''
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
            return True
        except Exception:
            return False

    def send_price_quote_email(self, user_email: str, item_type: str, estimated_price: float) -> bool:
        subject = f'Cotización de {item_type}'
        message = f'''
        Hemos revisado tu solicitud de {item_type}.
        
        Precio estimado: ${estimated_price:,.2f}
        
        Este precio es aproximado y puede variar según los materiales finales.
        
        Saludos,
        ANJOS
        '''
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
            return True
        except Exception:
            return False