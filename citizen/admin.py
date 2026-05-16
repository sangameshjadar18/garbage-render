from django.contrib import admin
from .models import Report, Feedback


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'citizen', 'status', 'priority', 'location', 'assigned_worker', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'location', 'citizen__username')
    raw_id_fields = ('citizen', 'assigned_worker')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'report', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'report__title', 'message')
    raw_id_fields = ('user', 'report')
