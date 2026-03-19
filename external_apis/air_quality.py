"""
Air Quality Index (AQI) API integration.
"""

import requests
from django.conf import settings
import random


def get_current_aqi(city, lat=None, lon=None):
    """Fetch current AQI data."""
    api_key = settings.AQI_API_KEY
    
    if api_key == 'demo_key':
        return get_mock_aqi(city)
    
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('status') == 'ok':
            aqi_data = data['data']
            return {
                'city': city,
                'aqi': aqi_data['aqi'],
                'category': get_aqi_category(aqi_data['aqi']),
                'dominant_pollutant': aqi_data.get('dominentpol', 'pm25'),
                'pm25': aqi_data.get('iaqi', {}).get('pm25', {}).get('v', 0),
                'pm10': aqi_data.get('iaqi', {}).get('pm10', {}).get('v', 0),
                'source': 'WAQI',
                'status': 'live',
            }
    except Exception:
        pass
    
    return get_mock_aqi(city)


def get_aqi_category(aqi):
    """Get AQI category label."""
    if aqi <= 50:
        return 'Good'
    elif aqi <= 100:
        return 'Satisfactory'
    elif aqi <= 200:
        return 'Moderate'
    elif aqi <= 300:
        return 'Poor'
    elif aqi <= 400:
        return 'Very Poor'
    else:
        return 'Severe'


def get_mock_aqi(city):
    """Mock AQI data for demo purposes."""
    city_aqi = {
        'delhi': 280,
        'noida': 260,
        'gurgaon': 250,
        'lucknow': 200,
        'mumbai': 120,
        'chennai': 80,
        'bangalore': 70,
        'kolkata': 150,
        'hyderabad': 100,
        'pune': 90,
        'jaipur': 160,
    }
    
    base_aqi = city_aqi.get(city.lower(), 100)
    aqi = base_aqi + random.randint(-30, 30)
    aqi = max(10, aqi)
    
    return {
        'city': city.title(),
        'aqi': aqi,
        'category': get_aqi_category(aqi),
        'dominant_pollutant': 'pm25',
        'pm25': round(aqi * 0.8, 1),
        'pm10': round(aqi * 1.2, 1),
        'source': 'Mock Data',
        'status': 'mock',
    }
