from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.plans_list, name='plans_list'),
    path('purchase/<uuid:plan_id>/', views.purchase_policy, name='purchase_policy'),
    path('my-policies/', views.my_policies, name='my_policies'),
    path('policy/<uuid:policy_id>/', views.policy_detail, name='policy_detail'),
]
