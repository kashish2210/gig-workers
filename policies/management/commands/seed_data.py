"""
Seed the database with insurance plans and parametric triggers.
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from policies.models import InsurancePlan
from claims.trigger_engine import setup_default_triggers
from accounts.models import User


class Command(BaseCommand):
    help = 'Seed the database with insurance plans, triggers, and admin user'
    
    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding GigShield database...\n')
        
        # Create Insurance Plans
        plans_data = [
            {
                'tier': 'basic',
                'name': 'Basic Shield',
                'description': 'Essential coverage for weather disruptions. Perfect for part-time delivery workers.',
                'base_weekly_premium': 49.00,
                'max_weekly_coverage': 2000.00,
                'daily_income_coverage_pct': 50,
                'max_claim_days_per_week': 2,
                'covers_weather': True,
                'covers_pollution': False,
                'covers_civil_unrest': False,
                'covers_platform_outage': False,
                'waiting_period_hours': 4,
            },
            {
                'tier': 'standard',
                'name': 'Standard Shield',
                'description': 'Comprehensive coverage including pollution and extended claim days. Best value for full-time workers.',
                'base_weekly_premium': 79.00,
                'max_weekly_coverage': 4000.00,
                'daily_income_coverage_pct': 70,
                'max_claim_days_per_week': 3,
                'covers_weather': True,
                'covers_pollution': True,
                'covers_civil_unrest': False,
                'covers_platform_outage': False,
                'waiting_period_hours': 2,
            },
            {
                'tier': 'premium',
                'name': 'Premium Shield',
                'description': 'Maximum protection with civil unrest, platform outage coverage, and instant payouts.',
                'base_weekly_premium': 129.00,
                'max_weekly_coverage': 7000.00,
                'daily_income_coverage_pct': 85,
                'max_claim_days_per_week': 5,
                'covers_weather': True,
                'covers_pollution': True,
                'covers_civil_unrest': True,
                'covers_platform_outage': True,
                'waiting_period_hours': 1,
            },
        ]
        
        for plan_data in plans_data:
            plan, created = InsurancePlan.objects.get_or_create(
                tier=plan_data['tier'],
                defaults=plan_data
            )
            status = '✅ Created' if created else '⏭️ Already exists'
            self.stdout.write(f'  {status}: {plan.name} (₹{plan.base_weekly_premium}/week)')
        
        # Setup parametric triggers
        triggers = setup_default_triggers()
        self.stdout.write(f'\n  ✅ {triggers.count()} parametric triggers configured')
        
        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@gigshield.in',
                password='admin123',
                first_name='Admin',
                last_name='GigShield',
                role='admin',
            )
            self.stdout.write(f'  ✅ Admin user created (admin / admin123)')
        else:
            self.stdout.write(f'  ⏭️ Admin user already exists')
        
        # Create a demo worker
        if not User.objects.filter(username='demo_worker').exists():
            from accounts.models import GigWorkerProfile
            
            worker = User.objects.create_user(
                username='demo_worker',
                email='worker@gigshield.in',
                password='worker123',
                first_name='Rahul',
                last_name='Sharma',
                role='worker',
                phone='9876543210',
            )
            
            GigWorkerProfile.objects.create(
                user=worker,
                platform='zomato',
                delivery_type='food',
                vehicle_type='motorcycle',
                city='Mumbai',
                zone='Andheri West',
                pincode='400053',
                latitude=19.1364,
                longitude=72.8296,
                platform_id='ZMT-12345',
                avg_weekly_earnings=4500.00,
                avg_daily_deliveries=18,
                avg_daily_hours=9,
                preferred_shift='flexible',
                experience_months=18,
                risk_score=55.0,
                risk_category='medium',
                upi_id='rahul@paytm',
                is_verified=True,
            )
            self.stdout.write(f'  ✅ Demo worker created (demo_worker / worker123)')
        else:
            self.stdout.write(f'  ⏭️ Demo worker already exists')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Database seeded successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Worker: demo_worker / worker123')
