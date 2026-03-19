"""
Weather API integration using OpenWeatherMap free tier.
"""

import requests
from django.conf import settings
import random


OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_current_weather(city, lat=None, lon=None):
    """Fetch current weather for a city using OpenWeatherMap API."""
    api_key = settings.OPENWEATHER_API_KEY
    
    if api_key == 'demo_key':
        return get_mock_weather(city)
    
    try:
        if lat and lon:
            url = f"{OPENWEATHER_BASE_URL}/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        else:
            url = f"{OPENWEATHER_BASE_URL}/weather?q={city},IN&appid={api_key}&units=metric"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            rain_1h = data.get('rain', {}).get('1h', 0)
            return {
                'city': data.get('name', city),
                'temp_celsius': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'rain_1h_mm': rain_1h,
                'rain_probability': min(100, rain_1h * 10),
                'visibility': data.get('visibility', 10000),
                'source': 'OpenWeatherMap',
                'status': 'live',
            }
    except Exception as e:
        pass
    
    return get_mock_weather(city)


def get_weather_forecast(city, days=7):
    """Get weather forecast for the next N days."""
    api_key = settings.OPENWEATHER_API_KEY
    
    if api_key == 'demo_key':
        return get_mock_forecast(city, days)
    
    try:
        url = f"{OPENWEATHER_BASE_URL}/forecast?q={city},IN&appid={api_key}&units=metric&cnt={days*8}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            forecasts = []
            for item in data.get('list', []):
                forecasts.append({
                    'datetime': item['dt_txt'],
                    'temp': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description'],
                    'rain_mm': item.get('rain', {}).get('3h', 0),
                    'wind_speed': item['wind']['speed'],
                })
            return {'city': city, 'forecasts': forecasts, 'source': 'OpenWeatherMap', 'status': 'live'}
    except Exception:
        pass
    
    return get_mock_forecast(city, days)


def get_mock_weather(city):
    """Mock weather data for demo/development."""
    # Realistic mock data based on Indian cities in March
    city_defaults = {
        'mumbai': {'temp': 32, 'humidity': 65, 'rain': 0},
        'delhi': {'temp': 28, 'humidity': 45, 'rain': 0},
        'chennai': {'temp': 34, 'humidity': 75, 'rain': 2},
        'kolkata': {'temp': 30, 'humidity': 70, 'rain': 1},
        'bangalore': {'temp': 28, 'humidity': 55, 'rain': 0},
        'hyderabad': {'temp': 33, 'humidity': 50, 'rain': 0},
        'pune': {'temp': 31, 'humidity': 45, 'rain': 0},
        'jaipur': {'temp': 30, 'humidity': 35, 'rain': 0},
    }
    
    defaults = city_defaults.get(city.lower(), {'temp': 30, 'humidity': 50, 'rain': 0})
    variation = random.uniform(-3, 3)
    
    return {
        'city': city.title(),
        'temp_celsius': round(defaults['temp'] + variation, 1),
        'feels_like': round(defaults['temp'] + variation + 2, 1),
        'humidity': defaults['humidity'] + random.randint(-5, 5),
        'description': 'partly cloudy' if defaults['rain'] == 0 else 'light rain',
        'icon': '02d' if defaults['rain'] == 0 else '10d',
        'wind_speed': round(random.uniform(2, 8), 1),
        'rain_1h_mm': defaults['rain'] + random.uniform(0, 2),
        'rain_probability': defaults['rain'] * 20 + random.randint(0, 20),
        'visibility': 8000 + random.randint(-2000, 2000),
        'source': 'Mock Data',
        'status': 'mock',
    }


def get_mock_forecast(city, days=7):
    """Mock weather forecast data."""
    import datetime
    forecasts = []
    base_temp = 30
    
    for d in range(days):
        for hour in [6, 12, 18]:
            dt = datetime.datetime.now() + datetime.timedelta(days=d, hours=hour)
            forecasts.append({
                'datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'temp': round(base_temp + random.uniform(-5, 8), 1),
                'humidity': random.randint(40, 80),
                'description': random.choice(['clear sky', 'few clouds', 'scattered clouds', 'light rain']),
                'rain_mm': round(random.uniform(0, 5), 1),
                'wind_speed': round(random.uniform(2, 10), 1),
            })
    
    return {'city': city, 'forecasts': forecasts, 'source': 'Mock Data', 'status': 'mock'}
