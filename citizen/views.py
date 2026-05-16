from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import citizen_required
from .models import Report, Feedback
from administrator.models import GarbageBin
import math
from .forms import ReportForm


@citizen_required
def citizen_dashboard(request):
    """Citizen dashboard with overview of their own reports only."""
    reports = Report.objects.filter(citizen=request.user)
    total = reports.count()
    pending = reports.filter(status='pending').count()
    in_progress = reports.filter(status__in=['assigned', 'in_progress']).count()
    resolved = reports.filter(status='resolved').count()
    recent_reports = reports[:5]

    context = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'recent_reports': recent_reports,
    }
    return render(request, 'citizen/dashboard.html', context)


@citizen_required
def submit_report(request):
    """Submit a new garbage complaint with optional image upload."""
    if request.method == 'POST':
        try:
            lat_str = request.POST.get('latitude')
            lon_str = request.POST.get('longitude')
            if lat_str and lon_str:
                lat = float(lat_str)
                lon = float(lon_str)

                if not (-90 <= lat <= 90):
                    raise ValueError("Invalid latitude")

                if not (-180 <= lon <= 180):
                    raise ValueError("Invalid longitude")
        except (ValueError, TypeError):
            messages.error(request, "Invalid location values")
            return redirect('submit_report')

        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.citizen = request.user
            report.save()
            messages.success(request, 'Your report has been submitted successfully!')
            return redirect('citizen_dashboard')
    else:
        form = ReportForm()

    return render(request, 'citizen/submit_report.html', {'form': form})


@citizen_required
def report_list(request):
    """List all reports submitted by this citizen with filtering."""
    reports = Report.objects.filter(citizen=request.user)

    # Filtering by status and priority
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')

    if status_filter:
        reports = reports.filter(status=status_filter)
    if priority_filter:
        reports = reports.filter(priority=priority_filter)

    context = {
        'reports': reports,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'citizen/report_list.html', context)


@citizen_required
def track_report(request, report_id):
    """Track a specific report's status and details (citizen's own report only)."""
    report = get_object_or_404(Report, id=report_id, citizen=request.user)
    return render(request, 'citizen/track_report.html', {'report': report})


@citizen_required
def submit_feedback(request, report_id):
    """Handle feedback submission from citizens for completed reports."""
    report = get_object_or_404(Report, id=report_id, citizen=request.user)
    
    if request.method == "POST":
        # Ensure feedback only for resolved/completed reports
        if report.status != 'resolved':
            messages.error(request, 'Feedback can only be submitted for resolved reports.')
            return redirect('track_report', report_id=report.id)
            
        # Optional: Prevent duplicate feedback
        if Feedback.objects.filter(user=request.user, report=report).exists():
            messages.warning(request, 'You have already submitted feedback for this report.')
            return redirect('track_report', report_id=report.id)

        message = request.POST.get('message', '')
        rating = request.POST.get('rating')

        if rating:
            Feedback.objects.create(
                user=request.user,
                report=report,
                message=message,
                rating=int(rating)
            )
            messages.success(request, 'Feedback submitted successfully!')
        
    return redirect('track_report', report_id=report.id)


# =============================================
# API ENDPOINTS (AJAX — No Page Reload)
# =============================================

@login_required
def api_report_status(request, report_id):
    """
    AJAX GET: Return real-time status of a single report as JSON.
    Used by citizen dashboard for auto-polling.
    Endpoint: /citizen/api/report/<id>/status/
    """
    report = get_object_or_404(Report, id=report_id)

    # Permission: citizens can only see their own reports
    if request.user.is_citizen and report.citizen != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    return JsonResponse({
        'id': report.id,
        'title': report.title,
        'status': report.status,
        'status_display': report.get_status_display(),
        'status_color': report.status_color,
        'priority': report.priority,
        'priority_display': report.get_priority_display(),
        'priority_color': report.priority_color,
        'worker': report.assigned_worker.username if report.assigned_worker else None,
        'worker_notes': report.worker_notes or '',
        'updated_at': report.updated_at.strftime('%b %d, %Y %I:%M %p'),
    })


@citizen_required
def api_dashboard_stats(request):
    """
    AJAX GET: Return citizen dashboard stats as JSON for live auto-update.
    Endpoint: /citizen/api/dashboard-stats/
    """
    reports = Report.objects.filter(citizen=request.user)
    recent = reports[:5]

    return JsonResponse({
        'total': reports.count(),
        'pending': reports.filter(status='pending').count(),
        'in_progress': reports.filter(status__in=['assigned', 'in_progress']).count(),
        'resolved': reports.filter(status='resolved').count(),
        'recent_reports': [{
            'id': r.id,
            'title': r.title[:30],
            'location': r.location[:25],
            'priority': r.get_priority_display(),
            'priority_color': r.priority_color,
            'status': r.get_status_display(),
            'status_color': r.status_color,
            'date': r.created_at.strftime('%b %d, %Y'),
        } for r in recent],
    })


def _distance_km(lat1, lon1, lat2, lon2):
    """Return distance between two points using the Haversine formula."""
    radius = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@citizen_required
def nearby_bins_map(request):
    """Show a map where citizens can find nearest bins by waste type."""
    return render(request, 'citizen/nearby_bins_map.html')


@citizen_required
def api_nearby_bins(request):
    """AJAX endpoint: returns nearest bins for the selected waste type."""
    try:
        user_lat = float(request.GET.get('lat'))
        user_lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Valid latitude and longitude are required.'}, status=400)

    waste_type = request.GET.get('waste_type', '')
    bins = GarbageBin.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

    if waste_type in dict(GarbageBin.WASTE_TYPE_CHOICES):
        bins = bins.filter(waste_type=waste_type)

    result = []
    for bin_obj in bins:
        distance = _distance_km(user_lat, user_lng, bin_obj.latitude, bin_obj.longitude)
        result.append({
            'id': bin_obj.id,
            'location': bin_obj.location,
            'latitude': bin_obj.latitude,
            'longitude': bin_obj.longitude,
            'waste_type': bin_obj.waste_type,
            'waste_type_display': bin_obj.get_waste_type_display(),
            'status': bin_obj.get_status_display(),
            'capacity': bin_obj.capacity,
            'distance_km': round(distance, 2),
            'google_maps_url': f'https://www.google.com/maps/dir/?api=1&destination={bin_obj.latitude},{bin_obj.longitude}',
        })

    result.sort(key=lambda item: item['distance_km'])
    return JsonResponse({'bins': result[:10]})
