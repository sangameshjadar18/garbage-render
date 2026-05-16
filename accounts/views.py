from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from .models import Notification


def register_view(request):
    """Handle user registration with role selection."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handle user login and redirect based on role."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                # Redirect based on role
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'worker':
                    return redirect('worker_dashboard')
                else:
                    return redirect('citizen_dashboard')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Log out the user."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    """View and update user profile."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# =============================================
# NOTIFICATION API ENDPOINTS (AJAX)
# =============================================

@login_required
def api_notifications(request):
    """AJAX: Return unread notifications as JSON for live badge/dropdown updates."""
    notifs = Notification.objects.filter(user=request.user, is_read=False)[:15]
    data = [{
        'id': n.id,
        'message': n.message,
        'created_at': n.created_at.strftime('%b %d, %H:%M'),
        'time_ago': _time_ago(n.created_at),
    } for n in notifs]
    return JsonResponse({'notifications': data, 'count': notifs.count()})


@login_required
@require_POST
def api_mark_all_read(request):
    """AJAX: Mark all notifications as read for the authenticated user."""
    count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True, 'marked': count})


@login_required
@require_POST
def api_mark_read(request, notif_id):
    """AJAX: Mark a single notification as read."""
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'success': True})


def _time_ago(dt):
    """Helper: human-readable time difference."""
    from django.utils import timezone
    diff = timezone.now() - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        return f'{int(seconds // 60)}m ago'
    elif seconds < 86400:
        return f'{int(seconds // 3600)}h ago'
    else:
        return f'{int(seconds // 86400)}d ago'
