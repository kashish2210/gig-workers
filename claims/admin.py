from django.contrib import admin
from .models import DisruptionTrigger, DisruptionEvent, Claim


@admin.register(DisruptionTrigger)
class DisruptionTriggerAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'threshold_value', 'threshold_unit', 'payout_percentage', 'is_active']
    list_filter = ['trigger_type', 'is_active']


@admin.register(DisruptionEvent)
class DisruptionEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'city', 'severity', 'measured_value', 'auto_claims_generated', 'event_start']
    list_filter = ['severity', 'city']


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['claim_number', 'worker', 'disruption_type', 'initiation_type', 'payout_amount', 'status', 'claim_date']
    list_filter = ['status', 'disruption_type', 'initiation_type']
    search_fields = ['claim_number', 'worker__username']
