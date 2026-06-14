from django.db import models
from django.utils import timezone
import json

class LogSource(models.Model):
    """Represents a source of logs"""
    SOURCE_CHOICES = [
        ('file', 'File Upload'),
        ('syslog', 'Syslog'),
        ('api', 'API'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.source_type})"


class Log(models.Model):
    """Main log entry model"""
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    source = models.ForeignKey(LogSource, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(db_index=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, db_index=True)
    service = models.CharField(max_length=100, db_index=True)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    # Anomaly Detection
    is_anomaly = models.BooleanField(default=False, db_index=True)
    anomaly_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'level']),
            models.Index(fields=['service', 'timestamp']),
            models.Index(fields=['is_anomaly', 'timestamp']),
        ]
    
    def __str__(self):
        return f"[{self.level}] {self.service} - {self.timestamp}"


class AlertRule(models.Model):
    """Define alert rules based on log patterns"""
    CONDITION_CHOICES = [
        ('contains', 'Contains text'),
        ('level_equals', 'Level equals'),
        ('error_rate', 'Error rate exceeds'),
        ('frequency', 'Frequency exceeds'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    condition_type = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    
    # Pattern matching
    service_filter = models.CharField(max_length=100, blank=True)
    level_filter = models.CharField(max_length=20, blank=True)
    text_pattern = models.TextField(blank=True)
    
    # Threshold
    threshold_value = models.IntegerField(default=5)
    threshold_window_minutes = models.IntegerField(default=5)
    
    # Alert Configuration
    enabled = models.BooleanField(default=True)
    email_recipients = models.TextField(blank=True, help_text="Comma-separated emails")
    severity = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.condition_type})"
    
    def get_email_list(self):
        if self.email_recipients:
            return [e.strip() for e in self.email_recipients.split(',')]
        return []


class Alert(models.Model):
    """Generated alerts from triggered rules"""
    STATUS_CHOICES = [
        ('triggered', 'Triggered'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='alerts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='triggered')
    
    # Alert Details
    log_count = models.IntegerField()
    message = models.TextField()
    details = models.JSONField(default=dict)
    
    # Timestamps
    triggered_at = models.DateTimeField(auto_now_add=True, db_index=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['status', 'triggered_at']),
            models.Index(fields=['rule', 'triggered_at']),
        ]
    
    def __str__(self):
        return f"{self.rule.name} - {self.status}"
    
    def acknowledge(self):
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self):
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()


class LogRetentionPolicy(models.Model):
    """Manage log retention and cleanup"""
    name = models.CharField(max_length=100)
    service_pattern = models.CharField(max_length=100)
    retention_days = models.IntegerField(default=30)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_cleanup = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.retention_days} days)"
