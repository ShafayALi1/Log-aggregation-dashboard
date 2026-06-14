from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json

from logs.models import Log, LogSource, AlertRule, Alert, LogRetentionPolicy
from log_ingestion import FileLogIngester, APILogIngester  # noqa - loaded via sys.path
from anomaly_detection import AnomalyDetector, AlertProcessor  # noqa


class LogSourceViewSet(viewsets.ModelViewSet):
    """API endpoints for log sources"""
    queryset = LogSource.objects.all()
    
    def get_serializer_data(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'source_type': instance.source_type,
            'description': instance.description,
            'is_active': instance.is_active,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
            'log_count': instance.logs.count()
        }
    
    def list(self, request):
        sources = self.get_queryset()
        data = [self.get_serializer_data(s) for s in sources]
        return Response(data)
    
    def retrieve(self, request, pk=None):
        source = get_object_or_404(LogSource, pk=pk)
        return Response(self.get_serializer_data(source))
    
    def create(self, request):
        name = request.data.get('name')
        source_type = request.data.get('source_type')
        
        if not name or not source_type:
            return Response({'error': 'Missing required fields'}, status=400)
        
        source, created = LogSource.objects.get_or_create(
            name=name,
            defaults={
                'source_type': source_type,
                'description': request.data.get('description', '')
            }
        )
        
        return Response(self.get_serializer_data(source), status=201)
    
    @action(detail=True, methods=['post'])
    def upload_logs(self, request, pk=None):
        """Upload log file"""
        source = get_object_or_404(LogSource, pk=pk)
        
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['file']
        ingester = FileLogIngester()
        
        # Save file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk.decode('utf-8'))
            tmp_path = tmp.name
        
        # Ingest logs
        parsed_logs = ingester.ingest_file(tmp_path)
        
        # Save to database
        detector = AnomalyDetector()
        created_count = 0
        created_logs = []
        
        for parsed_log in parsed_logs:
            log = Log(
                source=source,
                timestamp=parsed_log['timestamp'],
                level=parsed_log['level'],
                service=parsed_log['service'],
                message=parsed_log['message'],
                metadata=parsed_log.get('metadata', {})
            )
            
            # Check for anomalies
            anomaly_result = detector.detect_anomaly(
                Log.objects.filter(source=source),
                parsed_log['service']
            )
            log.is_anomaly = anomaly_result['is_anomaly']
            log.anomaly_score = abs(anomaly_result['z_score'])
            
            log.save()
            created_logs.append(log)
            created_count += 1
        
        # Check alert rules
        processor = AlertProcessor(detector)
        alert_rules = AlertRule.objects.all()
        triggered_rules = processor.process_logs_for_alerts(created_logs, alert_rules)
        for rule in triggered_rules:
            Alert.objects.create(
                rule=rule,
                log_count=created_count,
                message=f"Alert triggered: {rule.name}",
                details={'triggered_logs': created_count}
            )

        return Response({
            'message': f'Successfully ingested {created_count} logs',
            'count': created_count,
            'alerts_triggered': len(triggered_rules)
        })


