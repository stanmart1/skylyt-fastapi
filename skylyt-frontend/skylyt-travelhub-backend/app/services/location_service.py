from typing import Optional, Dict
import httpx
from app.utils.cache_manager import cache_manager


class LocationService:
    COUNTRY_CURRENCY_MAP = {
        'NG': 'NGN',  # Nigeria (default)
        'US': 'USD',  # United States
        'GB': 'GBP',  # United Kingdom
        'CA': 'USD',  # Canada
        'DE': 'EUR',  # Germany
        'FR': 'EUR',  # France
        'IT': 'EUR',  # Italy
        'ES': 'EUR',  # Spain
    }
    
    NIGERIAN_CITIES = ['Port Harcourt', 'Lagos', 'Abuja']
    
    @staticmethod
    async def detect_location_from_ip(ip_address: str) -> Dict[str, str]:
        """Detect country and currency from IP address"""
        cache_key = f"location_{ip_address}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient() as client:
                # Using ipapi.co (free tier)
                response = await client.get(f"https://ipapi.co/{ip_address}/json/")
                data = response.json()
                
                country_code = data.get('country_code', 'NG')
                country_name = data.get('country_name', 'Nigeria')
                city = data.get('city', '')
                
                result = {
                    'country_code': country_code,
                    'country_name': country_name,
                    'city': city,
                    'currency': LocationService.COUNTRY_CURRENCY_MAP.get(country_code, 'NGN'),
                    'is_nigeria': country_code == 'NG',
                    'is_supported_city': city in LocationService.NIGERIAN_CITIES
                }
                
                # Cache for 1 hour
                cache_manager.set(cache_key, result, 3600)
                return result
                
        except Exception as e:
            print(f"Location detection failed: {e}")
            # Default to Nigeria
            return {
                'country_code': 'NG',
                'country_name': 'Nigeria',
                'city': '',
                'currency': 'NGN',
                'is_nigeria': True,
                'is_supported_city': False
            }
    
    @staticmethod
    def get_supported_countries() -> Dict[str, Dict[str, str]]:
        return {
            'NG': {'name': 'Nigeria', 'currency': 'NGN', 'flag': '🇳🇬'},
            'US': {'name': 'United States', 'currency': 'USD', 'flag': '🇺🇸'},
            'GB': {'name': 'United Kingdom', 'currency': 'GBP', 'flag': '🇬🇧'},
            'CA': {'name': 'Canada', 'currency': 'USD', 'flag': '🇨🇦'},
            'DE': {'name': 'Germany', 'currency': 'EUR', 'flag': '🇩🇪'},
            'FR': {'name': 'France', 'currency': 'EUR', 'flag': '🇫🇷'},
        }