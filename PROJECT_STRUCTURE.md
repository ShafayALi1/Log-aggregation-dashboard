# 📁 Project Structure

```
log-aggregation-dashboard/
│
├── 📄 README.md                          # Main documentation
├── 📄 SETUP_GUIDE.md                     # Step-by-step installation
├── 📄 .gitignore                         # Git ignore rules
│
├── 📁 backend/                           # Django REST Backend
│   ├── 📄 settings.py                    # Django configuration
│   ├── 📄 models.py                      # Database models (Log, LogSource, Alert, Rule)
│   ├── 📄 views.py                       # REST API viewsets & endpoints
│   ├── 📄 urls.py                        # URL routing
│   ├── 📄 log_ingestion.py               # Log parsing & ingestion service
│   ├── 📄 anomaly_detection.py           # Statistical anomaly detection
│   ├── 📄 requirements.txt                # Backend dependencies
│   └── 📁 venv/                          # Virtual environment (created during setup)
│
├── 📁 frontend/                          # Streamlit Dashboard
│   ├── 📄 dashboard.py                   # Main Streamlit application
│   ├── 📄 requirements.txt                # Frontend dependencies
│   └── 📁 venv/                          # Virtual environment (created during setup)
│
├── 📁 docs/                              # Documentation
│   ├── 📄 API.md                         # REST API documentation with examples
│   ├── 📄 ARCHITECTURE.md                # System architecture & design
│   └── 📄 ANOMALY_DETECTION.md           # Anomaly detection explanation
│
└── 📁 logs/                              # Sample log files
    ├── 📁 application/
    │   └── sample.log                    # Sample application logs
    ├── 📁 system/                        # For system logs
    └── 📁 security/                      # For security logs
```

## File Descriptions

### Root Files

| File | Purpose |
|------|---------|
| `README.md` | Complete project documentation, features, and usage |
| `SETUP_GUIDE.md` | Step-by-step installation and troubleshooting |
| `.gitignore` | Git ignore patterns |

### Backend Directory (`backend/`)

| File | Purpose | Lines |
|------|---------|-------|
| `settings.py` | Django configuration, database, logging, REST framework setup | 100+ |
| `models.py` | 5 core models: Log, LogSource, AlertRule, Alert, LogRetentionPolicy | 150+ |
| `views.py` | REST API viewsets for all resources with filtering, search, statistics | 300+ |
| `urls.py` | URL routing and API endpoints configuration | 20 |
| `log_ingestion.py` | Multi-format log parser and ingestion orchestration | 250+ |
| `anomaly_detection.py` | Statistical anomaly detection using Z-score analysis | 200+ |
| `requirements.txt` | Python package dependencies (Django, DRF, etc.) | 10 |

**Total Backend Code:** ~1100 lines

### Frontend Directory (`frontend/`)

| File | Purpose | Lines |
|------|---------|-------|
| `dashboard.py` | Complete Streamlit UI with 6 pages and real-time data visualization | 500+ |
| `requirements.txt` | Python dependencies (Streamlit, Plotly, Pandas) | 5 |

**Total Frontend Code:** ~500 lines

### Documentation (`docs/`)

| File | Purpose | Content |
|------|---------|---------|
| `API.md` | Complete API reference with all endpoints and examples | All GET/POST operations, error responses, workflows |
| `ARCHITECTURE.md` | System design, data flows, scalability, deployment | 3-tier architecture, component design, security |
| `ANOMALY_DETECTION.md` | Detailed explanation of anomaly detection algorithm | Z-score analysis, implementation, examples, tuning |

**Total Documentation:** ~2000+ lines

## Key Components Overview

### Models (Database)

```python
Log
├─ Timestamp-based indexing for fast queries
├─ Anomaly detection scores
└─ Flexible metadata JSON field

LogSource
├─ File, Syslog, or API sources
└─ Active/inactive status

AlertRule
├─ Multiple condition types (contains, level, rate, frequency)
├─ Email notification recipients
└─ Severity levels

Alert
├─ Tracking triggered/acknowledged/resolved states
├─ Timestamps for SLA tracking
└─ Alert details and logs count

LogRetentionPolicy
├─ Service-pattern matching
├─ Configurable retention periods
└─ Cleanup tracking
```

