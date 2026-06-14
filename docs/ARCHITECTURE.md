# 🏗️ System Architecture

## Overview

The Log Aggregation & Analysis Dashboard follows a **three-tier architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                  Streamlit Dashboard                         │
│  (Visualization, User Interactions, Real-time Updates)       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│                  Django REST Backend                         │
│  (API Endpoints, Business Logic, Data Processing)            │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Log Ingestion│  │ Anomaly      │  │ Alert        │      │
│  │ Service      │  │ Detection    │  │ Processor    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL/ORM
┌────────────────────────▼────────────────────────────────────┐
│                   DATA LAYER                                 │
│              SQLite Database                                 │
│  (Logs, Sources, Rules, Alerts, Retention Policies)         │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Frontend Layer (Streamlit)

**Location:** `frontend/dashboard.py`

**Responsibilities:**
- User interface and visualization
- Real-time data fetching
- Interactive controls and filters
- Alert management UI

**Key Features:**
- Multi-page navigation
- Plotly charts and graphs
- Responsive layout
- Live metrics updates

**Data Flow:**
```
User Action → Streamlit → HTTP Request → Django API → Response → Visualization
```

### 2. Application Layer (Django)

#### 2.1 REST API Views
**File:** `backend/views.py`

**ViewSets:**
- `LogSourceViewSet`: Manage log sources
- `LogViewSet`: Query and ingest logs
- `AlertRuleViewSet`: Create/manage alert rules
- `AlertViewSet`: View and manage alerts

**Key Endpoints:**
- `/api/logs/` - Log operations
- `/api/rules/` - Alert rules
- `/api/alerts/` - Alert management
- `/api/sources/` - Log source management

#### 2.2 Log Ingestion Service
**File:** `backend/log_ingestion.py`

**Components:**
- `LogParser`: Multi-format log parsing
  - JSON logs
  - Standard logs `[TIMESTAMP] [LEVEL] [SERVICE] MESSAGE`
  - Syslog format (RFC 3164)
  - Apache/Nginx access logs
  - Auto-detection fallback

- `FileLogIngester`: File-based ingestion
  - Reads log files
  - Parses line-by-line
  - Bulk database insertion

- `SyslogIngester`: Network-based syslog
  - UDP socket listener
  - RFC 3164 parsing
  - Real-time message handling

- `APILogIngester`: REST API ingestion
  - JSON payload processing
  - Flexible log format support

- `LogIngestionManager`: Orchestrates all ingestion

#### 2.3 Anomaly Detection Service
**File:** `backend/anomaly_detection.py`

**Components:**
- `AnomalyDetector`: Statistical analysis
  - Baseline calculation (mean, std dev)
  - Z-score computation
  - Error rate spike detection
  - Service silence detection
  - Configurable thresholds

- `AlertProcessor`: Rule evaluation
  - Pattern matching
  - Condition evaluation
  - Alert triggering logic

#### 2.4 Django Models
**File:** `backend/models.py`

**Data Models:**
```
LogSource
  ├── name: CharField (unique)
  ├── source_type: CharField (file, syslog, api)
  ├── is_active: BooleanField
  └── logs: ForeignKey (reverse)

Log (Main model)
  ├── source: ForeignKey → LogSource
  ├── timestamp: DateTimeField (indexed)
  ├── level: CharField (indexed)
  ├── service: CharField (indexed)
  ├── message: TextField
  ├── metadata: JSONField
  ├── is_anomaly: BooleanField (indexed)
  └── anomaly_score: FloatField

AlertRule
  ├── name: CharField
  ├── condition_type: CharField
  ├── service_filter: CharField
  ├── level_filter: CharField
  ├── text_pattern: TextField
  ├── threshold_value: IntegerField
  ├── enabled: BooleanField
  └── email_recipients: TextField

Alert
  ├── rule: ForeignKey → AlertRule
  ├── status: CharField (triggered, acknowledged, resolved)
  ├── log_count: IntegerField
  ├── triggered_at: DateTimeField (indexed)
  ├── acknowledged_at: DateTimeField
  └── resolved_at: DateTimeField

LogRetentionPolicy
  ├── name: CharField
  ├── service_pattern: CharField
  ├── retention_days: IntegerField
  └── last_cleanup: DateTimeField
```

