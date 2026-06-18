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
        # En Railway ejecutar síncronamente para evitar problemas con background tasks
        import os
        if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_SERVICE_NAME'):
            # Ejecución síncrona en Railway
            return self._send_mass_email_sync(subject, message, user_role)
        else:
            # Ejecución asíncrona en desarrollo local
            _send_mass_email_task(subject, message, user_role)
            return 0
    
    def _send_mass_email_sync(self, subject: str, message: str, user_role: str = None) -> int:
        """Versión síncrona para Railway"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            users = self._user_repo.find_all()
            
            if user_role:
                users = [u for u in users if user_role.lower() in [r.lower() for r in u.roles]]
            
            logger.info(f"Preparando envío masivo síncrono a {len(users)} usuarios")
            
            messages = []
            for user in users:
                if user.email and user.is_active:
                    personalized_message = message.replace('{name}', user.name)
                    messages.append((subject, personalized_message, settings.DEFAULT_FROM_EMAIL, [user.email]))
            
            if messages:
                try:
                    result = send_mass_mail(messages, fail_silently=False)
                    logger.info(f"Envío masivo síncrono completado: {result} correos enviados")
                    return result
                except Exception as email_error:
                    logger.error(f"Error específico de SMTP: {str(email_error)}")
                    # Intentar enviar uno por uno si falla el envío masivo
                    sent_count = 0
                    for subject, message, from_email, recipient_list in messages:
                        try:
                            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                            sent_count += 1
                        except Exception as individual_error:
                            logger.error(f"Error enviando a {recipient_list[0]}: {str(individual_error)}")
                    logger.info(f"Envío individual completado: {sent_count}/{len(messages)} correos enviados")
                    return sent_count
            else:
                logger.warning("No hay usuarios válidos para enviar correos")
                return 0
                
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