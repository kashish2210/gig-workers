from django.contrib import admin
from .models import InsurancePlan, Policy, PremiumCalculation


@admin.register(InsurancePlan)
class InsurancePlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'base_weekly_premium', 'max_weekly_coverage', 'daily_income_coverage_pct', 'is_active']
    list_filter = ['tier', 'is_active']


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['policy_number', 'worker', 'plan', 'week_start', 'week_end', 'final_premium', 'coverage_amount', 'status']
    list_filter = ['status', 'plan']
    search_fields = ['policy_number', 'worker__username']


@admin.register(PremiumCalculation)
class PremiumCalculationAdmin(admin.ModelAdmin):
    list_display = ['policy', 'base_amount', 'final_premium', 'model_version', 'created_at']