### 3. Data Layer (SQLite)

**Database:** SQLite3 (default)

**Key Features:**
- ACID compliance
- Indexed queries for performance
- JSON field support
- Transaction support

**Indexes:**
```
Log Table:
- (timestamp, level)
- (service, timestamp)
- (is_anomaly, timestamp)

Alert Table:
- (status, triggered_at)
- (rule, triggered_at)
```

---

## Data Flow Diagrams

### Flow 1: Log Ingestion & Processing

```
Log Source (File/API/Syslog)
         │
         ▼
    LogParser (Auto-detection)
         │
         ├─→ JSON Format?
         ├─→ Standard Format?
         ├─→ Syslog Format?
         └─→ Fallback
         │
         ▼
   Parsed Structure
   {
     timestamp, level, service,
     message, metadata
   }
         │
         ▼
    AnomalyDetector
    (Statistical Analysis)
         │
         ├─→ Get baseline stats
         ├─→ Calculate z-score
         └─→ Determine if anomaly
         │
         ▼
    Django Model Instance
    (Log with anomaly_score)
         │
         ▼
    Database Save
         │
         ▼
    AlertProcessor
    (Check rules)
         │
         ▼
    Alert Triggered?
    (If conditions met)
         │
         ▼
    Alert Record Created
```

### Flow 2: Alert Evaluation

```
New Logs Arrive
      │
      ▼
AlertProcessor.process_logs_for_alerts()
      │
      ├─→ For each AlertRule (enabled)
      │       │
      │       ├─→ Check condition_type
      │       │       ├─ contains
      │       │       ├─ level_equals
      │       │       ├─ error_rate
      │       │       └─ frequency
      │       │
      │       ├─→ Evaluate condition
      │       │
      │       └─→ Trigger? YES/NO
      │
      ▼
Triggered Rules List
      │
      ▼
Create Alert Records
      │
      ├─→ Alert.status = 'triggered'
      ├─→ Alert.log_count = count
      └─→ Alert.details = metadata
      │
      ▼
Send Notifications (Email)
```

### Flow 3: Dashboard Visualization

```
Streamlit App
      │
      ├─→ Dashboard Page
      │       │
      │       ├─→ /api/logs/statistics/
      │       ├─→ /api/alerts/?status=triggered
      │       └─→ /api/sources/
      │
      ├─→ Logs Page
      │       │
      │       ├─→ /api/logs/ (with filters)
      │       └─→ /api/logs/{id}/
      │
      ├─→ Alerts Page
      │       │
      │       ├─→ /api/alerts/
      │       ├─→ POST acknowledge
      │       └─→ POST resolve
      │
      └─→ Rules Page
              │
              └─→ /api/rules/
```

---

## Technology Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | Django 4.2 |
| API | Django REST Framework |
| Database | SQLite3 |
| Parser | Regex + JSON |
| Server | Django Development Server |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | Streamlit |
| Charts | Plotly |
| Data Handling | Pandas |
| HTTP Client | Requests |

### Networking
| Feature | Implementation |
|---------|--------------|
| REST API | HTTP/JSON |
| Syslog | UDP:514 |
| CORS | django-cors-headers |

---

## Scalability Considerations

### Current Limitations
- **SQLite**: Limited for concurrent writes
- **Single process**: No distributed processing
- **In-memory anomaly baseline**: Lost on restart

### Production Upgrades

#### Database Migration
```
SQLite → PostgreSQL
├─ Better concurrent access
├─ Advanced indexing
├─ Partitioning support
└─ Connection pooling
```

#### Backend Scaling
```
Single Django → Multiple Instances
├─ Load balancer (Nginx/HAProxy)
├─ Task queue (Celery)
├─ Cache layer (Redis)
└─ Session management
```

#### Real-time Processing
```
Current → Stream Processing
├─ Apache Kafka (log broker)
├─ Apache Flink (stream processing)
├─ Real-time anomaly detection
└─ Instant alerting
```

