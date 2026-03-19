from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import InsurancePlan, Policy
from .premium_engine import calculate_premium, save_premium_calculation
from accounts.models import GigWorkerProfile


@login_required
def plans_list(request):
    """Show available insurance plans with dynamic premium preview."""
    plans = InsurancePlan.objects.filter(is_active=True)
    
    try:
        profile = request.user.worker_profile
    except GigWorkerProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('profile_setup')
    
    # Calculate dynamic premiums for each plan
    plan_data = []
    for plan in plans:
        calc = calculate_premium(plan, profile)
        plan_data.append({
            'plan': plan,
            'calc': calc,
        })
    
    return render(request, 'policies/plans.html', {
        'plan_data': plan_data,
        'profile': profile,
    })


@login_required
def purchase_policy(request, plan_id):
    """Purchase a weekly policy."""
    plan = get_object_or_404(InsurancePlan, id=plan_id, is_active=True)
    
    try:
        profile = request.user.worker_profile
    except GigWorkerProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('profile_setup')
    
    # Check for existing active policy
    active_policy = Policy.objects.filter(
        worker=request.user,
        status='active',
        week_end__gte=timezone.now().date()
    ).first()
    
    if active_policy:
        messages.warning(request, 'You already have an active policy for this week.')
        return redirect('my_policies')
    
    # Calculate premium
    calc = calculate_premium(plan, profile)
    
    if request.method == 'POST':
        # Create the policy
        today = timezone.now().date()
        # Start from next Monday if today is not Monday
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            week_start = today
        else:
            week_start = today  # Start immediately for demo purposes
        week_end = week_start + timedelta(days=6)
        
        policy = Policy.objects.create(
            worker=request.user,
            plan=plan,
            week_start=week_start,
            week_end=week_end,
            base_premium=Decimal(str(calc['base_premium'])),
            risk_adjustment=Decimal(str(calc['risk_adjustment'])),
            final_premium=Decimal(str(calc['final_premium'])),
            coverage_amount=Decimal(str(calc['coverage_amount'])),
            status='active',
            risk_score_at_creation=profile.risk_score,
            city_at_creation=profile.city,
            zone_at_creation=profile.zone,
        )
        
        # Save premium calculation audit
        save_premium_calculation(policy, calc)
        
        messages.success(request, f'🛡️ Policy {policy.policy_number} activated! You\'re protected for this week.')
        return redirect('policy_detail', policy_id=policy.id)
    
    return render(request, 'policies/purchase.html', {
        'plan': plan,
        'calc': calc,
        'profile': profile,
    })


@login_required
def my_policies(request):
    """List all policies for the current worker."""
    policies = Policy.objects.filter(worker=request.user).order_by('-created_at')
    
    active_policy = policies.filter(
        status='active',
        week_end__gte=timezone.now().date()
    ).first()
    
    return render(request, 'policies/my_policies.html', {
        'policies': policies,
        'active_policy': active_policy,
    })


@login_required
def policy_detail(request, policy_id):
    """View policy details including premium breakdown."""
    policy = get_object_or_404(Policy, id=policy_id, worker=request.user)
    premium_calcs = policy.premium_calculations.order_by('-created_at')
    
    return render(request, 'policies/policy_detail.html', {
        'policy': policy,
        'premium_calcs': premium_calcs,
    })
