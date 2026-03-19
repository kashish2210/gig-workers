"""
Parametric Trigger Engine for GigShield.
Monitors real-time conditions and auto-initiates claims when thresholds are breached.
"""

from decimal import Decimal
from django.utils import timezone
from .models import DisruptionTrigger, DisruptionEvent, Claim
from policies.models import Policy


# Default triggers for food delivery persona
DEFAULT_TRIGGERS = [
    {
        'trigger_type': 'heavy_rain',
        'name': 'Heavy Rainfall Alert',
        'description': 'Rainfall exceeds 30mm/hr making deliveries unsafe and roads impassable.',
        'threshold_value': 30.0,
        'threshold_unit': 'mm/hr',
        'threshold_comparison': 'gte',
        'payout_percentage': 70,
        'cities_affected': ['mumbai', 'chennai', 'kolkata', 'delhi', 'bangalore', 'hyderabad', 'pune'],
    },
    {
        'trigger_type': 'extreme_heat',
        'name': 'Extreme Heat Warning',
        'description': 'Temperature exceeds 45°C making outdoor work dangerous.',
        'threshold_value': 45.0,
        'threshold_unit': '°C',
        'threshold_comparison': 'gte',
        'payout_percentage': 60,
        'cities_affected': ['delhi', 'jaipur', 'ahmedabad', 'lucknow', 'nagpur', 'noida', 'gurgaon'],
    },
    {
        'trigger_type': 'severe_pollution',
        'name': 'Severe Air Quality Alert',
        'description': 'AQI exceeds 400 (Severe+ category) with health advisory against outdoor activity.',
        'threshold_value': 400.0,
        'threshold_unit': 'AQI Index',
        'threshold_comparison': 'gte',
        'payout_percentage': 60,
        'cities_affected': ['delhi', 'noida', 'gurgaon', 'lucknow', 'kanpur', 'patna'],
    },
    {
        'trigger_type': 'flooding',
        'name': 'Flood / Waterlogging Alert',
        'description': 'Water levels exceed safe limits, roads submerged, delivery zones inaccessible.',
        'threshold_value': 200.0,
        'threshold_unit': 'mm (cumulative 24hr)',
        'threshold_comparison': 'gte',
        'payout_percentage': 80,
        'cities_affected': ['mumbai', 'chennai', 'kolkata', 'hyderabad', 'bangalore'],
    },
    {
        'trigger_type': 'cyclone',
        'name': 'Cyclone Warning',
        'description': 'IMD cyclone warning issued for the region, all outdoor activity suspended.',
        'threshold_value': 1.0,
        'threshold_unit': 'Warning Level (1-5)',
        'threshold_comparison': 'gte',
        'payout_percentage': 100,
        'cities_affected': ['chennai', 'mumbai', 'kolkata', 'visakhapatnam', 'bhubaneswar'],
    },
]


def setup_default_triggers():
    """Initialize default parametric triggers in the database."""
    for trigger_data in DEFAULT_TRIGGERS:
        DisruptionTrigger.objects.get_or_create(
            trigger_type=trigger_data['trigger_type'],
            defaults=trigger_data,
        )
    return DisruptionTrigger.objects.filter(is_active=True)


def check_trigger(trigger, current_value):
    """Check if a trigger's threshold is breached."""
    threshold = trigger.threshold_value
    comp = trigger.threshold_comparison
    
    if comp == 'gt':
        return current_value > threshold
    elif comp == 'lt':
        return current_value < threshold
    elif comp == 'gte':
        return current_value >= threshold
    elif comp == 'lte':
        return current_value <= threshold
    elif comp == 'eq':
        return current_value == threshold
    return False


