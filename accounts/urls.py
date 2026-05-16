from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    # Notification API endpoints (AJAX)
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/mark-all-read/', views.api_mark_all_read, name='api_mark_all_read'),
    path('api/notifications/<int:notif_id>/read/', views.api_mark_read, name='api_mark_read'),
]
