from django.db import models
from accounts.models import User
from policies.models import Policy
import uuid


class DisruptionTrigger(models.Model):
    """Defines parametric triggers that auto-initiate claims."""
    
    TRIGGER_TYPES = [
        ('heavy_rain', 'Heavy Rainfall'),
        ('extreme_heat', 'Extreme Heat'),
        ('severe_pollution', 'Severe Air Pollution (AQI)'),
        ('flooding', 'Flooding / Waterlogging'),
        ('cyclone', 'Cyclone Warning'),
        ('civil_unrest', 'Civil Unrest / Curfew'),
        ('platform_outage', 'Platform Outage'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Threshold values for auto-triggering
    threshold_value = models.FloatField(help_text="Numeric threshold to trigger")
    threshold_unit = models.CharField(max_length=30, help_text="e.g., mm/hr, °C, AQI index")
    threshold_comparison = models.CharField(max_length=5, 
                                             choices=[('gt', '>'), ('lt', '<'), ('gte', '>='), ('lte', '<='), ('eq', '=')],
                                             default='gte')
    
    # Payout percentage of daily income
    payout_percentage = models.IntegerField(default=70, help_text="% of daily income to pay out")
    
    # Affected area
    cities_affected = models.JSONField(default=list, help_text="List of affected city names")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['trigger_type']
    
    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"


class DisruptionEvent(models.Model):
    """Records actual disruption events detected by the system."""
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('severe', 'Severe'),
        ('extreme', 'Extreme'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trigger = models.ForeignKey(DisruptionTrigger, on_delete=models.CASCADE, related_name='events')
    
    # Event details
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    
    # Location
    city = models.CharField(max_length=100)
    zones_affected = models.JSONField(default=list)
    
    # Measured values
    measured_value = models.FloatField(help_text="Actual measured value that triggered this")
    data_source = models.CharField(max_length=100, help_text="API source of the data")
    
    # Duration
    event_start = models.DateTimeField()
    event_end = models.DateTimeField(null=True, blank=True)
    estimated_hours_lost = models.FloatField(default=4, help_text="Estimated working hours lost")
    
    # Auto-claim tracking
    auto_claims_generated = models.IntegerField(default=0)
    
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-event_start']
    
    def __str__(self):
        return f"{self.title} - {self.city} ({self.severity})"


class Claim(models.Model):
    """Insurance claims filed by workers or auto-triggered by the system."""
    
    STATUS_CHOICES = [
        ('auto_initiated', 'Auto-Initiated'),
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid Out'),
        ('flagged', 'Flagged for Fraud'),
    ]
    
    INITIATION_CHOICES = [
        ('automatic', 'Automatic (Parametric Trigger)'),
        ('manual', 'Manual (Worker Submitted)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim_number = models.CharField(max_length=20, unique=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='claims')
    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    
    # Disruption link
    disruption_event = models.ForeignKey(DisruptionEvent, on_delete=models.SET_NULL, 
                                          null=True, blank=True, related_name='claims')
    disruption_type = models.CharField(max_length=30, choices=DisruptionTrigger.TRIGGER_TYPES)
    
    # Claim details
    initiation_type = models.CharField(max_length=20, choices=INITIATION_CHOICES, default='automatic')
    claim_date = models.DateField()
    description = models.TextField(blank=True)
    
    # Location at time of claim
    claim_city = models.CharField(max_length=100)
    claim_zone = models.CharField(max_length=100, blank=True)
    claim_latitude = models.FloatField(null=True, blank=True)
    claim_longitude = models.FloatField(null=True, blank=True)
    
    # Income loss
    estimated_hours_lost = models.FloatField(default=0)
    estimated_income_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payout
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payout_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Fraud detection
    fraud_score = models.FloatField(default=0, help_text="AI fraud score 0-100")
    fraud_flags = models.JSONField(default=list)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='auto_initiated')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='reviewed_claims')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Evidence
    weather_data_snapshot = models.JSONField(default=dict)
    aqi_data_snapshot = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Claim {self.claim_number} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.claim_number:
            self.claim_number = f"CLM-{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)
