from django.contrib import admin
from .models import GarbageBin


@admin.register(GarbageBin)
class GarbageBinAdmin(admin.ModelAdmin):
    list_display = ('location', 'status', 'capacity', 'assigned_worker', 'last_collected', 'updated_at')
    list_filter = ('status',)
    search_fields = ('location',)
