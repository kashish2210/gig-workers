from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from datetime import timedelta
from accounts.models import GigWorkerProfile
from policies.models import Policy, InsurancePlan
from claims.models import Claim, DisruptionEvent, DisruptionTrigger
from external_apis.weather import get_current_weather
from external_apis.air_quality import get_current_aqi


@login_required
def dashboard(request):
    """Main dashboard — different views for workers vs admins."""
    if request.user.role == 'admin':
        return admin_dashboard(request)
    return worker_dashboard(request)


@login_required
def worker_dashboard(request):
    """Worker dashboard showing coverage, claims, and weather."""
    try:
        profile = request.user.worker_profile
    except GigWorkerProfile.DoesNotExist:
        return redirect('profile_setup')
    
    today = timezone.now().date()
    
    # Active policy
    active_policy = Policy.objects.filter(
        worker=request.user,
        status='active',
        week_end__gte=today
    ).first()
    
    # Claims summary
    claims = Claim.objects.filter(worker=request.user)
    recent_claims = claims.order_by('-created_at')[:5]
    total_protected = claims.filter(
        status__in=['approved', 'paid']
    ).aggregate(total=Sum('payout_amount'))['total'] or 0
    
    # Weather data for worker's city
    weather = get_current_weather(profile.city)
    aqi = get_current_aqi(profile.city)
    
    # Recent disruption events in worker's city
    recent_events = DisruptionEvent.objects.filter(
        city__iexact=profile.city
    ).order_by('-event_start')[:5]
    
    # Stats
    total_policies = Policy.objects.filter(worker=request.user).count()
    total_claims_count = claims.count()
    approved_claims = claims.filter(status__in=['approved', 'paid']).count()
    
    # Weekly earnings protection calculation
    weekly_protection = 0
    if active_policy:
        weekly_protection = float(active_policy.coverage_amount)
    
    context = {
        'profile': profile,
        'active_policy': active_policy,
        'recent_claims': recent_claims,
        'total_protected': total_protected,
        'weather': weather,
        'aqi': aqi,
        'recent_events': recent_events,
        'total_policies': total_policies,
        'total_claims_count': total_claims_count,
        'approved_claims': approved_claims,
        'weekly_protection': weekly_protection,
    }
    
    return render(request, 'dashboard/worker_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Admin/Insurer dashboard with analytics."""
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Overall stats
    total_workers = GigWorkerProfile.objects.count()
    active_policies = Policy.objects.filter(status='active', week_end__gte=today).count()
    total_claims = Claim.objects.count()
    total_payouts = Claim.objects.filter(
        status__in=['approved', 'paid']
    ).aggregate(total=Sum('payout_amount'))['total'] or 0
    total_premiums = Policy.objects.aggregate(total=Sum('final_premium'))['total'] or 0
    
    # Loss ratio
    loss_ratio = (float(total_payouts) / float(total_premiums) * 100) if total_premiums > 0 else 0
    
    # Claims by type
    claims_by_type = Claim.objects.values('disruption_type').annotate(
        count=Count('id'),
        total_amount=Sum('payout_amount')
    ).order_by('-count')
    
    # Recent events
    recent_events = DisruptionEvent.objects.order_by('-event_start')[:10]
    
    # Claims by status
    claims_by_status = Claim.objects.values('status').annotate(count=Count('id'))
    
    # Top cities by claims
    top_cities = Claim.objects.values('claim_city').annotate(
        count=Count('id'),
        total_payout=Sum('payout_amount')
    ).order_by('-count')[:10]
    
    # Risk distribution
    risk_dist = GigWorkerProfile.objects.values('risk_category').annotate(count=Count('id'))
    
    # Recently flagged claims
    flagged_claims = Claim.objects.filter(status='flagged').order_by('-created_at')[:5]
    
    # Monthly trend (claims count per day for last 30 days)
    claims_trend = []
    for i in range(30):
        day = today - timedelta(days=29-i)
        count = Claim.objects.filter(claim_date=day).count()
        claims_trend.append({'date': day.strftime('%m/%d'), 'count': count})
    
    context = {
        'total_workers': total_workers,
        'active_policies': active_policies,
        'total_claims': total_claims,
        'total_payouts': total_payouts,
        'total_premiums': total_premiums,
        'loss_ratio': round(loss_ratio, 1),
        'claims_by_type': list(claims_by_type),
        'recent_events': recent_events,
        'claims_by_status': list(claims_by_status),
        'top_cities': list(top_cities),
        'risk_dist': list(risk_dist),
        'flagged_claims': flagged_claims,
        'claims_trend': claims_trend,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def api_dashboard_stats(request):
    """JSON endpoint for dashboard chart data."""
    from django.http import JsonResponse
    
    today = timezone.now().date()
    
    # Claims trend (last 14 days)
    claims_trend = []
    for i in range(14):
        day = today - timedelta(days=13-i)
        count = Claim.objects.filter(claim_date=day).count()
        amount = Claim.objects.filter(
            claim_date=day, status__in=['approved', 'paid']
        ).aggregate(total=Sum('payout_amount'))['total'] or 0
        claims_trend.append({
            'date': day.strftime('%b %d'),
            'count': count,
            'amount': float(amount),
        })
    
    # Claims by disruption type
    by_type = list(Claim.objects.values('disruption_type').annotate(
        count=Count('id')
    ).order_by('-count'))
    
    return JsonResponse({
        'claims_trend': claims_trend,
        'claims_by_type': by_type,
    })
