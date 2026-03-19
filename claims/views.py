from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
from .models import Claim, DisruptionEvent, DisruptionTrigger
from .trigger_engine import process_disruption, setup_default_triggers
from policies.models import Policy
from accounts.models import GigWorkerProfile


@login_required
def claims_list(request):
    """List all claims for the logged-in worker."""
    claims = Claim.objects.filter(worker=request.user).order_by('-created_at')
    
    return render(request, 'claims/claims_list.html', {
        'claims': claims,
        'total_claimed': sum(float(c.payout_amount) for c in claims if c.status in ['approved', 'paid']),
        'pending_claims': claims.filter(status__in=['auto_initiated', 'pending', 'under_review']).count(),
    })


@login_required
def claim_detail(request, claim_id):
    """View claim details."""
    claim = get_object_or_404(Claim, id=claim_id, worker=request.user)
    return render(request, 'claims/claim_detail.html', {'claim': claim})


@login_required
def file_manual_claim(request):
    """File a manual claim (worker-initiated)."""
    try:
        profile = request.user.worker_profile
    except GigWorkerProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('profile_setup')
    
    # Get active policy
    active_policy = Policy.objects.filter(
        worker=request.user,
        status='active',
        week_end__gte=timezone.now().date()
    ).first()
    
    if not active_policy:
        messages.warning(request, 'You need an active policy to file a claim.')
        return redirect('plans_list')
    
    triggers = DisruptionTrigger.objects.filter(is_active=True)
    
    if request.method == 'POST':
        disruption_type = request.POST.get('disruption_type')
        description = request.POST.get('description', '')
        hours_lost = float(request.POST.get('hours_lost', 4))
        
        # Calculate income loss
        daily_income = float(profile.avg_weekly_earnings) / 7
        hours_factor = hours_lost / float(profile.avg_daily_hours)
        income_loss = daily_income * hours_factor
        
        # Create manual claim (pending review)
        claim = Claim.objects.create(
            policy=active_policy,
            worker=request.user,
            disruption_type=disruption_type,
            initiation_type='manual',
            claim_date=timezone.now().date(),
            description=description,
            claim_city=profile.city,
            claim_zone=profile.zone,
            estimated_hours_lost=hours_lost,
            estimated_income_loss=Decimal(str(round(income_loss, 2))),
            status='pending',
        )
        
        messages.success(request, f'📝 Claim {claim.claim_number} submitted for review.')
        return redirect('claim_detail', claim_id=claim.id)
    
    return render(request, 'claims/file_claim.html', {
        'policy': active_policy,
        'triggers': triggers,
        'profile': profile,
    })


@login_required
def disruption_events(request):
    """View recent disruption events."""
    events = DisruptionEvent.objects.all()[:20]
    return render(request, 'claims/events.html', {'events': events})


def simulate_disruption(request):
    """API endpoint to simulate a disruption event (for demo purposes)."""
    if request.method == 'POST':
        trigger_type = request.POST.get('trigger_type', 'heavy_rain')
        city = request.POST.get('city', 'mumbai')
        measured_value = float(request.POST.get('measured_value', 50))
        
        result = process_disruption(
            trigger_type=trigger_type,
            city=city,
            measured_value=measured_value,
            data_source='Simulation',
            estimated_hours_lost=float(request.POST.get('hours_lost', 4)),
        )
        
        if result.get('status') == 'triggered':
            messages.success(request, 
                f'⚡ Disruption triggered! {result["claims_created"]} auto-claims generated. '
                f'Severity: {result["severity"].upper()}')
        elif result.get('status') == 'below_threshold':
            messages.info(request, 
                f'Value {result["measured"]} is below threshold {result["threshold"]}. No claims triggered.')
        else:
            messages.error(request, f'Error: {result.get("error", "Unknown")}')
        
        return redirect('dashboard')
    
    triggers = DisruptionTrigger.objects.filter(is_active=True)
    return render(request, 'claims/simulate.html', {'triggers': triggers})


def init_triggers(request):
    """Initialize default triggers (admin only)."""
    setup_default_triggers()
    messages.success(request, '✅ Default parametric triggers initialized.')
    return redirect('dashboard')
