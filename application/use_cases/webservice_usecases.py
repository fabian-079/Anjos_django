import requests
from typing import Dict, Optional
from decimal import Decimal
from django.conf import settings


class WebServiceUseCases:
    """Casos de uso para consumo de Web Services externos"""
    
    def __init__(self):
        self.exchange_api_url = settings.EXCHANGE_RATE_API_URL
    
    def get_exchange_rates(self, base_currency: str = 'USD') -> Optional[Dict]:
        """
        Consumir API de tasas de cambio
        API pública: https://api.exchangerate-api.com/v4/latest/USD
        """
        try:
            url = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'base': data.get('base'),
                'date': data.get('date'),
                'rates': data.get('rates', {})
            }
        except requests.exceptions.RequestException as e:
            print(f"Error consumiendo API de tasas de cambio: {e}")
            return None
    
    def convert_currency(self, amount: Decimal, from_currency: str, 
                        to_currency: str) -> Optional[Decimal]:
        """Convertir moneda usando API externa"""
        rates_data = self.get_exchange_rates(from_currency)
        if not rates_data or 'rates' not in rates_data:
            return None
        
        rate = rates_data['rates'].get(to_currency)
        if not rate:
            return None
        
        return amount * Decimal(str(rate))
    
    def get_product_price_in_currency(self, price_usd: Decimal, 
                                     currency: str) -> Optional[Dict]:
        """Obtener precio de producto en diferentes monedas"""
        converted_price = self.convert_currency(price_usd, 'USD', currency)
        if not converted_price:
            return None
        
        return {
            'original_price': float(price_usd),
            'original_currency': 'USD',
            'converted_price': float(converted_price),
            'target_currency': currency
        }
    
    def validate_email_api(self, email: str) -> Dict:
        """
        Validar email usando API externa (ejemplo con API pública)
        Nota: Esta es una API de ejemplo, en producción usar un servicio real
        """
        try:
            # API pública de validación de email (ejemplo)
            url = f'https://emailvalidation.abstractapi.com/v1/?api_key=test&email={email}'
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'valid': data.get('is_valid_format', {}).get('value', False),
                    'email': email,
                    'provider': 'AbstractAPI'
                }
        except Exception:
            pass
        
        # Fallback: validación básica local
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return {
            'valid': bool(re.match(pattern, email)),
            'email': email,
            'provider': 'Local'
        }
    
    def get_gold_price(self) -> Optional[Dict]:
        """
        Obtener precio del oro desde API externa
        API pública: https://api.gold-api.com/price/XAU
        """
        try:
            url = 'https://api.gold-api.com/price/XAU'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                'price': data.get('price'),
                'currency': data.get('currency', 'USD'),
                'unit': 'troy ounce',
                'timestamp': data.get('updatedAt'),
                'updated': data.get('updatedAtReadable'),
            }
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo precio del oro: {e}")
            return None
    
    def get_location_info(self, ip_address: str = None) -> Optional[Dict]:
        """
        Obtener información de ubicación por IP
        API pública: https://ipapi.co/{ip}/json/
        """
        try:
            if not ip_address:
                # Obtener IP pública del servidor
                ip_response = requests.get('https://api.ipify.org?format=json', timeout=5)
                ip_address = ip_response.json().get('ip')
            
            url = f'https://ipapi.co/{ip_address}/json/'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'ip': data.get('ip'),
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country_name'),
                'country_code': data.get('country_code'),
                'currency': data.get('currency'),
                'timezone': data.get('timezone')
            }
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo información de ubicación: {e}")
            return None
    
    def get_weather_info(self, city: str) -> Optional[Dict]:
        """
        Obtener información del clima (ejemplo de consumo de API)
        Nota: Requiere API key en producción
        """
        try:
            # API pública de clima (wttr.in)
            url = f'https://wttr.in/{city}?format=j1'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data.get('current_condition', [{}])[0]
            return {
                'city': city,
                'temperature_c': current.get('temp_C'),
                'temperature_f': current.get('temp_F'),
                'description': current.get('weatherDesc', [{}])[0].get('value'),
                'humidity': current.get('humidity')
            }
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo información del clima: {e}")
            return None
    
    def verify_phone_number(self, phone: str, country_code: str = 'CO') -> Dict:
        """
        Verificar número de teléfono (ejemplo básico)
        En producción usar servicios como Twilio Lookup API
        """
        import re
        
        # Validación básica para Colombia
        if country_code == 'CO':
            # Formato: +57 3XX XXX XXXX o 3XXXXXXXX
            pattern = r'^(\+57)?3\d{9}$|^3\d{9}$'
            is_valid = bool(re.match(pattern, phone.replace(' ', '')))
        else:
            # Validación genérica
            pattern = r'^\+?\d{10,15}$'
            is_valid = bool(re.match(pattern, phone.replace(' ', '')))
        
        return {
            'valid': is_valid,
            'phone': phone,
            'country_code': country_code,
            'provider': 'Local Validation'
        }
    
    def get_shipping_cost(self, origin: str, destination: str, 
                         weight_kg: float) -> Dict:
        """
        Calcular costo de envío (simulación de API de envíos)
        En producción integrar con APIs de DHL, FedEx, etc.
        """
        # Simulación de cálculo de envío
        base_cost = 5000  # COP
        cost_per_km = 100  # COP
        cost_per_kg = 2000  # COP
        
        # Distancias aproximadas entre ciudades principales de Colombia
        distances = {
            ('Bogotá', 'Medellín'): 415,
            ('Bogotá', 'Cali'): 460,
            ('Bogotá', 'Barranquilla'): 990,
            ('Medellín', 'Cali'): 420,
            ('Medellín', 'Barranquilla'): 700,
            ('Cali', 'Barranquilla'): 1100,
        }
        
        # Buscar distancia
        distance = distances.get((origin, destination)) or \
                  distances.get((destination, origin)) or 300
        
        total_cost = base_cost + (distance * cost_per_km) + (weight_kg * cost_per_kg)
        
        return {
            'origin': origin,
            'destination': destination,
            'weight_kg': weight_kg,
            'distance_km': distance,
            'cost_cop': total_cost,
            'estimated_days': max(1, distance // 200),
            'provider': 'Anjos Shipping Calculator'
        }
