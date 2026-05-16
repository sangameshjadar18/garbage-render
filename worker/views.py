import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.decorators import worker_required
from citizen.models import Report
from accounts.models import Notification
from administrator.models import GarbageBin


@worker_required
def worker_dashboard(request):
    """
    Worker dashboard showing ONLY reports assigned to this worker,
    plus any garbage bins assigned to them by admin.
    """
    my_tasks = Report.objects.filter(assigned_worker=request.user)

    total = my_tasks.count()
    pending = my_tasks.filter(status='assigned').count()
    in_progress = my_tasks.filter(status='in_progress').count()
    completed = my_tasks.filter(status='resolved').count()
    my_assigned = my_tasks.exclude(status='resolved').count()

    # Show unresolved assigned reports, ordered by priority
    recent_tasks = my_tasks.exclude(status='resolved').order_by('-priority', '-created_at')[:8]

    # BUG FIX: Also fetch garbage bins assigned to this worker
    assigned_bins = GarbageBin.objects.filter(assigned_worker=request.user)
    assigned_bins_count = assigned_bins.count()

    # DEBUG: verify bins are being fetched (remove after confirming fix)
    print(f"[DEBUG worker_dashboard] User: {request.user.username}, Assigned bins: {assigned_bins}, Count: {assigned_bins_count}")

    context = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'my_assigned': my_assigned,
        'recent_tasks': recent_tasks,
        'assigned_bins': assigned_bins,
        'assigned_bins_count': assigned_bins_count,
    }
    return render(request, 'worker/dashboard.html', context)


@worker_required
def my_tasks(request):
    """
    Dedicated view showing garbage bins assigned to this worker.
    BUG FIX: This view was missing — workers could never see assigned bins.
    """
    assigned_bins = GarbageBin.objects.filter(assigned_worker=request.user)

    # DEBUG: verify bins are being fetched (remove after confirming fix)
    print(f"[DEBUG my_tasks] User: {request.user.username}, Assigned bins queryset: {assigned_bins}")

    status_filter = request.GET.get('status', '')
    if status_filter:
        assigned_bins = assigned_bins.filter(status=status_filter)

    context = {
        'assigned_bins': assigned_bins,
        'status_filter': status_filter,
    }
    return render(request, 'worker/my_tasks.html', context)


@worker_required
def task_list(request):
    """List all reports assigned to THIS worker only, with filtering."""
    tasks = Report.objects.filter(assigned_worker=request.user)

    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'worker/task_list.html', context)


@worker_required
def task_detail(request, task_id):
    """View details of a specific report assigned to this worker."""
    task = get_object_or_404(Report, id=task_id, assigned_worker=request.user)
    return render(request, 'worker/task_detail.html', {'task': task})


@worker_required
def update_task_status(request, task_id):
    """Update the status of an assigned report (traditional form POST)."""
    task = get_object_or_404(Report, id=task_id, assigned_worker=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('worker_notes', '')

        # Allowed status transitions for workers
        if new_status in ['in_progress', 'resolved']:
            task.status = new_status
            task.worker_notes = notes
            if not task.worker:
                task.worker = request.user
            
            image = request.FILES.get('completion_image')
            if new_status == 'resolved' and image:
                task.completion_image = image
                
            task.save()

            # Send notification to citizen
            Notification.objects.create(
                user=task.citizen,
                message=f'Your report "{task.title}" has been updated to "{task.get_status_display()}".'
            )

            messages.success(request, f'Task status updated to "{task.get_status_display()}".')
        else:
            messages.error(request, 'Invalid status.')

        return redirect('task_detail', task_id=task.id)

    return render(request, 'worker/update_status.html', {'task': task})


# =============================================
# AJAX API ENDPOINT (No Page Reload)
# =============================================

@worker_required
@require_POST
def api_update_task_status(request, task_id):
    """
    AJAX POST: Update report status without page reload.
    Endpoint: /worker/api/task/<id>/update/
    Returns JSON with updated status info.
    
    Expected POST body (JSON):
        { "status": "in_progress" | "resolved", "worker_notes": "..." }
    """
    task = get_object_or_404(Report, id=task_id, assigned_worker=request.user)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    new_status = body.get('status', '')
    notes = body.get('worker_notes', '')

    # Validate allowed status transitions
    if new_status not in ['in_progress', 'resolved']:
        return JsonResponse({'error': 'Invalid status. Must be "in_progress" or "resolved".'}, status=400)

    # Update the report
    task.status = new_status
    task.worker_notes = notes
    if not task.worker:
        task.worker = request.user
    task.save()

    # Send notification to the citizen who submitted the report
    Notification.objects.create(
        user=task.citizen,
        message=f'Your report "{task.title}" has been updated to "{task.get_status_display()}".'
    )

    return JsonResponse({
        'success': True,
        'id': task.id,
        'status': task.status,
        'status_display': task.get_status_display(),
        'status_color': task.status_color,
        'worker_notes': task.worker_notes or '',
        'updated_at': task.updated_at.strftime('%b %d, %Y %I:%M %p'),
        'message': f'Task status updated to "{task.get_status_display()}".',
    })
