"""
Anomaly Detection Module
Uses statistical methods to identify unusual log patterns
"""

from collections import defaultdict
from datetime import datetime, timedelta
from django.utils import timezone
import statistics


class AnomalyDetector:
    """Detect anomalies in log patterns using statistical analysis"""
    
    def __init__(self, threshold_std=2.5, window_hours=24):
        """
        Initialize anomaly detector
        
        Args:
            threshold_std: Number of standard deviations for anomaly (default 2.5)
            window_hours: Time window for baseline calculation
        """
        self.threshold_std = threshold_std
        self.window_hours = window_hours
    
    def get_baseline_stats(self, logs, service_name):
        """
        Calculate baseline statistics for a service
        
        Args:
            logs: QuerySet of Log objects
            service_name: Service to analyze
            
        Returns:
            dict with mean and std dev of error counts
        """
        now = timezone.now()
        past = now - timedelta(hours=self.window_hours)
        
        # Count errors per hour
        hourly_counts = defaultdict(int)
        
        for log in logs.filter(
            service=service_name,
            level__in=['ERROR', 'CRITICAL'],
            timestamp__gte=past,
            timestamp__lte=now
        ):
            hour_key = log.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] += 1
        
        if not hourly_counts:
            return {'mean': 0, 'std_dev': 0, 'count': 0}
        
        counts = list(hourly_counts.values())
        mean = statistics.mean(counts)
        
        # Calculate standard deviation
        if len(counts) > 1:
            std_dev = statistics.stdev(counts)
        else:
            std_dev = 0
        
        return {
            'mean': mean,
            'std_dev': std_dev,
            'count': len(counts),
            'min': min(counts),
            'max': max(counts)
        }
    
    def detect_anomaly(self, logs, service_name, recent_window_minutes=5):
        """
        Detect if current error rate is anomalous
        
        Args:
            logs: QuerySet of Log objects
            service_name: Service to analyze
            recent_window_minutes: Time window for recent count
            
        Returns:
            dict with anomaly detection results
        """
        stats = self.get_baseline_stats(logs, service_name)
        
        now = timezone.now()
        recent_past = now - timedelta(minutes=recent_window_minutes)
        
        # Count recent errors
        recent_count = logs.filter(
            service=service_name,
            level__in=['ERROR', 'CRITICAL'],
            timestamp__gte=recent_past,
            timestamp__lte=now
        ).count()
        
        # Calculate z-score
        if stats['std_dev'] == 0:
            z_score = 0 if recent_count == stats['mean'] else float('inf')
        else:
            z_score = (recent_count - stats['mean']) / stats['std_dev']
        
        is_anomaly = abs(z_score) > self.threshold_std
        
        return {
            'is_anomaly': is_anomaly,
            'z_score': z_score,
            'recent_count': recent_count,
            'baseline_mean': stats['mean'],
            'baseline_std': stats['std_dev'],
            'threshold': self.threshold_std,
            'severity': self._calculate_severity(z_score)
        }
    
    def _calculate_severity(self, z_score):
        """Calculate severity based on z-score"""
        abs_z = abs(z_score)
        if abs_z > 3.5:
            return 'critical'
        elif abs_z > 3.0:
            return 'high'
        elif abs_z > 2.5:
            return 'medium'
        else:
            return 'low'
    
    def detect_error_rate_spike(self, logs, service_name, threshold_percentage=50):
        """
        Detect if error rate increased significantly
        
        Args:
            logs: QuerySet of Log objects
            service_name: Service to analyze
            threshold_percentage: Increase threshold
            
        Returns:
            bool indicating if spike detected
        """
        now = timezone.now()
        past_hour = now - timedelta(hours=1)
        past_2_hours = now - timedelta(hours=2)
        
        # Current hour errors
        current_errors = logs.filter(
            service=service_name,
            level__in=['ERROR', 'CRITICAL'],
            timestamp__gte=past_hour,
            timestamp__lte=now
        ).count()
        
        # Previous hour errors
        previous_errors = logs.filter(
            service=service_name,
            level__in=['ERROR', 'CRITICAL'],
            timestamp__gte=past_2_hours,
            timestamp__lt=past_hour
        ).count()
        
        if previous_errors == 0:
            return current_errors > 0
        
        increase_percentage = ((current_errors - previous_errors) / previous_errors) * 100
        
        return increase_percentage >= threshold_percentage
    
    def detect_service_silence(self, logs, service_name, silence_minutes=30):
        """
        Detect if a service stopped logging
        
        Args:
            logs: QuerySet of Log objects
            service_name: Service to analyze
            silence_minutes: Threshold for no logs
            
        Returns:
            dict with silence detection results
        """
        now = timezone.now()
        recent_past = now - timedelta(minutes=silence_minutes)
        
        recent_logs = logs.filter(
            service=service_name,
            timestamp__gte=recent_past,
            timestamp__lte=now
        ).count()
        
        is_silent = recent_logs == 0
        
        # Get last log timestamp
        last_log = logs.filter(service=service_name).order_by('-timestamp').first()
        
        return {
            'is_silent': is_silent,
            'minutes_since_last_log': (now - last_log.timestamp).total_seconds() / 60 if last_log else None,
            'threshold_minutes': silence_minutes
        }


class AlertProcessor:
    """Process and trigger alerts based on rules"""
    
    def __init__(self, anomaly_detector=None):
        self.detector = anomaly_detector or AnomalyDetector()
    
    def process_logs_for_alerts(self, new_logs, alert_rules):
        """
        Process new logs and check alert rules
        
        Args:
            new_logs: List of new Log objects
            alert_rules: QuerySet of AlertRule objects
            
        Returns:
            list of triggered alerts
        """
        triggered_alerts = []
        
        for rule in alert_rules.filter(enabled=True):
            if self._should_trigger_alert(rule, new_logs):
                triggered_alerts.append(rule)
        
        return triggered_alerts
    
    def _should_trigger_alert(self, rule, logs):
        """Check if alert rule should trigger"""
        
        if rule.condition_type == 'contains':
            return any(rule.text_pattern in log.message for log in logs)
        
        elif rule.condition_type == 'level_equals':
            return any(log.level == rule.level_filter for log in logs)
        
        elif rule.condition_type == 'error_rate':
            # Check error rate for specific service
            service_logs = [l for l in logs if l.service == rule.service_filter]
            error_logs = [l for l in service_logs if l.level in ['ERROR', 'CRITICAL']]
            
            if service_logs:
                error_rate = (len(error_logs) / len(service_logs)) * 100
                return error_rate >= rule.threshold_value
        
        elif rule.condition_type == 'frequency':
            # Check if error frequency exceeds threshold
            service_logs = [l for l in logs if l.service == rule.service_filter]
            error_logs = [l for l in service_logs if l.level in ['ERROR', 'CRITICAL']]
            return len(error_logs) >= rule.threshold_value
        
        return False
