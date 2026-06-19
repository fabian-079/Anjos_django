"""
Servicio profesional de integración con Wompi (Colombia).
Soporta PSE, tarjetas, efectivo y otros métodos de pago colombianos.

FLUJO PSE REAL (segun documentacion Wompi):
1. Crear transaccion con POST /transactions
2. Hacer polling con GET /transactions/{id} hasta que aparezca async_payment_url
3. Redirigir al usuario a async_payment_url para completar el pago en el banco
4. El banco redirige de vuelta a redirect_url
"""
import hashlib
import os
import time
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
        self.public_key = self._get_env('WOMPI_PUBLIC_KEY')
        self.private_key = self._get_env('WOMPI_PRIVATE_KEY')
        self.integrity_key = self._get_env('WOMPI_INTEGRITY_KEY')
        self.base_url = "https://sandbox.wompi.co/v1"
        self._acceptance_tokens = None

    @staticmethod
    def _get_env(name: str) -> str:
        val = getattr(settings, name, '')
        if not val:
            val = os.environ.get(name, '')
        return str(val).strip() if val else ''

    def is_configured(self) -> bool:
        return bool(self.public_key and self.private_key and self.integrity_key)

    def get_config_status(self) -> dict:
        return {
            'public_key_present': bool(self.public_key),
            'public_key_prefix': self.public_key[:7] + '...' if self.public_key else 'N/A',
            'private_key_present': bool(self.private_key),
            'private_key_prefix': self.private_key[:7] + '...' if self.private_key else 'N/A',
            'integrity_key_present': bool(self.integrity_key),
            'integrity_key_prefix': self.integrity_key[:15] + '...' if self.integrity_key else 'N/A',
            'configured': self.is_configured(),
        }

    def get_acceptance_tokens(self) -> dict:
        if self._acceptance_tokens:
            return self._acceptance_tokens
        if not self.is_configured():
            return {'acceptance_token': '', 'accept_personal_auth': ''}
        try:
            resp = requests.get(f"{self.base_url}/merchants/{self.public_key}", timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                merchant = data.get('data', {})
                presigned = merchant.get('presigned_acceptance', {})
                personal = merchant.get('presigned_personal_data_auth', {})
                self._acceptance_tokens = {
                    'acceptance_token': presigned.get('acceptance_token', ''),
                    'accept_personal_auth': personal.get('acceptance_token', ''),
                }
                return self._acceptance_tokens
        except Exception:
            pass
        return {'acceptance_token': '', 'accept_personal_auth': ''}

    def build_absolute_url(self, path: str) -> str:
        base = getattr(settings, 'BASE_URL', '')
        if not base:
            base = 'https://anjosdjango-production.up.railway.app'
        base = base.rstrip('/')
        path = path.lstrip('/')
        return f"{base}/{path}"

    def _build_signature(self, reference: str, amount_in_cents: int, currency: str) -> str:
        message = f"{reference}{amount_in_cents}{currency}{self.integrity_key}"
        return hashlib.sha256(message.encode('utf-8')).hexdigest()

    def _generate_unique_reference(self, order_number: str) -> str:
        timestamp = int(time.time() * 1000)
        return f"ANJOS-{order_number}-{timestamp}"

    @staticmethod
    def extract_order_number_from_reference(reference: str) -> str:
        if not reference.startswith('ANJOS-'):
            return reference
        rest = reference[6:]
        parts = rest.rsplit('-', 1)
        if len(parts) == 2 and parts[1].isdigit():
            return parts[0]
        return rest

    def get_pse_banks(self) -> list:
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

    def _get_test_bank_code(self, bank_code: str, bank_name: str = '') -> str:
        name_lower = (bank_name or '').lower()
        if 'aprueba' in name_lower:
            return '1'
        if 'declina' in name_lower or 'rechaza' in name_lower:
            return '2'
        if 'error' in name_lower:
            return '3'
        return bank_code

    def _poll_async_payment_url(self, transaction_id: str, max_attempts: int = 15, delay: float = 2.0) -> dict:
        """
        Wompi PSE es asincrono: la transaccion se crea pero async_payment_url
        aparece despues de unos segundos. Hacemos polling hasta obtenerla.
        """
        for attempt in range(1, max_attempts + 1):
            try:
                resp = requests.get(
                    f"{self.base_url}/transactions/{transaction_id}",
                    headers={"Authorization": f"Bearer {self.public_key}"},
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    txn = data.get('data', {})
                    status = txn.get('status', '')
                    payment_method = txn.get('payment_method', {})
                    extra = payment_method.get('extra', {}) if isinstance(payment_method, dict) else {}
                    async_url = extra.get('async_payment_url') if isinstance(extra, dict) else None

                    if async_url:
                        return {
                            'found': True,
                            'async_url': async_url,
                            'status': status,
                            'attempt': attempt,
                        }

                    # Si el estado es ERROR o DECLINED, no tiene sentido seguir
                    if status in ('ERROR', 'DECLINED', 'VOIDED'):
                        return {
                            'found': False,
                            'error': f'Transaccion en estado {status}, no se puede continuar.',
                            'attempt': attempt,
                        }

                time.sleep(delay)
            except Exception as e:
                if attempt == max_attempts:
                    return {'found': False, 'error': f'Error en polling: {str(e)}', 'attempt': attempt}
                time.sleep(delay)

        return {
            'found': False,
            'error': f'Timeout: no se obtuvo async_payment_url despues de {max_attempts} intentos.',
            'attempt': max_attempts,
        }

    def create_pse_transaction(self, order, order_items, bank_code: str,
                                user_type: int, user_legal_id: str,
                                user_legal_id_type: str,
                                customer_email: str,
                                customer_name: str = '',
                                customer_phone: str = '',
                                bank_name: str = '') -> dict:
        """
        Crear una transacción PSE en Wompi con polling para obtener async_payment_url.
        Retorna dict con: success, transaction_id, redirect_url, error
        """
        if not self.is_configured():
            return {'success': False, 'error': 'Wompi no está configurado. Contacta al administrador.'}

        try:
            total_cents = int(order.total * 100)
            reference = self._generate_unique_reference(order.order_number)
            redirect_url = self.build_absolute_url('/orders/wompi/callback/')
            currency = "COP"
            actual_bank_code = self._get_test_bank_code(bank_code, bank_name)
            signature = self._build_signature(reference, total_cents, currency)

            tokens = self.get_acceptance_tokens()
            acceptance_token = tokens.get('acceptance_token', '')
            accept_personal_auth = tokens.get('accept_personal_auth', '')

            if not acceptance_token or not accept_personal_auth:
                return {'success': False, 'error': 'No se pudieron obtener los tokens de aceptacion de Wompi.'}

            description = f"ANJOS {order.order_number}"
            if len(description) > 30:
                description = description[:30]

            phone = customer_phone or '573000000000'
            phone = phone.replace('+', '').replace(' ', '').replace('-', '')
            if not phone.startswith('57'):
                phone = '57' + phone

            payload = {
                "acceptance_token": acceptance_token,
                "accept_personal_auth": accept_personal_auth,
                "amount_in_cents": total_cents,
                "currency": currency,
                "customer_email": customer_email,
                "customer_data": {
                    "phone_number": phone,
                    "full_name": customer_name or "Cliente ANJOS",
                },
                "payment_method": {
                    "type": "PSE",
                    "user_type": user_type,
                    "user_legal_id": user_legal_id,
                    "user_legal_id_type": user_legal_id_type,
                    "financial_institution_code": actual_bank_code,
                    "payment_description": description,
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
                transaction_id = transaction_data.get('id')
                initial_status = transaction_data.get('status')

                if not transaction_id:
                    return {'success': False, 'error': 'Wompi no devolvio ID de transaccion.'}

                # Wompi PSE requiere polling: la URL de redireccion NO aparece inmediatamente
                poll_result = self._poll_async_payment_url(transaction_id)

                if poll_result['found']:
                    return {
                        'success': True,
                        'transaction_id': transaction_id,
                        'status': poll_result['status'],
                        'redirect_url': poll_result['async_url'],
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Transaccion creada (ID: {transaction_id}, estado: {initial_status}) '
                                 f'pero no se obtuvo URL de pago: {poll_result["error"]} '
                                 f'(intentos: {poll_result["attempt"]})',
                    }
            else:
                error_msg = 'Error desconocido de Wompi'
                error_details = ''
                try:
                    if 'error' in data:
                        err = data['error']
                        if isinstance(err, dict):
                            error_msg = err.get('reason') or err.get('message') or err.get('type') or str(err)
                            extra_err = err.get('extra', {})
                            if extra_err:
                                error_details = str(extra_err)
                        else:
                            error_msg = str(err)
                    elif 'message' in data:
                        error_msg = data['message']
                except Exception:
                    pass

                return {
                    'success': False,
                    'error': error_msg,
                    'error_details': error_details,
                    'debug_status': resp.status_code,
                }

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Tiempo de espera agotado con Wompi. Intenta nuevamente.'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'No se pudo conectar con Wompi. Verifica tu conexion.'}
        except Exception as e:
            return {'success': False, 'error': f'Error inesperado: {str(e)}'}

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
            return {'success': False, 'error': 'Transaccion no encontrada'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
