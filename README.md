#  Log Aggregation & Analysis Dashboard

A comprehensive log management system built with Django backend and Streamlit frontend. Designed for real-time log ingestion, analysis, and anomaly detection.

## for Superusercreation
## docker-compose exec backend python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" 

## important steps notes made by me
## Running with Docker

## Start the application:

 ## docker-compose up


## Access:
## - Dashboard: http://localhost:8501
## - Backend API: http://localhost:8000/api/
## - Django Admin: http://localhost:8000/admin/

## for suoer user
## docker-compose exec backend python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

## For logs sample
## docker-compose exec backend python manage.py shell -c "from logs.models import LogSource; LogSource.objects.create(name='my-logs', source_type='file', description='Sample log source')"





## features
### Core Functionality
- **Multi-source Log Ingestion**
  - File upload support
  - Syslog protocol integration
  - REST API endpoints
  - Automatic log parsing (JSON, standard, Apache, Nginx formats)

- **Real-time Log Analysis**
  - Full-text search across logs
  - Filter by service, level, timestamp
  - Anomaly detection using statistical analysis
  - Error rate tracking

- **Alert Management**
  - Customizable alert rules
  - Multiple trigger conditions
  - Email notification support
  - Alert acknowledgment and resolution tracking

- **Dashboard & Visualization**
  - Real-time statistics
  - Service-wise log distribution
  - Error rate visualization
  - Anomaly trend analysis

- **Log Retention Policies**
  - Automatic cleanup of old logs
  - Configurable retention periods
  - Service-level policies

## 🏗️ Project Structure

```
log-aggregation-dashboard/
├── backend/                    # Django backend
│   ├── settings.py            # Django configuration
│   ├── models.py              # Database models
│   ├── views.py               # REST API views
│   ├── urls.py                # URL routing
│   ├── anomaly_detection.py   # Anomaly detection service
│   ├── log_ingestion.py       # Log parsing & ingestion
│   └── requirements.txt        # Backend dependencies
├── frontend/                   # Streamlit frontend
│   ├── dashboard.py           # Main dashboard application
│   └── requirements.txt        # Frontend dependencies
├── logs/                       # Sample log directories
│   ├── application/
│   ├── system/
│   └── security/
├── docs/                       # Documentation
│   ├── API.md                 # API documentation
│   ├── ARCHITECTURE.md        # System architecture
│   └── ANOMALY_DETECTION.md  # Anomaly detection details
├── manage.py                   # Django management script
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- SQLite3 (included with Python)

### Installation

#### 1. Clone and Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser

# Start backend server
python manage.py runserver 0.0.0.0:8000
```

#### 2. Setup Frontend

```bash
# Open new terminal window
# Navigate to frontend directory
cd frontend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Streamlit app
streamlit run dashboard.py
```

The dashboard will be available at `http://localhost:8501`

## 📡 API Endpoints

### Log Sources
- `GET /api/sources/` - List all log sources
- `POST /api/sources/` - Create new log source
- `POST /api/sources/{id}/upload_logs/` - Upload log file

### Logs
- `GET /api/logs/` - List logs with filters
- `GET /api/logs/{id}/` - Get specific log
- `POST /api/logs/ingest_api/` - Ingest logs via API
- `GET /api/logs/statistics/` - Get log statistics

### Alert Rules
- `GET /api/rules/` - List alert rules
- `POST /api/rules/` - Create alert rule
- `GET /api/rules/{id}/` - Get specific rule

### Alerts
- `GET /api/alerts/` - List alerts
- `POST /api/alerts/{id}/acknowledge/` - Acknowledge alert
- `POST /api/alerts/{id}/resolve/` - Resolve alert

## 🔍 Log Ingestion

### File Upload
1. Navigate to "Upload Logs" section in dashboard
2. Select log source
3. Upload log file
4. System automatically parses and ingests logs

### API Ingestion
```bash
curl -X POST http://localhost:8000/api/logs/ingest_api/ \
  -H "Content-Type: application/json" \
  -d '{
    "source": "api-source",
    "logs": [
      {
        "timestamp": "2024-01-15T10:30:00Z",
        "level": "ERROR",
        "service": "api-gateway",
        "message": "Connection timeout",
        "metadata": {"user_id": 123}
      }
    ]
  }'
```

### Syslog Integration
Configure your syslog client to forward logs:
```
# /etc/rsyslog.d/forward.conf
*.* @@localhost:514
```

## 🤖 Anomaly Detection

### How It Works
- Analyzes historical error patterns for each service
- Calculates baseline mean and standard deviation
- Uses Z-score to identify statistical anomalies
- Configurable threshold (default: 2.5 standard deviations)

