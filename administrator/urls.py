from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('bins/', views.manage_bins, name='manage_bins'),
    path('bins/add/', views.add_bin, name='add_bin'),
    path('bins/<int:bin_id>/edit/', views.edit_bin, name='edit_bin'),
    path('bins/<int:bin_id>/delete/', views.delete_bin, name='delete_bin'),
    path('reports/', views.reports_analytics, name='reports_analytics'),
    path('reports/<int:report_id>/assign/', views.assign_task, name='assign_task'),
    path('feedback/', views.manage_feedback, name='manage_feedback'),
]
