from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*allowed_roles):
    """
    Generic decorator that restricts access to users with specific roles.
    Usage: @role_required('worker', 'admin')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access that page.')
                # Redirect to the user's own dashboard
                if request.user.role == 'citizen':
                    return redirect('citizen_dashboard')
                elif request.user.role == 'worker':
                    return redirect('worker_dashboard')
                elif request.user.role == 'admin':
                    return redirect('admin_dashboard')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def citizen_required(view_func):
    """Decorator to restrict access to citizens only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'citizen':
            messages.error(request, 'You do not have permission to access that page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def worker_required(view_func):
    """Decorator to restrict access to workers only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'worker':
            messages.error(request, 'You do not have permission to access that page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to restrict access to admins only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'admin':
            messages.error(request, 'You do not have permission to access that page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper
