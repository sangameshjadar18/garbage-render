from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('tasks/', views.task_list, name='task_list'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/update/', views.update_task_status, name='update_task_status'),
    # AJAX API endpoint for status update without page reload
    path('api/task/<int:task_id>/update/', views.api_update_task_status, name='api_update_task_status'),
]
