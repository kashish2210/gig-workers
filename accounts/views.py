from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import WorkerRegistrationForm, WorkerProfileForm, WorkerLoginForm
from .models import GigWorkerProfile


def landing_page(request):
    """Landing page — the public homepage."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing/index.html')


def register_view(request):
    """Step 1: Account registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = WorkerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '🎉 Account created! Now set up your delivery profile.')
            return redirect('profile_setup')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = WorkerRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_setup_view(request):
    """Step 2: Worker profile setup (onboarding)."""
    # Check if profile already exists
    try:
        profile = request.user.worker_profile
        form = WorkerProfileForm(request.POST or None, instance=profile)
    except GigWorkerProfile.DoesNotExist:
        form = WorkerProfileForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        profile.onboarded_at = timezone.now()
        # Calculate initial risk score (basic version)
        profile.risk_score = _calculate_initial_risk(profile)
        profile.risk_category = _get_risk_category(profile.risk_score)
        profile.save()
        messages.success(request, '✅ Profile set up! Welcome to GigShield.')
        return redirect('dashboard')
    
    return render(request, 'accounts/profile_setup.html', {'form': form})


def login_view(request):
    """Login page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = WorkerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}! 👋')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = WorkerLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Logout and redirect to landing."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing')


@login_required
def profile_view(request):
    """View/edit profile."""
    try:
        profile = request.user.worker_profile
    except GigWorkerProfile.DoesNotExist:
        return redirect('profile_setup')
    
    if request.method == 'POST':
        form = WorkerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.risk_score = _calculate_initial_risk(profile)
            profile.risk_category = _get_risk_category(profile.risk_score)
            profile.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = WorkerProfileForm(instance=profile)
    
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


def _calculate_initial_risk(profile):
    """Basic risk scoring (will be enhanced with ML in Phase 2)."""
    score = 50.0  # Base score
    
    # City risk factors (metros have more disruptions)
    high_risk_cities = ['mumbai', 'chennai', 'kolkata', 'delhi', 'bangalore', 'hyderabad']
    if profile.city.lower() in high_risk_cities:
        score += 15
    
    # Night shift is riskier
    if profile.preferred_shift == 'night':
        score += 10
    elif profile.preferred_shift == 'flexible':
        score += 5
    
    # Vehicle type matters
    if profile.vehicle_type in ['bicycle', 'on_foot']:
        score += 10  # More affected by weather
    elif profile.vehicle_type == 'ev_scooter':
        score += 5  # Battery affected by extreme heat
    
    # Experience reduces risk
    if profile.experience_months > 24:
        score -= 10
    elif profile.experience_months > 12:
        score -= 5
    
    # Higher earnings = more to lose
    if float(profile.avg_weekly_earnings) > 5000:
        score += 5
    
    return max(0, min(100, score))


def _get_risk_category(score):
    if score < 35:
        return 'low'
    elif score < 65:
        return 'medium'
    else:
        return 'high'
