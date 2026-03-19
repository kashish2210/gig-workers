from django.db import models
from accounts.models import User, GigWorkerProfile
import uuid


class InsurancePlan(models.Model):
    """Available insurance plans/tiers."""
    
    TIER_CHOICES = [
        ('basic', 'Basic Shield'),
        ('standard', 'Standard Shield'),
        ('premium', 'Premium Shield'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    description = models.TextField()
    
    # Coverage details
    base_weekly_premium = models.DecimalField(max_digits=8, decimal_places=2)
    max_weekly_coverage = models.DecimalField(max_digits=10, decimal_places=2, 
                                               help_text="Max payout per week in INR")
    daily_income_coverage_pct = models.IntegerField(default=70,
                                                      help_text="% of daily income covered")
    max_claim_days_per_week = models.IntegerField(default=3,
                                                    help_text="Max claimable days per week")
    
    # Covered disruptions
    covers_weather = models.BooleanField(default=True)
    covers_pollution = models.BooleanField(default=True)
    covers_civil_unrest = models.BooleanField(default=False)
    covers_platform_outage = models.BooleanField(default=False)
    
    # Waiting period (hours after trigger before claim is approved)
    waiting_period_hours = models.IntegerField(default=2)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['base_weekly_premium']
    
    def __str__(self):
        return f"{self.name} (₹{self.base_weekly_premium}/week)"


class Policy(models.Model):
    """Individual insurance policy for a gig worker (weekly cycle)."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
        ('lapsed', 'Lapsed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_number = models.CharField(max_length=20, unique=True)
    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='policies')
    plan = models.ForeignKey(InsurancePlan, on_delete=models.PROTECT, related_name='policies')
    
    # Weekly cycle
    week_start = models.DateField()
    week_end = models.DateField()
    
    # Premium (dynamically calculated)
    base_premium = models.DecimalField(max_digits=8, decimal_places=2)
    risk_adjustment = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    final_premium = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Coverage
    coverage_amount = models.DecimalField(max_digits=10, decimal_places=2)
    claims_made = models.IntegerField(default=0)
    total_claimed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    auto_renew = models.BooleanField(default=True)
    
    # Risk snapshot at policy creation
    risk_score_at_creation = models.FloatField(default=50.0)
    city_at_creation = models.CharField(max_length=100, blank=True)
    zone_at_creation = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Policies'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Policy {self.policy_number} - {self.worker.get_full_name()}"
    
    @property
    def is_claimable(self):
        return self.status == 'active' and self.claims_made < self.plan.max_claim_days_per_week
    
    @property
    def remaining_coverage(self):
        return float(self.coverage_amount) - float(self.total_claimed)
    
    def save(self, *args, **kwargs):
        if not self.policy_number:
            self.policy_number = f"GS-{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)


class PremiumCalculation(models.Model):
    """Audit trail for premium calculations showing AI factors."""
    
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='premium_calculations')
    
    # Factors
    base_amount = models.DecimalField(max_digits=8, decimal_places=2)
    city_factor = models.FloatField(default=1.0)
    zone_factor = models.FloatField(default=1.0)
    season_factor = models.FloatField(default=1.0)
    historical_claims_factor = models.FloatField(default=1.0)
    shift_factor = models.FloatField(default=1.0)
    vehicle_factor = models.FloatField(default=1.0)
    experience_factor = models.FloatField(default=1.0)
    weather_forecast_factor = models.FloatField(default=1.0)
    aqi_forecast_factor = models.FloatField(default=1.0)
    
    final_premium = models.DecimalField(max_digits=8, decimal_places=2)
    
    # ML model info
    model_version = models.CharField(max_length=50, default='v1.0-rule-based')
    calculation_details = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Premium calc for {self.policy.policy_number}: ₹{self.final_premium}"
