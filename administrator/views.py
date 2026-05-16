from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from accounts.decorators import admin_required
from accounts.models import User, Notification
from citizen.models import Report, Feedback
from .models import GarbageBin
from .forms import GarbageBinForm, AssignWorkerForm


@admin_required
def admin_dashboard(request):
    """Admin dashboard with system-wide analytics."""
    # User stats
    total_users = User.objects.count()
    total_citizens = User.objects.filter(role='citizen').count()
    total_workers = User.objects.filter(role='worker').count()

    # Report stats
    total_reports = Report.objects.count()
    pending_reports = Report.objects.filter(status='pending').count()
    assigned_reports = Report.objects.filter(status='assigned').count()
    in_progress_reports = Report.objects.filter(status='in_progress').count()
    resolved_reports = Report.objects.filter(status='resolved').count()

    # Bin stats
    total_bins = GarbageBin.objects.count()
    overflow_bins = GarbageBin.objects.filter(status='overflow').count()
    full_bins = GarbageBin.objects.filter(status='full').count()

    # Recent reports
    recent_reports = Report.objects.all()[:10]

    # Recent feedback
    recent_feedback = Feedback.objects.all().order_by('-created_at')[:5]

    # Weekly report counts for chart
    today = timezone.now().date()
    weekly_data = []
    weekly_labels = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Report.objects.filter(created_at__date=day).count()
        weekly_data.append(count)
        weekly_labels.append(day.strftime('%a'))

    # Priority distribution
    priority_data = {
        'low': Report.objects.filter(priority='low').count(),
        'medium': Report.objects.filter(priority='medium').count(),
        'high': Report.objects.filter(priority='high').count(),
        'critical': Report.objects.filter(priority='critical').count(),
    }

    context = {
        'total_users': total_users,
        'total_citizens': total_citizens,
        'total_workers': total_workers,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'assigned_reports': assigned_reports,
        'in_progress_reports': in_progress_reports,
        'resolved_reports': resolved_reports,
        'total_bins': total_bins,
        'overflow_bins': overflow_bins,
        'full_bins': full_bins,
        'recent_reports': recent_reports,
        'weekly_data': weekly_data,
        'weekly_labels': weekly_labels,
        'priority_data': priority_data,
        'recent_feedback': recent_feedback,
    }
    return render(request, 'administrator/dashboard.html', context)

@admin_required
def manage_users(request):
    """Manage (list/deactivate) all users."""
    users = User.objects.all().order_by('-date_joined')

    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)

    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    context = {
        'users': users,
        'role_filter': role_filter,
        'search': search,
    }
    return render(request, 'administrator/manage_users.html', context)


@admin_required
def toggle_user_status(request, user_id):
    """Activate/Deactivate a user."""
    user = get_object_or_404(User, id=user_id)
    if user != request.user:  # Don't let admin deactivate themselves
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} has been {status}.')
    else:
        messages.error(request, 'You cannot deactivate your own account.')
    return redirect('manage_users')


@admin_required
def manage_bins(request):
    """CRUD for garbage bins."""
    bins = GarbageBin.objects.all()

    status_filter = request.GET.get('status', '')
    if status_filter:
        bins = bins.filter(status=status_filter)

    context = {
        'bins': bins,
        'status_filter': status_filter,
    }
    return render(request, 'administrator/manage_bins.html', context)


@admin_required
def add_bin(request):
    """Add a new garbage bin."""
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
            return redirect('add_bin')

        form = GarbageBinForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Garbage bin added successfully!')
            return redirect('manage_bins')
    else:
        form = GarbageBinForm()

    return render(request, 'administrator/add_bin.html', {'form': form})


@admin_required
def edit_bin(request, bin_id):
    """Edit an existing garbage bin."""
    garbage_bin = get_object_or_404(GarbageBin, id=bin_id)
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
            return redirect('edit_bin', bin_id=bin_id)

        form = GarbageBinForm(request.POST, instance=garbage_bin)
        print(f"[DEBUG edit_bin] POST data: {request.POST}")
        print(f"[DEBUG edit_bin] Form valid: {form.is_valid()}")
        print(f"[DEBUG edit_bin] Form errors: {form.errors}")
        if form.is_valid():
            form.save()
            messages.success(request, 'Garbage bin updated successfully!')
            return redirect('manage_bins')
    else:
        form = GarbageBinForm(instance=garbage_bin)

    return render(request, 'administrator/edit_bin.html', {'form': form, 'bin': garbage_bin})


@admin_required
def delete_bin(request, bin_id):
    """Delete a garbage bin."""
    garbage_bin = get_object_or_404(GarbageBin, id=bin_id)
    if request.method == 'POST':
        garbage_bin.delete()
        messages.success(request, 'Garbage bin deleted.')
        return redirect('manage_bins')
    return render(request, 'administrator/confirm_delete_bin.html', {'bin': garbage_bin})


@admin_required
def reports_analytics(request):
    """View all reports with analytics."""
    reports = Report.objects.all()

    # Filters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    search = request.GET.get('search', '')

    if status_filter:
        reports = reports.filter(status=status_filter)
    if priority_filter:
        reports = reports.filter(priority=priority_filter)
    if search:
        reports = reports.filter(
            Q(title__icontains=search) |
            Q(location__icontains=search) |
            Q(citizen__username__icontains=search)
        )

    context = {
        'reports': reports,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search': search,
    }
    return render(request, 'administrator/reports_analytics.html', context)


@admin_required
def assign_task(request, report_id):
    """Assign a report to a worker. Sends notifications to both worker and citizen."""
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        form = AssignWorkerForm(request.POST)
        if form.is_valid():
            report.assigned_worker = form.cleaned_data['worker']
            report.priority = form.cleaned_data['priority']
            report.status = 'assigned'
            report.save()

            # Notify the assigned worker
            Notification.objects.create(
                user=report.assigned_worker,
                message=f'You have been assigned a new task: "{report.title}" at {report.location}.'
            )

            # Notify the citizen who submitted the report
            Notification.objects.create(
                user=report.citizen,
                message=f'Your report "{report.title}" has been assigned to a worker and is being processed.'
            )

            messages.success(
                request,
                f'Report assigned to {report.assigned_worker.username}.'
            )
            return redirect('reports_analytics')
    else:
        form = AssignWorkerForm(initial={'priority': report.priority})

    return render(request, 'administrator/assign_task.html', {
        'form': form,
        'report': report,
    })


@admin_required
def manage_feedback(request):
    """View all citizen feedback."""
    feedback_list = Feedback.objects.all().order_by('-created_at')
    
    # Optional Filtering
    rating_filter = request.GET.get('rating', '')
    if rating_filter:
        feedback_list = feedback_list.filter(rating=rating_filter)
        
    context = {
        'feedbacks': feedback_list,
        'rating_filter': rating_filter,
    }
    return render(request, 'administrator/feedback_list.html', context)

