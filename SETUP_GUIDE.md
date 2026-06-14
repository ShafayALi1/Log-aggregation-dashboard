# 🚀 Complete Setup Guide

## System Requirements

- **Python:** 3.8 or higher
- **RAM:** 2GB minimum
- **Storage:** 500MB for project + dependencies
- **OS:** Windows, macOS, or Linux
- **Internet:** For pip package installation

## Step-by-Step Installation

### Step 1: Download and Extract Project

```bash
# Extract the zip file
# You should have the following structure:
# log-aggregation-dashboard/
#   ├── backend/
#   ├── frontend/
#   ├── docs/
#   ├── logs/
#   └── README.md

cd log-aggregation-dashboard
```

### Step 2: Backend Setup

#### 2a. Create Backend Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

#### 2b. Install Backend Dependencies

```bash
# Ensure you're in backend directory with venv activated
pip install -r requirements.txt

# Verify installation
pip list
```

#### 2c. Create Django Project Structure

Since this is a simplified setup, create the necessary Django files:

**Create `core/__init__.py`:**
```python
# Empty file
```

**Create `core/wsgi.py`:**
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
application = get_wsgi_application()
```

**Create `manage.py`:**
```python
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
```

#### 2d. Create Django Apps

```bash
# Create app directories
mkdir -p logs alerts
touch logs/__init__.py
touch alerts/__init__.py
```

**Create `logs/apps.py`:**
```python
from django.apps import AppConfig

class LogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logs'
```

**Create `logs/admin.py`:**
```python
from django.contrib import admin
from .models import Log, LogSource

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'level', 'service', 'is_anomaly']
    list_filter = ['level', 'service', 'is_anomaly']
    search_fields = ['message', 'service']

@admin.register(LogSource)
class LogSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'is_active']
```

**Create `alerts/apps.py`:**
```python
from django.apps import AppConfig

class AlertsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alerts'
```

#### 2e. Initialize Database

```bash
# Create migrations
python manage.py makemigrations logs alerts

# Apply migrations
python manage.py migrate

# Create superuser (optional)
# python manage.py createsuperuser
# Follow prompts

# Output should show:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, logs, alerts
# Running migrations:
#   ...
#   OK
```

#### 2f. Start Backend Server

```bash
# In backend directory with venv activated
python manage.py runserver 0.0.0.0:8000

# Expected output:
# Starting development server at http://0.0.0.0:8000/
# Quit the server with CONTROL-C.
```

**✓ Backend is running!** Access API at `http://localhost:8000/api/`

### Step 3: Frontend Setup

**Open a new terminal window** (keep backend running in first window)

#### 3a. Create Frontend Virtual Environment

```bash
# Navigate to frontend directory
cd frontend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 3b. Install Frontend Dependencies

```bash
# Install dependencies
pip install -r requirements.txt

# Verify
pip list | grep streamlit
```

#### 3c. Start Frontend

```bash
# In frontend directory with venv activated
streamlit run dashboard.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
# Network URL: http://192.168.x.x:8501
```

**✓ Frontend is running!** Open `http://localhost:8501` in your browser

---

## Post-Installation Steps

### 1. Create Sample Log Source

In Streamlit Dashboard (Settings page):
- Note: Log sources will auto-create on first use

Or via API:
```bash
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{"name": "sample-logs", "source_type": "file", "description": "Sample log source"}'
```

### 2. Test with Sample Logs

**Create a test log file `test.log`:**
```
[2024-01-15T10:30:00Z] [INFO] [web-server] Server started
[2024-01-15T10:31:00Z] [INFO] [web-server] Request from 192.168.1.1
[2024-01-15T10:32:00Z] [WARNING] [web-server] High memory usage: 85%
[2024-01-15T10:33:00Z] [ERROR] [web-server] Connection timeout
[2024-01-15T10:34:00Z] [ERROR] [web-server] Connection timeout
[2024-01-15T10:35:00Z] [CRITICAL] [web-server] Service crashed
```

