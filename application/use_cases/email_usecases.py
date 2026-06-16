from typing import List, Optional
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from domain.repositories.user_repository import UserRepository


class EmailUseCases:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def send_welcome_email(self, user_id: int) -> bool:
        """Enviar email de bienvenida a un usuario"""
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
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False

    def send_order_confirmation(self, user_email: str, order_number: str, total: float) -> bool:
        """Enviar confirmación de orden"""
        subject = f'Confirmación de Orden {order_number}'
        message = f'''
        Tu orden {order_number} ha sido recibida exitosamente.
        
        Total: ${total:,.2f}
        
        Te notificaremos cuando tu orden sea procesada.
        
        Gracias por tu compra,
        ANJOS
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False,
            )
            return True
        except Exception:
            return False

    def send_mass_promotional_email(self, subject: str, message: str, 
                                    user_role: str = None) -> int:
        """Enviar correo masivo a usuarios (promociones, anuncios)"""
        if user_role:
            users = [u for u in self._user_repo.find_all() 
                    if user_role.lower() in [r.lower() for r in u.roles]]
        else:
            users = self._user_repo.find_all()
        
        if not users:
            return 0
        
        messages = []
        for user in users:
            if user.email and user.is_active:
                personalized_message = message.replace('{name}', user.name)
                messages.append((
                    subject,
                    personalized_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                ))
        
        try:
            send_mass_mail(messages, fail_silently=False)
            return len(messages)
        except Exception as e:
            print(f"Error enviando correos masivos: {e}")
            return 0

    def send_new_products_notification(self, product_names: List[str]) -> int:
        """Notificar a clientes sobre nuevos productos"""
        users = [u for u in self._user_repo.find_all() 
                if 'cliente' in [r.lower() for r in u.roles] and u.is_active]
        
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
                messages.append((
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                ))
        
        try:
            send_mass_mail(messages, fail_silently=False)
            return len(messages)
        except Exception:
            return 0

    def send_repair_status_update(self, user_email: str, repair_number: str, 
                                  new_status: str) -> bool:
        """Notificar cambio de estado en reparación"""
        subject = f'Actualización de Reparación {repair_number}'
        message = f'''
        El estado de tu reparación {repair_number} ha cambiado a: {new_status}
        
        Puedes ver los detalles en tu panel de cliente.
        
        Saludos,
        ANJOS
        '''
        
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, 
                     [user_email], fail_silently=False)
            return True
        except Exception:
            return False

    def send_price_quote_email(self, user_email: str, item_type: str, 
                               estimated_price: float) -> bool:
        """Enviar cotización de precio"""
        subject = f'Cotización de {item_type}'
        message = f'''
        Hemos revisado tu solicitud de {item_type}.
        
        Precio estimado: ${estimated_price:,.2f}
        
        Este precio es aproximado y puede variar según los materiales finales.
        
        Saludos,
        ANJOS
        '''
        
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, 
                     [user_email], fail_silently=False)
            return True
        except Exception:
            return False