class LogViewSet(viewsets.ModelViewSet):
    """API endpoints for logs"""
    queryset = Log.objects.all()
    
    def get_serializer_data(self, instance):
        return {
            'id': instance.id,
            'source': instance.source.name,
            'timestamp': instance.timestamp,
            'level': instance.level,
            'service': instance.service,
            'message': instance.message,
            'metadata': instance.metadata,
            'is_anomaly': instance.is_anomaly,
            'anomaly_score': instance.anomaly_score,
            'created_at': instance.created_at
        }
    
    def list(self, request):
        queryset = self.get_queryset()
        
        # Filters
        if 'service' in request.query_params:
            queryset = queryset.filter(service=request.query_params['service'])
        
        if 'level' in request.query_params:
            queryset = queryset.filter(level=request.query_params['level'])
        
        if 'is_anomaly' in request.query_params:
            is_anomaly = request.query_params['is_anomaly'].lower() == 'true'
            queryset = queryset.filter(is_anomaly=is_anomaly)
        
        if 'search' in request.query_params:
            search_term = request.query_params['search']
            queryset = queryset.filter(
                Q(message__icontains=search_term) |
                Q(service__icontains=search_term)
            )
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 100))
        
        total = queryset.count()
        queryset = queryset[(page-1)*page_size:page*page_size]
        
        data = [self.get_serializer_data(log) for log in queryset]
        
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': data
        })
    
    def retrieve(self, request, pk=None):
        log = get_object_or_404(Log, pk=pk)
        return Response(self.get_serializer_data(log))
    
    @action(detail=False, methods=['post'])
    def ingest_api(self, request):
        """Ingest logs via API"""
        source_name = request.data.get('source', 'api-source')
        logs_data = request.data.get('logs', [])
        
        # Get or create source
        source, _ = LogSource.objects.get_or_create(
            name=source_name,
            defaults={'source_type': 'api'}
        )
        
        # Ingest logs
        ingester = APILogIngester()
        parsed_logs = ingester.process_api_logs(logs_data)
        
        detector = AnomalyDetector()
        processor = AlertProcessor(detector)
        
        created_logs = []
        for parsed_log in parsed_logs:
            log = Log(
                source=source,
                timestamp=parsed_log['timestamp'],
                level=parsed_log['level'],
                service=parsed_log['service'],
                message=parsed_log['message'],
                metadata=parsed_log.get('metadata', {})
            )
            
            # Anomaly detection
            anomaly_result = detector.detect_anomaly(
                Log.objects.filter(source=source),
                parsed_log['service']
            )
            log.is_anomaly = anomaly_result['is_anomaly']
            log.anomaly_score = abs(anomaly_result['z_score'])
            
            log.save()
            created_logs.append(log)
        
        # Check alert rules
        alert_rules = AlertRule.objects.all()
        triggered_rules = processor.process_logs_for_alerts(created_logs, alert_rules)
        
        triggered_alerts = []
        for rule in triggered_rules:
            alert = Alert.objects.create(
                rule=rule,
                log_count=len(created_logs),
                message=f"Alert triggered: {rule.name}",
                details={'triggered_logs': len(created_logs)}
            )
            triggered_alerts.append({
                'id': alert.id,
                'rule': rule.name,
                'message': alert.message
            })
        
        return Response({
            'message': f'Ingested {len(created_logs)} logs',
            'ingested_count': len(created_logs),
            'triggered_alerts': triggered_alerts
        }, status=201)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get log statistics"""
        queryset = self.get_queryset()
        
        # Time range filter (0 = all time)
        hours = int(request.query_params.get('hours', 0))
        if hours > 0:
            since = timezone.now() - timedelta(hours=hours)
            queryset = queryset.filter(timestamp__gte=since)
        
        stats = {
            'total_logs': queryset.count(),
            'by_level': {},
            'by_service': {},
            'anomalies_count': queryset.filter(is_anomaly=True).count(),
            'error_rate': 0
        }
        
        # Count by level
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            count = queryset.filter(level=level).count()
            if count > 0:
                stats['by_level'][level] = count
        
        # Count by service
        services = queryset.values('service').annotate(count=Count('id'))
        for service in services:
            stats['by_service'][service['service']] = service['count']
        
        # Calculate error rate
        total = queryset.count()
        if total > 0:
            error_count = queryset.filter(level__in=['ERROR', 'CRITICAL']).count()
            stats['error_rate'] = round((error_count / total) * 100, 2)
        
        return Response(stats)


class AlertRuleViewSet(viewsets.ModelViewSet):
    """API endpoints for alert rules"""
    queryset = AlertRule.objects.all()
    
    def get_serializer_data(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'description': instance.description,
            'condition_type': instance.condition_type,
            'service_filter': instance.service_filter,
            'level_filter': instance.level_filter,
            'text_pattern': instance.text_pattern,
            'threshold_value': instance.threshold_value,
            'threshold_window_minutes': instance.threshold_window_minutes,
            'enabled': instance.enabled,
            'email_recipients': instance.email_recipients,
            'severity': instance.severity,
            'created_at': instance.created_at
        }
    
    def list(self, request):
        queryset = self.get_queryset()
        data = [self.get_serializer_data(rule) for rule in queryset]
        return Response(data)
    
    def retrieve(self, request, pk=None):
        rule = get_object_or_404(AlertRule, pk=pk)
        return Response(self.get_serializer_data(rule))
    
    def create(self, request):
        rule = AlertRule.objects.create(
            name=request.data.get('name'),
            description=request.data.get('description', ''),
            condition_type=request.data.get('condition_type'),
            service_filter=request.data.get('service_filter', ''),
            level_filter=request.data.get('level_filter', ''),
            text_pattern=request.data.get('text_pattern', ''),
            threshold_value=request.data.get('threshold_value', 5),
            threshold_window_minutes=request.data.get('threshold_window_minutes', 5),
            enabled=request.data.get('enabled', True),
            email_recipients=request.data.get('email_recipients', ''),
            severity=request.data.get('severity', 'medium')
        )
        return Response(self.get_serializer_data(rule), status=201)


class AlertViewSet(viewsets.ModelViewSet):
    """API endpoints for alerts"""
    queryset = Alert.objects.all()
    
    def get_serializer_data(self, instance):
        return {
            'id': instance.id,
            'rule': instance.rule.name,
            'status': instance.status,
            'log_count': instance.log_count,
            'message': instance.message,
            'details': instance.details,
            'triggered_at': instance.triggered_at,
            'acknowledged_at': instance.acknowledged_at,
            'resolved_at': instance.resolved_at
        }
    
    def list(self, request):
        queryset = self.get_queryset()
        
        if 'status' in request.query_params:
            queryset = queryset.filter(status=request.query_params['status'])
        
        data = [self.get_serializer_data(alert) for alert in queryset]
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = get_object_or_404(Alert, pk=pk)
        alert.acknowledge()
        return Response(self.get_serializer_data(alert))
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = get_object_or_404(Alert, pk=pk)
        alert.resolve()
        return Response(self.get_serializer_data(alert))
