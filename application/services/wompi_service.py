"""
Servicio profesional de integración con Wompi (Colombia).
Soporta PSE, tarjetas, efectivo y otros métodos de pago colombianos.
"""
import hashlib
import requests
from django.conf import settings


# Lista de bancos PSE más comunes (fallback si la API de Wompi no responde)
DEFAULT_PSE_BANKS = [
    {"code": "1040", "name": "Bancolombia"},
    {"code": "1001", "name": "Banco de Bogotá"},
    {"code": "1052", "name": "Davivienda"},
    {"code": "1013", "name": "BBVA Colombia"},
    {"code": "1057", "name": "Banco Popular"},
    {"code": "1002", "name": "Banco de Occidente"},
    {"code": "1012", "name": "Banco GNB Sudameris"},
    {"code": "1061", "name": "Bancoomeva"},
    {"code": "1065", "name": "Nequi (Bancolombia)"},
    {"code": "1078", "name": "Banco Falabella"},
    {"code": "1081", "name": "Banco Pichincha"},
    {"code": "1032", "name": "Banco Caja Social"},
    {"code": "1062", "name": "Itaú"},
    {"code": "1007", "name": "Banco Citibank"},
    {"code": "1058", "name": "Banco Protección"},
]


class WompiService:
    """Servicio de Wompi para ANJOS Jewelry."""

    def __init__(self):
        self.public_key = getattr(settings, 'WOMPI_PUBLIC_KEY', '')
        self.private_key = getattr(settings, 'WOMPI_PRIVATE_KEY', '')
        self.integrity_key = getattr(settings, 'WOMPI_INTEGRITY_KEY', '')
        # Sandbox por defecto, cambiar a producción cuando esté listo
        self.base_url = "https://sandbox.wompi.co/v1"

    def is_configured(self) -> bool:
        """Verificar si Wompi tiene credenciales reales configuradas."""
        return bool(
            self.public_key
            and self.public_key.startswith('pub_')
            and self.private_key
            and self.private_key.startswith('prv_')
        )

    def build_absolute_url(self, path: str) -> str:
        """Construir URL absoluta usando BASE_URL configurado."""
        base = getattr(settings, 'BASE_URL', '')
        if not base:
            base = 'https://anjosdjango-production.up.railway.app'
        base = base.rstrip('/')
        path = path.lstrip('/')
        return f"{base}/{path}"

    def _build_signature(self, reference: str, amount_in_cents: int, currency: str) -> str:
        """
        Construir firma de integridad para Wompi.
        Wompi requiere: SHA-256( reference + amount_in_cents + currency + integrity_key )
        Todo como strings concatenados sin separadores.
        """
        message = f"{reference}{amount_in_cents}{currency}{self.integrity_key}"
        return hashlib.sha256(message.encode('utf-8')).hexdigest()

    def get_pse_banks(self) -> list:
        """Obtener lista de bancos PSE desde Wompi API."""
        # Siempre usar fallback por defecto (más confiable que la API en sandbox)
        fallback = list(DEFAULT_PSE_BANKS)

        if not self.is_configured():
            return fallback

        try:
            resp = requests.get(
                f"{self.base_url}/pse/financial_institutions",
                headers={"Authorization": f"Bearer {self.public_key}"},
                timeout=8,
            )
            if resp.status_code == 200:
                data = resp.json()
                raw_banks = data.get('data', [])
                if raw_banks and isinstance(raw_banks, list) and len(raw_banks) > 0:
                    # Normalizar formato: Wompi puede devolver code/name o financial_institution_code/financial_institution_name
                    normalized = []
                    for b in raw_banks:
                        code = b.get('code') or b.get('financial_institution_code')
                        name = b.get('name') or b.get('financial_institution_name')
                        if code and name:
                            normalized.append({'code': str(code), 'name': str(name)})
                    if normalized:
                        return sorted(normalized, key=lambda x: x['name'])
        except Exception:
            pass

        return fallback

    def create_pse_transaction(self, order, order_items, bank_code: str,
                                user_type: int, user_legal_id: str,
                                user_legal_id_type: str,
                                customer_email: str) -> dict:
        """
        Crear una transacción PSE en Wompi.
        Retorna dict con: success, transaction_id, redirect_url, error
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Wompi no está configurado. Contacta al administrador.'
            }

        try:
            total_cents = int(order.total * 100)
            reference = f"ANJOS-{order.order_number}"
            redirect_url = self.build_absolute_url('/orders/wompi/callback/')
            currency = "COP"

            # Calcular firma de integridad (obligatoria en Wompi)
            signature = self._build_signature(reference, total_cents, currency)

            payload = {
                "amount_in_cents": total_cents,
                "currency": currency,
                "customer_email": customer_email,
                "payment_method": {
                    "type": "PSE",
                    "user_type": user_type,
                    "user_legal_id": user_legal_id,
                    "user_legal_id_type": user_legal_id_type,
                    "financial_institution_code": bank_code,
                    "payment_description": f"Compra {order.order_number} en ANJOS Jewelry",
                },
                "reference": reference,
                "redirect_url": redirect_url,
                "signature": signature,
            }

            resp = requests.post(
                f"{self.base_url}/transactions",
                headers={
                    "Authorization": f"Bearer {self.private_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=15,
            )

            data = resp.json()

            if resp.status_code in (200, 201):
                transaction_data = data.get('data', {})
                payment_method = transaction_data.get('payment_method', {})
                extra = payment_method.get('extra', {})
                redirect_url = extra.get('async_payment_url') or extra.get('external_identifier')

                return {
                    'success': True,
                    'transaction_id': transaction_data.get('id'),
                    'status': transaction_data.get('status'),
                    'redirect_url': redirect_url,
                }
            else:
                # Intentar extraer mensaje de error en cualquier formato
                error_msg = 'Error desconocido de Wompi'
                try:
                    if 'error' in data:
                        err = data['error']
                        if isinstance(err, dict):
                            error_msg = err.get('reason') or err.get('message') or err.get('type') or str(err)
                        else:
                            error_msg = str(err)
                    elif 'message' in data:
                        error_msg = data['message']
                    elif 'errors' in data and isinstance(data['errors'], list):
                        error_msg = '; '.join(str(e) for e in data['errors'])
                except Exception:
                    pass

                return {
                    'success': False,
                    'error': error_msg,
                    'debug_status': resp.status_code,
                    'debug_response': str(data)[:500],
                }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Tiempo de espera agotado con Wompi. Intenta nuevamente.'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'No se pudo conectar con Wompi. Verifica tu conexión.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }

    def get_transaction_status(self, transaction_id: str) -> dict:
        """Consultar el estado de una transacción Wompi."""
        if not self.is_configured():
            return {'success': False, 'error': 'Wompi no configurado'}
        try:
            resp = requests.get(
                f"{self.base_url}/transactions/{transaction_id}",
                headers={"Authorization": f"Bearer {self.public_key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                transaction = data.get('data', {})
                return {
                    'success': True,
                    'status': transaction.get('status'),
                    'reference': transaction.get('reference'),
                }
            return {'success': False, 'error': 'Transacción no encontrada'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
