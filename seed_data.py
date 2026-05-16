"""Seed script to populate the database with sample data."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgarbage.settings')
django.setup()

from accounts.models import User
from citizen.models import Report
from administrator.models import GarbageBin
from django.utils import timezone
from datetime import timedelta

print("Seeding database...")

# Create sample users
citizen1, _ = User.objects.get_or_create(username='rahul', defaults={
    'email': 'rahul@example.com', 'role': 'citizen', 'phone': '9876543210',
    'address': '12 MG Road, Sector 5, Bangalore'
})
citizen1.set_password('test1234')
citizen1.save()

citizen2, _ = User.objects.get_or_create(username='priya', defaults={
    'email': 'priya@example.com', 'role': 'citizen', 'phone': '9876543211',
    'address': '45 Green Park, Delhi'
})
citizen2.set_password('test1234')
citizen2.save()

worker1, _ = User.objects.get_or_create(username='worker1', defaults={
    'email': 'worker1@example.com', 'role': 'worker', 'phone': '9876543220',
    'address': 'Municipal Office, Zone A'
})
worker1.set_password('test1234')
worker1.save()

worker2, _ = User.objects.get_or_create(username='worker2', defaults={
    'email': 'worker2@example.com', 'role': 'worker', 'phone': '9876543221',
    'address': 'Municipal Office, Zone B'
})
worker2.set_password('test1234')
worker2.save()

print(f"Users: {User.objects.count()}")

# Create sample reports
now = timezone.now()
reports_data = [
    {'title': 'Overflowing garbage bin near bus stop',
     'description': 'The garbage bin near the main bus stop has been overflowing for 3 days. Waste is scattered around the area causing health hazards.',
     'location': 'Bus Stop, MG Road, Sector 5', 'citizen': citizen1, 'priority': 'high', 'status': 'pending',
     'created_at': now - timedelta(hours=2)},
    {'title': 'Illegal waste dumping in park',
     'description': 'Construction waste and household garbage has been dumped illegally in the community park area.',
     'location': 'Central Park, Green Avenue', 'citizen': citizen1, 'priority': 'critical', 'status': 'assigned',
     'assigned_worker': worker1, 'created_at': now - timedelta(days=1)},
    {'title': 'Broken garbage bin leaking waste',
     'description': 'The metallic garbage bin is broken and leaking liquid waste on the sidewalk. Very unhygienic conditions.',
     'location': '23 Market Road, Old City', 'citizen': citizen2, 'priority': 'high', 'status': 'in_progress',
     'assigned_worker': worker1, 'worker_notes': 'On my way to the location. Will need replacement bin.',
     'created_at': now - timedelta(days=2)},
    {'title': 'No garbage collection for a week',
     'description': 'Our area has not had garbage collection for over a week. Bins are full and waste is piling up.',
     'location': 'Residential Block C, Sector 12', 'citizen': citizen2, 'priority': 'medium', 'status': 'resolved',
     'assigned_worker': worker2, 'worker_notes': 'Collection completed. Regular schedule resumed.',
     'created_at': now - timedelta(days=4)},
    {'title': 'Dead animal carcass on road',
     'description': 'A dead animal is lying near the roadside creating foul smell and attracting stray dogs.',
     'location': 'Highway Junction, NH-48', 'citizen': citizen1, 'priority': 'critical', 'status': 'pending',
     'created_at': now - timedelta(hours=5)},
    {'title': 'Plastic waste in drainage canal',
     'description': 'Large amounts of plastic waste blocking the drainage canal causing water stagnation.',
     'location': 'Canal Road, Near Railway Station', 'citizen': citizen2, 'priority': 'medium', 'status': 'assigned',
     'assigned_worker': worker2, 'created_at': now - timedelta(days=1, hours=8)},
]

for rd in reports_data:
    created = rd.pop('created_at', now)
    r, created_flag = Report.objects.get_or_create(title=rd['title'], defaults=rd)
    if created_flag:
        Report.objects.filter(id=r.id).update(created_at=created)

print(f"Reports: {Report.objects.count()}")

# Create sample garbage bins
bins_data = [
    {'location': 'MG Road Bus Stop, Sector 5', 'capacity': 85, 'status': 'full', 'assigned_worker': worker1},
    {'location': 'Central Park Entrance', 'capacity': 45, 'status': 'half', 'assigned_worker': worker1},
    {'location': 'Market Road Junction', 'capacity': 95, 'status': 'overflow', 'assigned_worker': worker2},
    {'location': 'Railway Station Gate B', 'capacity': 20, 'status': 'empty', 'assigned_worker': worker2},
    {'location': 'Hospital Road, Block A', 'capacity': 60, 'status': 'half', 'assigned_worker': worker1},
    {'location': 'School Lane, Sector 9', 'capacity': 10, 'status': 'empty'},
]

for bd in bins_data:
    GarbageBin.objects.get_or_create(location=bd['location'], defaults=bd)

print(f"Bins: {GarbageBin.objects.count()}")
print("Done! ✓")