### API Endpoints

```
/api/sources/                 - Log source management
/api/logs/                   - Log querying and filtering
/api/logs/ingest_api/        - API-based log ingestion
/api/logs/statistics/        - Real-time log statistics
/api/rules/                  - Alert rule management
/api/alerts/                 - Alert lifecycle management
```

### Frontend Pages

```
Dashboard                    - Real-time metrics and alerts
Logs                        - Search and filter logs
Alerts                      - Alert management
Rules                       - Create/configure alert rules
Upload Logs                 - File-based ingestion
Settings                    - Configuration
```

## Dependencies

### Backend (Django Stack)
- Django 4.2.7 - Web framework
- djangorestframework 3.14.0 - REST API
- django-cors-headers 4.3.1 - CORS support
- django-filter 23.4 - Advanced filtering
- Pillow 10.0.1 - Image processing
- python-dateutil 2.8.2 - Date utilities
- requests 2.31.0 - HTTP client

### Frontend (Streamlit Stack)
- streamlit 1.28.1 - Web UI framework
- pandas 2.1.3 - Data manipulation
- plotly 5.17.0 - Interactive charts
- requests 2.31.0 - HTTP client
- python-dateutil 2.8.2 - Date utilities

## Code Statistics

| Metric | Count |
|--------|-------|
| Total Python files | 8 |
| Total lines of code | ~1600 |
| Total documentation | ~2000 |
| Database models | 5 |
| API endpoints | 15+ |
| Dashboard pages | 6 |
| Supported log formats | 5+ |
| Alert condition types | 4 |
| Anomaly detection methods | 3 |

## Getting Started

1. **Read:** `README.md` (5 min) - Overview
2. **Setup:** `SETUP_GUIDE.md` (15 min) - Installation
3. **Explore:** Start frontend, upload sample logs
4. **Reference:** `docs/API.md` - API usage
5. **Learn:** `docs/ARCHITECTURE.md` - System design
6. **Deep Dive:** `docs/ANOMALY_DETECTION.md` - Detection algorithm

## Project Size

- **Total Files:** 15+
- **Total Lines:** ~5600 (code + docs)
- **Download Size:** ~2MB (uncompressed)
- **Installation Size:** ~300MB (with dependencies)
- **Runtime Memory:** ~500MB (backend + frontend)

## Development Notes

### Backend Architecture
- **Pattern:** Django REST Framework (DRF) ViewSets
- **Database:** SQLite with proper indexing
- **Services:** Modular ingestion and detection
- **Scalability:** Ready for PostgreSQL + Celery

### Frontend Architecture
- **Framework:** Streamlit (rapid UI development)
- **State:** Session-based state management
- **Charts:** Plotly for interactive visualizations
- **API:** Synchronous requests to Django backend

## Quality Metrics

- ✅ **Code Organization:** Modular, separated concerns
- ✅ **Documentation:** Comprehensive with examples
- ✅ **Error Handling:** Graceful degradation
- ✅ **Performance:** Indexed queries, batch operations
- ✅ **Scalability:** Production-ready upgrades documented
- ✅ **Testing:** Includes test data and workflows

## Production Readiness

### Current State (Development)
- ✓ SQLite database
- ✓ Django development server
- ✓ No authentication
- ✓ DEBUG mode enabled

### Production Upgrade Path
- ⚠️ Migrate to PostgreSQL
- ⚠️ Use Gunicorn + Nginx
- ⚠️ Implement JWT authentication
- ⚠️ Enable HTTPS
- ⚠️ Add Redis caching
- ⚠️ Deploy with Docker

## Learning Value

This project is excellent for learning:
- ✓ Django & REST Framework
- ✓ Statistical data analysis
- ✓ Real-time monitoring systems
- ✓ Database design & indexing
- ✓ API design & documentation
- ✓ Frontend-backend integration
- ✓ System architecture
- ✓ DevOps concepts

---

**Created:** January 2024
**Version:** 1.0
**License:** Educational - Free to use and modify