#### Advanced Analytics
```
Simple Stats → Machine Learning
├─ Isolation Forest (anomaly detection)
├─ Time series forecasting
├─ Log clustering
└─ Root cause analysis
```

---

## Security Architecture

### Current State (Development)
```
❌ No authentication
❌ CORS enabled for all origins
❌ DEBUG mode enabled
❌ Hardcoded secret key
```

### Production Requirements
```
✅ JWT/OAuth2 authentication
✅ CORS restricted to known origins
✅ DEBUG=False
✅ Environment-based configuration
✅ HTTPS encryption
✅ Database encryption
✅ Log sanitization (remove PII)
✅ Role-based access control (RBAC)
✅ API rate limiting
✅ Request validation & sanitization
```

---

## Deployment Architecture

### Development (Current)
```
Laptop/VM
├─ Backend: manage.py runserver
├─ Frontend: streamlit run
└─ Database: sqlite3
```

### Production (Recommended)
```
Server Infrastructure
├─ Web Server (Nginx)
│   └─ Reverse Proxy
├─ Application Servers
│   ├─ Django (Gunicorn)
│   ├─ Django (Gunicorn)
│   └─ Django (Gunicorn)
├─ Task Queue (Celery)
├─ Cache (Redis)
├─ Database (PostgreSQL)
├─ Message Broker (RabbitMQ)
└─ Monitoring
    ├─ Prometheus
    ├─ Grafana
    └─ ELK Stack
```

---

## Performance Metrics

### Log Ingestion
- File parsing: ~5000 logs/second
- Database insert: ~1000 logs/second
- Anomaly detection: ~2000 calculations/second

### Query Performance
- Simple filters: < 100ms
- Complex filters: < 500ms
- Statistics calculation: < 1000ms
- Full-text search: < 500ms

### UI Response
- Page load: < 2 seconds
- Chart rendering: < 1 second
- Search: < 300ms

---

## Error Handling

### Log Ingestion
```
Invalid Format
     │
     └─→ Fallback to simple text parse
     
Database Error
     │
     └─→ Log error and skip entry
     
Anomaly Calc Error
     │
     └─→ Set is_anomaly=False, anomaly_score=0
```

### Alert Processing
```
Rule Evaluation Error
     │
     └─→ Log error, skip rule
     
Notification Failed
     │
     └─→ Mark as pending, retry later
     
Database Insert Error
     │
     └─→ Rollback, log error
```

---

## Monitoring Points

### Backend Metrics
- Request latency
- Error rates
- Database query time
- Anomaly detection time
- Alert trigger frequency

### Frontend Metrics
- Page load time
- API response time
- Chart rendering time
- User interactions

### Data Quality
- Log ingestion rate
- Parse error rate
- Anomaly detection accuracy
- False positive rate

---

## Integration Points

### External Systems
1. **Email Server** (SMTP)
   - Send alert notifications
   
2. **Log Sources**
   - File system
   - Syslog servers
   - Third-party APIs
   
3. **Monitoring Tools**
   - Prometheus (future)
   - Grafana (future)
   - DataDog (future)

---

## Database Schema

```sql
-- Core tables
CREATE TABLE logs (
    id BIGINT PRIMARY KEY,
    source_id INT,
    timestamp DATETIME INDEXED,
    level VARCHAR INDEXED,
    service VARCHAR INDEXED,
    message TEXT,
    metadata JSON,
    is_anomaly BOOL INDEXED,
    anomaly_score FLOAT,
    created_at DATETIME
);

CREATE TABLE alert_rules (
    id INT PRIMARY KEY,
    name VARCHAR,
    condition_type VARCHAR,
    threshold_value INT,
    enabled BOOL,
    created_at DATETIME
);

CREATE TABLE alerts (
    id INT PRIMARY KEY,
    rule_id INT,
    status VARCHAR INDEXED,
    triggered_at DATETIME INDEXED,
    acknowledged_at DATETIME,
    resolved_at DATETIME
);
```

---

**Last Updated:** January 2024
**Architecture Version:** 1.0
