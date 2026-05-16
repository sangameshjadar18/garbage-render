from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
    path('report/new/', views.submit_report, name='submit_report'),
    path('reports/', views.report_list, name='report_list'),
    path('report/<int:report_id>/', views.track_report, name='track_report'),
    path('feedback/<int:report_id>/', views.submit_feedback, name='submit_feedback'),
    path('nearby-bins/', views.nearby_bins_map, name='nearby_bins_map'),
    # AJAX API endpoints
    path('api/report/<int:report_id>/status/', views.api_report_status, name='api_report_status'),
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/nearby-bins/', views.api_nearby_bins, name='api_nearby_bins'),
]
