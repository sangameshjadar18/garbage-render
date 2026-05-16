from .models import Notification

def notifications(request):
    """Injects unread notifications into the context for authenticated users."""
    if request.user.is_authenticated:
        return {'notifications': request.user.notifications.filter(is_read=False)}
    return {'notifications': []}
