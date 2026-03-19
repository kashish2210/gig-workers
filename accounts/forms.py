from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, GigWorkerProfile


class WorkerRegistrationForm(UserCreationForm):
    """Registration form for gig workers."""
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First Name',
            'id': 'id_first_name',
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last Name',
            'id': 'id_last_name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email Address',
            'id': 'id_email',
        })
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Phone Number',
            'id': 'id_phone',
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Username',
                'id': 'id_username',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Password',
            'id': 'id_password1',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm Password',
            'id': 'id_password2',
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'worker'
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
        return user


class WorkerProfileForm(forms.ModelForm):
    """Profile setup form for gig workers (step 2 of onboarding)."""
    
    class Meta:
        model = GigWorkerProfile
        fields = [
            'platform', 'delivery_type', 'vehicle_type',
            'city', 'zone', 'pincode',
            'platform_id', 'avg_weekly_earnings', 'avg_daily_deliveries',
            'avg_daily_hours', 'preferred_shift', 'experience_months',
            'upi_id',
        ]
        widgets = {
            'platform': forms.Select(attrs={'class': 'form-select', 'id': 'id_platform'}),
            'delivery_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_delivery_type'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_vehicle_type'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City (e.g., Mumbai)', 'id': 'id_city'}),
            'zone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Delivery Zone (e.g., Andheri West)', 'id': 'id_zone'}),
            'pincode': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Pincode', 'id': 'id_pincode'}),
            'platform_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Platform Worker ID', 'id': 'id_platform_id'}),
            'avg_weekly_earnings': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Avg Weekly Earnings (₹)', 'id': 'id_avg_weekly_earnings'}),
            'avg_daily_deliveries': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Avg Daily Deliveries', 'id': 'id_avg_daily_deliveries'}),
            'avg_daily_hours': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Avg Daily Hours', 'step': '0.5', 'id': 'id_avg_daily_hours'}),
            'preferred_shift': forms.Select(attrs={'class': 'form-select', 'id': 'id_preferred_shift'}),
            'experience_months': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Experience (months)', 'id': 'id_experience_months'}),
            'upi_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'UPI ID (e.g., name@upi)', 'id': 'id_upi_id'}),
        }


class WorkerLoginForm(AuthenticationForm):
    """Custom login form."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username or Email',
            'id': 'id_login_username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'id': 'id_login_password',
        })
    )
