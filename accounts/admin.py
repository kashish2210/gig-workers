from django.contrib import admin
from .models import User, GigWorkerProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(GigWorkerProfile)
class GigWorkerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'delivery_type', 'city', 'zone', 'risk_score', 'risk_category', 'is_verified']
    list_filter = ['platform', 'delivery_type', 'city', 'risk_category', 'is_verified']
    search_fields = ['user__username', 'user__first_name', 'city', 'zone']