**Upload via Dashboard:**
1. Go to "Upload Logs" section
2. Select "sample-logs" source
3. Upload `test.log`
4. See logs appear in "Log Search" section

### 3. Create Sample Alert Rule

1. Navigate to "Rules" → "Create Rule"
2. Create rule:
   ```
   Name: Test Alert
   Condition: level_equals
   Level: ERROR
   Severity: medium
   Email: your-email@example.com
   ```
3. Create alert rule

### 4. Test Alert Triggering

Send test logs via API:
```bash
curl -X POST http://localhost:8000/api/logs/ingest_api/ \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test-api",
    "logs": [
      {"level": "ERROR", "service": "test-service", "message": "Test error"},
      {"level": "ERROR", "service": "test-service", "message": "Test error 2"}
    ]
  }'
```

Check "Alerts" page - should show triggered alert!

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution:**
```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Then install requirements
pip install -r requirements.txt
```

### Issue: "Address already in use" on port 8000

**Solution:**
```bash
# Use different port
python manage.py runserver 8001

# Or kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### Issue: "Address already in use" on port 8501

**Solution:**
```bash
# Use different port
streamlit run dashboard.py --server.port 8502
```

### Issue: Frontend can't connect to backend

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/api/logs/`
2. Check API_BASE_URL in `frontend/dashboard.py` matches backend URL
3. Check CORS is enabled in backend (it should be by default)

### Issue: Database errors

**Solution:**
```bash
# Reset database (DELETES ALL DATA)
rm db.sqlite3

# Recreate database
python manage.py migrate

# Create superuser again
python manage.py createsuperuser
```

### Issue: Large file upload fails

**Solution:**
- Upload files in smaller chunks
- Max default: ~100MB (configurable in Django settings)
- For larger files, use syslog integration

---

## Project Navigation

### Backend Endpoints

```
http://localhost:8000/
├── /api/
│   ├── /sources/              - Log sources
│   ├── /logs/                 - Log queries
│   ├── /logs/ingest_api/      - API ingestion
│   ├── /logs/statistics/      - Statistics
│   ├── /rules/                - Alert rules
│   └── /alerts/               - Alert management
├── /admin/                    - Django admin
└── /api-auth/                 - Auth endpoints
```

### Frontend Pages

```
http://localhost:8501/
├── Dashboard                  - Overview & active alerts
├── Logs                       - Search & filter logs
├── Alerts                     - Alert management
├── Rules                      - Create alert rules
├── Upload Logs                - File upload
└── Settings                   - Configuration
```

---

## Development Workflow

### Day-to-Day Usage

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
source venv/bin/activate  # or venv\Scripts\activate on Windows
streamlit run dashboard.py

# Open browser to http://localhost:8501
```

### Making Changes

**Backend Changes:**
1. Edit Python files (models.py, views.py, etc.)
2. If model changes: `python manage.py makemigrations`
3. `python manage.py migrate`
4. Restart server (Ctrl+C, then run again)

**Frontend Changes:**
1. Edit `frontend/dashboard.py`
2. Streamlit auto-reloads on save
3. Refresh browser or click "Rerun" button

---

## Production Deployment

### Before Deploying

1. **Security:**
   ```python
   # settings.py
   DEBUG = False
   SECRET_KEY = os.environ.get('SECRET_KEY')
   ALLOWED_HOSTS = ['yourdomain.com']
   SECURE_SSL_REDIRECT = True
   ```

2. **Database:**
   ```bash
   # Migrate to PostgreSQL
   pip install psycopg2
   # Update DATABASES in settings.py
   ```

3. **Testing:**
   ```bash
   # Run tests
   python manage.py test
   ```

### Deployment Options

**Option 1: Heroku**
```bash
# Add Procfile
web: gunicorn core.wsgi

