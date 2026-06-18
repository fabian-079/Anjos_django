import requests
import json
from django.conf import settings

class EmailAPIService:
    def __init__(self):
        self.api_key = getattr(settings, 'BREVO_API_KEY', None)
        self.base_url = 'https://api.brevo.com/v3'
    
    def send_email_via_api(self, to_email, subject, html_content, sender_name="ANJOS Jewelry"):
        """Enviar email usando API HTTP de Brevo (funciona en Railway)"""
        if not self.api_key:
            print("❌ ERROR: BREVO_API_KEY no está configurada")
            return False
        
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'api-key': self.api_key
        }
        
        data = {
            "sender": {
                "name": sender_name,
                "email": settings.DEFAULT_FROM_EMAIL
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content
        }
        
        try:
            print(f"📤 Enviando email via API a: {to_email}")
            response = requests.post(
                f"{self.base_url}/smtp/email",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 201:
                print(f"✅ Email enviado exitosamente a: {to_email}")
                return True
            else:
                print(f"❌ Error API a {to_email}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando API a {to_email}: {str(e)}")
            return False
    
    def send_mass_emails_via_api(self, messages):
        """Enviar múltiples emails usando API HTTP"""
        print(f"📧 Enviando {len(messages)} correos via API HTTP...")
        
        sent_count = 0
        for subject, message, from_email, recipient_list in messages:
            to_email = recipient_list[0]
            
            # Convertir mensaje plano a HTML
            html_content = f"""
            <html>
            <body>
                <p>{message.replace('\n', '<br>')}</p>
                <br>
                <p>Saludos,<br>
                <strong>ANJOS Jewelry</strong></p>
            </body>
            </html>
            """
            
            if self.send_email_via_api(to_email, subject, html_content):
                sent_count += 1
        
        print(f"📊 RESULTADO API: {sent_count}/{len(messages)} correos enviados")
        return sent_count

# Instancia global
email_api = EmailAPIService()
