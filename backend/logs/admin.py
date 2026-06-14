from django.contrib import admin
from .models import Log, LogSource, AlertRule, Alert, LogRetentionPolicy


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'level', 'service', 'is_anomaly']
    list_filter = ['level', 'service', 'is_anomaly']
    search_fields = ['message', 'service']


@admin.register(LogSource)
class LogSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'is_active']


admin.site.register(AlertRule)
admin.site.register(Alert)
admin.site.register(LogRetentionPolicy)