### Detection Methods

1. **Error Rate Anomaly Detection**
   - Detects unusual spikes in error frequency
   - Compares recent error count to historical baseline

2. **Error Rate Spike Detection**
   - Identifies significant percentage increases in error rate
   - Useful for detecting service degradation

3. **Service Silence Detection**
   - Alerts when a service stops sending logs
   - Configurable timeout period

## ⚠️ Alert Rules

### Rule Types

#### 1. Contains Text Pattern
Triggers when log message contains specific text
```
Rule: "Database Connection Lost"
Condition: Contains "Connection refused"
```

#### 2. Log Level Equals
Triggers when log level matches condition
```
Rule: "Critical Errors"
Condition: Level equals CRITICAL
```

#### 3. Error Rate Exceeds
Triggers when error percentage exceeds threshold
```
Rule: "High Error Rate"
Condition: Error rate > 25% for service "api-gateway"
```

#### 4. Frequency Exceeds
Triggers when error count exceeds threshold in time window
```
Rule: "Error Frequency"
Condition: 10 or more errors in 5 minutes
```

## 📊 Dashboard Sections

### Dashboard Overview
- Real-time statistics (total logs, anomalies, error rate)
- Log distribution by severity level
- Service-wise log counts
- Active alerts widget

### Log Search
- Full-text search across logs
- Filter by service, level, timestamp
- Detailed log inspection
- Metadata viewing

### Alerts
- View triggered/acknowledged/resolved alerts
- Acknowledge and resolve alerts
- Alert timeline

### Rules Management
- View existing alert rules
- Create new rules with custom conditions
- Enable/disable rules

### Log Upload
- File-based log ingestion
- Support for multiple log formats
- Real-time parsing and storage

## 🔧 Configuration

### Django Settings
Edit `backend/settings.py`:
```python
# Log retention (days)
LOG_RETENTION_DAYS = 30

# Anomaly detection threshold (standard deviations)
ANOMALY_THRESHOLD = 2.5

# Database (default: SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
```

### Log Retention Policy
Create policies via Django admin:
1. Navigate to `/admin/`
2. Add retention policies
3. Specify service pattern and retention days

## 📈 Performance Considerations

- **Indexing**: Logs are indexed by timestamp, level, service for fast queries
- **Pagination**: API returns 100 logs per page
- **Caching**: Statistics are calculated on-demand
- **Database**: SQLite suitable for < 1 million logs; use PostgreSQL for production

## 🔒 Security Notes

- ⚠️ Change `SECRET_KEY` in production
- ⚠️ Set `DEBUG = False` in production
- ⚠️ Use environment variables for sensitive data
- ⚠️ Implement authentication on API endpoints
- ⚠️ Enable HTTPS for log transmission

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check migrations
python manage.py showmigrations

# Reset database (development only)
rm db.sqlite3
python manage.py migrate
```

### Frontend can't connect to backend
```bash
# Verify backend is running on port 8000
curl http://localhost:8000/api/logs/

# Check API_BASE_URL in dashboard.py
```

### Large log files slow down ingestion
- Use the syslog integration for real-time streaming
- Upload files in smaller chunks
- Consider using PostgreSQL for production

## 📝 Example Log Formats

### JSON Format
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "ERROR",
  "service": "payment-service",
  "message": "Payment processing failed",
  "metadata": {"order_id": "ORD-123"}
}
```

### Standard Format
```
[2024-01-15T10:30:00Z] [ERROR] [payment-service] Payment processing failed
```

### Syslog Format
```
Jan 15 10:30:00 server payment-service: Payment processing failed
```

## 🧪 Testing

### Test Log Ingestion
```bash
# Create test log file
echo "[2024-01-15T10:30:00Z] [ERROR] [test-service] Test error message" > test.log

# Upload via API
curl -F "file=@test.log" http://localhost:8000/api/sources/1/upload_logs/
```

### Test API Endpoint
```bash
# Ingest test logs
curl -X POST http://localhost:8000/api/logs/ingest_api/ \
  -H "Content-Type: application/json" \
  -d '{"source": "test", "logs": [{"level": "INFO", "service": "test", "message": "test"}]}'
```

## 📚 Additional Resources

- [API Documentation](docs/API.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Anomaly Detection Details](docs/ANOMALY_DETECTION.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- PostgreSQL integration
- Elasticsearch backend
- Machine learning anomaly detection
- Real-time WebSocket support
- Email notifications
- User authentication

## 📄 License

This project is provided as-is for educational purposes.

## 👨‍💻 Author

Built for 7th Semester Final Project - Log Aggregation & Analysis System

---

**Last Updated:** January 2024
**Version:** 1.0.0
