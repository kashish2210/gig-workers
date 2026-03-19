from django.urls import path
from . import views

urlpatterns = [
    path('', views.claims_list, name='claims_list'),
    path('<uuid:claim_id>/', views.claim_detail, name='claim_detail'),
    path('file/', views.file_manual_claim, name='file_claim'),
    path('events/', views.disruption_events, name='disruption_events'),
    path('simulate/', views.simulate_disruption, name='simulate_disruption'),
    path('init-triggers/', views.init_triggers, name='init_triggers'),
]
