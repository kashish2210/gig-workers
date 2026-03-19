"""
Dynamic Premium Calculation Engine for GigShield.
Uses rule-based logic (Phase 1) with ML enhancement planned for Phase 2.
"""

from decimal import Decimal
from datetime import datetime
from .models import PremiumCalculation


# City-level risk multipliers (based on historical weather, pollution, flooding data)
CITY_RISK_FACTORS = {
    'mumbai': 1.30,      # Heavy monsoon flooding
    'chennai': 1.25,      # Cyclones, flooding
    'kolkata': 1.20,      # Monsoon + pollution
    'delhi': 1.25,        # Extreme heat + severe pollution
    'bangalore': 1.05,    # Moderate weather
    'hyderabad': 1.10,    # Moderate
    'pune': 1.08,
    'ahmedabad': 1.15,    # Extreme heat
    'jaipur': 1.12,       # Heat
    'lucknow': 1.15,      # Pollution + heat
    'noida': 1.20,        # Same as Delhi NCR
    'gurgaon': 1.20,      # Same as Delhi NCR
}

# Season risk multipliers
SEASON_FACTORS = {
    'monsoon': 1.25,      # June-September
    'winter': 0.90,       # November-February (mild weather mostly)
    'summer': 1.15,       # March-May (extreme heat)
    'post_monsoon': 1.05, # October
}

# Vehicle vulnerability to weather
VEHICLE_FACTORS = {
    'bicycle': 1.20,      # Most vulnerable
    'on_foot': 1.25,      # Most vulnerable
    'scooter': 1.05,
    'motorcycle': 1.00,   # Base
    'ev_scooter': 1.10,   # Battery issues in extreme temps
}

# Shift risk
SHIFT_FACTORS = {
    'morning': 0.95,      # Safest
    'afternoon': 1.05,    # Peak heat
    'night': 1.15,        # Visibility, safety
    'flexible': 1.00,     # Average
}


def get_current_season():
    """Determine current season based on Indian weather patterns."""
    month = datetime.now().month
    if month in [6, 7, 8, 9]:
        return 'monsoon'
    elif month in [11, 12, 1, 2]:
        return 'winter'
    elif month in [3, 4, 5]:
        return 'summer'
    else:
        return 'post_monsoon'


def calculate_premium(plan, worker_profile, weather_data=None, aqi_data=None):
    """
    Calculate dynamic weekly premium based on multiple risk factors.
    
    Returns: dict with premium details and factor breakdown
    """
    base = float(plan.base_weekly_premium)
    
    # 1. City Factor
    city_lower = worker_profile.city.lower().strip()
    city_factor = CITY_RISK_FACTORS.get(city_lower, 1.0)
    
    # 2. Season Factor
    season = get_current_season()
    season_factor = SEASON_FACTORS.get(season, 1.0)
    
    # 3. Vehicle Factor
    vehicle_factor = VEHICLE_FACTORS.get(worker_profile.vehicle_type, 1.0)
    
    # 4. Shift Factor
    shift_factor = SHIFT_FACTORS.get(worker_profile.preferred_shift, 1.0)
    
    # 5. Experience Factor (more experience = slight discount)
    exp = worker_profile.experience_months
    if exp >= 24:
        experience_factor = 0.90
    elif exp >= 12:
        experience_factor = 0.95
    elif exp >= 6:
        experience_factor = 1.0
    else:
        experience_factor = 1.05  # New workers slightly higher
    
    # 6. Historical claims factor (placeholder - will use actual claims data in Phase 2)
    historical_claims_factor = 1.0
    
    # Count past claims from the worker
    from claims.models import Claim
    past_claims = Claim.objects.filter(
        policy__worker=worker_profile.user,
        status='approved'
    ).count()
    
    if past_claims == 0:
        historical_claims_factor = 0.92  # No-claim discount
    elif past_claims <= 2:
        historical_claims_factor = 1.0
    elif past_claims <= 5:
        historical_claims_factor = 1.10
    else:
        historical_claims_factor = 1.20
    
    # 7. Weather forecast factor (if live data available)
    weather_forecast_factor = 1.0
    if weather_data:
        # If bad weather expected, premium goes up (higher risk of claims)
        if weather_data.get('rain_probability', 0) > 70:
            weather_forecast_factor = 1.15
        elif weather_data.get('temp_celsius', 30) > 42:
            weather_forecast_factor = 1.10
    
    # 8. AQI forecast factor
    aqi_forecast_factor = 1.0
    if aqi_data:
        aqi = aqi_data.get('aqi', 0)
        if aqi > 300:
            aqi_forecast_factor = 1.20
        elif aqi > 200:
            aqi_forecast_factor = 1.10
    
    # 9. Zone-specific factor (placeholder for hyper-local risk)
    zone_factor = 1.0
    flood_prone_zones = ['andheri', 'sion', 'dadar', 'kurla', 'matunga', 'wadala', 'parel']
    if worker_profile.zone.lower().strip() in flood_prone_zones:
        zone_factor = 1.15
    
    # Calculate final premium
    combined_factor = (
        city_factor * season_factor * vehicle_factor * shift_factor *
        experience_factor * historical_claims_factor * weather_forecast_factor *
        aqi_forecast_factor * zone_factor
    )
    
    final_premium = round(base * combined_factor, 2)
    
    # Clamp to reasonable range
    min_premium = base * 0.70  # 30% max discount
    max_premium = base * 2.0   # 100% max surcharge
    final_premium = max(min_premium, min(max_premium, final_premium))
    
    risk_adjustment = round(final_premium - base, 2)
    
    # Coverage amount = worker's avg weekly earnings * coverage percentage
    coverage_pct = plan.daily_income_coverage_pct / 100
    weekly_coverage = float(worker_profile.avg_weekly_earnings) * coverage_pct
    coverage_amount = min(weekly_coverage, float(plan.max_weekly_coverage))
    
    return {
        'base_premium': base,
        'final_premium': final_premium,
        'risk_adjustment': risk_adjustment,
        'coverage_amount': round(coverage_amount, 2),
        'factors': {
            'city_factor': city_factor,
            'zone_factor': zone_factor,
            'season_factor': season_factor,
            'vehicle_factor': vehicle_factor,
            'shift_factor': shift_factor,
            'experience_factor': experience_factor,
            'historical_claims_factor': historical_claims_factor,
            'weather_forecast_factor': weather_forecast_factor,
            'aqi_forecast_factor': aqi_forecast_factor,
        },
        'season': season,
        'combined_multiplier': round(combined_factor, 4),
        'model_version': 'v1.0-rule-based',
    }


def save_premium_calculation(policy, calc_result):
    """Save premium calculation as audit trail."""
    factors = calc_result['factors']
    PremiumCalculation.objects.create(
        policy=policy,
        base_amount=Decimal(str(calc_result['base_premium'])),
        city_factor=factors['city_factor'],
        zone_factor=factors['zone_factor'],
        season_factor=factors['season_factor'],
        historical_claims_factor=factors['historical_claims_factor'],
        shift_factor=factors['shift_factor'],
        vehicle_factor=factors['vehicle_factor'],
        experience_factor=factors['experience_factor'],
        weather_forecast_factor=factors['weather_forecast_factor'],
        aqi_forecast_factor=factors['aqi_forecast_factor'],
        final_premium=Decimal(str(calc_result['final_premium'])),
        model_version=calc_result['model_version'],
        calculation_details=calc_result,
    )