# Deploy
git push heroku main
```

**Option 2: DigitalOcean / AWS**
```bash
# Use Docker
docker build -t log-aggregation .
docker run -p 8000:8000 log-aggregation
```

**Option 3: Traditional Server**
```bash
# Use Gunicorn + Nginx
gunicorn core.wsgi -b 0.0.0.0:8000
# Configure Nginx as reverse proxy
```

---

## Testing the System

### 1. Test File Upload

```bash
# Create sample log
echo "[2024-01-15T10:30:00Z] [ERROR] [test] Error message" > test.log

# Upload via API
curl -F "file=@test.log" \
  http://localhost:8000/api/sources/1/upload_logs/
```

### 2. Test API Ingestion

```bash
curl -X POST http://localhost:8000/api/logs/ingest_api/ \
  -H "Content-Type: application/json" \
  -d '{
    "source": "api-test",
    "logs": [
      {
        "timestamp": "2024-01-15T10:30:00Z",
        "level": "ERROR",
        "service": "test",
        "message": "Test error"
      }
    ]
  }'
```

### 3. Test Anomaly Detection

```bash
# Send burst of errors
for i in {1..20}; do
  curl -X POST http://localhost:8000/api/logs/ingest_api/ \
    -H "Content-Type: application/json" \
    -d '{"source":"test","logs":[{"level":"ERROR","service":"api","message":"Error"}]}'
done

# Check detected anomalies
curl http://localhost:8000/api/logs/?is_anomaly=true
```

---

## Useful Commands

```bash
# View database contents (Django shell)
python manage.py shell
>>> from logs.models import Log
>>> Log.objects.all().count()
>>> Log.objects.filter(is_anomaly=True).count()

# Reset everything
python manage.py flush  # Delete all data, keep structure
python manage.py migrate --fake zero  # Undo migrations
python manage.py migrate  # Redo migrations

# Get detailed API response
curl -X GET http://localhost:8000/api/logs/ -s | python -m json.tool

# Monitor backend
python manage.py runserver --debug

# Check Django settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASE_URL)
```

---

## Performance Tuning

### Database Optimization

```python
# Add indexes in models
class Log(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['timestamp', 'level']),
            models.Index(fields=['service', 'timestamp']),
        ]
```

### Batch Insertions

```python
# Instead of
for log in logs:
    Log.objects.create(**log)

# Use
Log.objects.bulk_create(log_objects)
```

### Query Optimization

```python
# Use select_related for foreign keys
logs = Log.objects.select_related('source').all()

# Use prefetch_related for reverse relations
sources = LogSource.objects.prefetch_related('logs').all()
```

---

## Next Steps

1. **Explore the Dashboard**
   - Navigate through all pages
   - Upload sample logs
   - Create alert rules
   - Monitor alerts

2. **Read Documentation**
   - [API Documentation](../docs/API.md)
   - [System Architecture](../docs/ARCHITECTURE.md)
   - [Anomaly Detection](../docs/ANOMALY_DETECTION.md)

3. **Customize**
   - Modify alert rules
   - Adjust anomaly thresholds
   - Add custom log sources
   - Integrate with your systems

4. **Scale Up**
   - Migrate to PostgreSQL
   - Add caching layer (Redis)
   - Implement authentication
   - Deploy to production

---

## Support

### Getting Help

- Check [README.md](../README.md) for overview
- Review [API Documentation](../docs/API.md) for endpoint details
- Check logs for error messages:
  ```bash
  tail -f logs/django.log  # Backend logs
  ```

### Debugging Tips

```bash
# Enable verbose logging
export DJANGO_LOG_LEVEL=DEBUG
python manage.py runserver

# Check database queries
python manage.py shell
>>> import django
>>> from django.conf import settings
>>> settings.DEBUG_PROPAGATE_EXCEPTIONS = True

# Monitor in real-time
watch -n 1 'curl -s http://localhost:8000/api/logs/statistics/ | python -m json.tool'
```

---

**Setup Complete!** 🎉

You're now ready to use the Log Aggregation Dashboard. Start with the Dashboard page and explore the features.

**Last Updated:** January 2024