def process_disruption(trigger_type, city, measured_value, data_source='OpenWeatherMap',
                        zones_affected=None, estimated_hours_lost=4):
    """
    Process a detected disruption:
    1. Create a DisruptionEvent
    2. Find all affected active policies
    3. Auto-initiate claims
    """
    # Find the matching trigger
    try:
        trigger = DisruptionTrigger.objects.get(trigger_type=trigger_type, is_active=True)
    except DisruptionTrigger.DoesNotExist:
        return {'error': f'No active trigger for type: {trigger_type}'}
    
    # Check if threshold is breached
    if not check_trigger(trigger, measured_value):
        return {'status': 'below_threshold', 'measured': measured_value, 'threshold': trigger.threshold_value}
    
    # Determine severity
    ratio = measured_value / trigger.threshold_value if trigger.threshold_value > 0 else 1
    if ratio >= 2.0:
        severity = 'extreme'
    elif ratio >= 1.5:
        severity = 'severe'
    elif ratio >= 1.2:
        severity = 'high'
    elif ratio >= 1.0:
        severity = 'moderate'
    else:
        severity = 'low'
    
    # Create disruption event
    event = DisruptionEvent.objects.create(
        trigger=trigger,
        title=f"{trigger.name} in {city}",
        description=f"Measured {measured_value} {trigger.threshold_unit} (threshold: {trigger.threshold_value}). "
                     f"Source: {data_source}",
        severity=severity,
        city=city,
        zones_affected=zones_affected or [],
        measured_value=measured_value,
        data_source=data_source,
        event_start=timezone.now(),
        estimated_hours_lost=estimated_hours_lost,
    )
    
    # Find all active policies in the affected city
    active_policies = Policy.objects.filter(
        status='active',
        city_at_creation__iexact=city,
        week_start__lte=timezone.now().date(),
        week_end__gte=timezone.now().date(),
    )
    
    # Auto-initiate claims
    claims_created = []
    for policy in active_policies:
        # Check if plan covers this disruption type
        if trigger_type in ['heavy_rain', 'extreme_heat', 'flooding', 'cyclone'] and not policy.plan.covers_weather:
            continue
        if trigger_type == 'severe_pollution' and not policy.plan.covers_pollution:
            continue
        if trigger_type == 'civil_unrest' and not policy.plan.covers_civil_unrest:
            continue
        
        # Check if worker hasn't already claimed today
        today_claim = Claim.objects.filter(
            policy=policy,
            claim_date=timezone.now().date(),
        ).exists()
        
        if today_claim:
            continue
        
        # Check claim limit for the week
        if not policy.is_claimable:
            continue
        
        # Calculate payout
        try:
            profile = policy.worker.worker_profile
            daily_income = float(profile.avg_weekly_earnings) / 7
            hours_factor = estimated_hours_lost / float(profile.avg_daily_hours)
            income_loss = daily_income * hours_factor
            payout = income_loss * (trigger.payout_percentage / 100)
            
            # Cap at remaining coverage
            payout = min(payout, policy.remaining_coverage)
        except Exception:
            payout = 0
            income_loss = 0
        
        # Create auto-claim
        claim = Claim.objects.create(
            policy=policy,
            worker=policy.worker,
            disruption_event=event,
            disruption_type=trigger_type,
            initiation_type='automatic',
            claim_date=timezone.now().date(),
            description=f"Auto-triggered: {event.title}. {event.description}",
            claim_city=city,
            estimated_hours_lost=estimated_hours_lost,
            estimated_income_loss=Decimal(str(round(income_loss, 2))),
            approved_amount=Decimal(str(round(payout, 2))),
            payout_amount=Decimal(str(round(payout, 2))),
            status='approved',
            weather_data_snapshot={'measured_value': measured_value, 'source': data_source},
        )
        
        # Update policy claim count
        policy.claims_made += 1
        policy.total_claimed += Decimal(str(round(payout, 2)))
        policy.save()
        
        claims_created.append(claim)
    
    # Update event with claims count
    event.auto_claims_generated = len(claims_created)
    event.save()
    
    return {
        'status': 'triggered',
        'event': event,
        'claims_created': len(claims_created),
        'severity': severity,
    }
