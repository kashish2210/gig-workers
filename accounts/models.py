from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class User(AbstractUser):
    """Extended user model for GigShield platform."""
    ROLE_CHOICES = [
        ('worker', 'Gig Worker'),
        ('admin', 'Insurance Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='worker')
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    @property
    def is_worker(self):
        return self.role == 'worker'
    
    @property
    def is_admin_user(self):
        return self.role == 'admin'


class GigWorkerProfile(models.Model):
    """Detailed profile for gig delivery workers."""
    
    PLATFORM_CHOICES = [
        ('zomato', 'Zomato'),
        ('swiggy', 'Swiggy'),
        ('zepto', 'Zepto'),
        ('blinkit', 'Blinkit'),
        ('amazon', 'Amazon'),
        ('flipkart', 'Flipkart'),
        ('dunzo', 'Dunzo'),
        ('other', 'Other'),
    ]
    
    DELIVERY_TYPE_CHOICES = [
        ('food', 'Food Delivery'),
        ('grocery', 'Grocery / Q-Commerce'),
        ('ecommerce', 'E-Commerce'),
    ]
    
    VEHICLE_CHOICES = [
        ('bicycle', 'Bicycle'),
        ('motorcycle', 'Motorcycle'),
        ('scooter', 'Scooter'),
        ('ev_scooter', 'Electric Scooter'),
        ('on_foot', 'On Foot'),
    ]
    
    SHIFT_CHOICES = [
        ('morning', 'Morning (6AM - 2PM)'),
        ('afternoon', 'Afternoon (2PM - 10PM)'),
        ('night', 'Night (10PM - 6AM)'),
        ('flexible', 'Flexible / Full Day'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPE_CHOICES)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, default='motorcycle')
    
    # Location
    city = models.CharField(max_length=100)
    zone = models.CharField(max_length=100, help_text="Delivery zone/area")
    pincode = models.CharField(max_length=10)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Work details
    platform_id = models.CharField(max_length=50, help_text="Worker ID on the platform", blank=True)
    avg_weekly_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                               help_text="Average weekly earnings in INR")
    avg_daily_deliveries = models.IntegerField(default=0)
    avg_daily_hours = models.DecimalField(max_digits=4, decimal_places=1, default=8)
    preferred_shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='flexible')
    experience_months = models.IntegerField(default=0, help_text="Months of delivery experience")
    
    # Risk profile (computed by AI)
    risk_score = models.FloatField(default=50.0, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                    help_text="AI-computed risk score (0=low, 100=high)")
    risk_category = models.CharField(max_length=20, default='medium',
                                      choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    
    # KYC
    aadhaar_last_four = models.CharField(max_length=4, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    bank_account = models.CharField(max_length=20, blank=True)
    bank_ifsc = models.CharField(max_length=11, blank=True)
    upi_id = models.CharField(max_length=50, blank=True)
    
    # Flags
    is_verified = models.BooleanField(default=False)
    is_active_worker = models.BooleanField(default=True)
    onboarded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Gig Worker Profile'
        verbose_name_plural = 'Gig Worker Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_platform_display()} ({self.city})"
    
    @property
    def monthly_earning_estimate(self):
        return float(self.avg_weekly_earnings) * 4.33
