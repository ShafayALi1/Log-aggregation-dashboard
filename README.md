# 📊 Log Aggregation & Analysis Dashboard

A log management system built with a **Django REST API** backend and a **Streamlit** dashboard frontend. It supports log ingestion, search and filtering, statistical anomaly detection, configurable alert rules, and visual analytics — fully containerized with Docker.

---

## ✨ Features

- **Log Ingestion** — upload `.log`/`.txt` files through the dashboard or via the REST API
- **Search & Filtering** — filter logs by level (INFO/WARNING/ERROR/CRITICAL), service, keyword, and anomaly status
- **Anomaly Detection** — statistical (Z-score based) detection of unusual log patterns per service
- **Alert Rules & Alerts** — define rules (e.g. trigger on ERROR logs), view and manage active alerts (acknowledge/resolve)
- **Dashboard Visualizations**
  - Log distribution by severity (pie chart)
  - Logs by service (bar chart)
  - Log volume over time (line chart)
  - Top error messages (horizontal bar chart)
  - Anomaly trend over time (area chart)
- **Dockerized** — one command (`docker-compose up`) runs both backend and frontend
- **CI Pipeline** — GitHub Actions workflow validates Django checks, migrations, and Docker builds

---

## 🏗️ Architecture

```
┌─────────────────────────┐
│   Streamlit Frontend     │  → http://localhost:8501
│   (frontend/dashboard.py)│
└───────────┬──────────────┘
            │ REST API (HTTP)
┌───────────▼──────────────┐
│   Django REST Backend     │  → http://localhost:8000/api/
│   (backend/)               │
│   - Log ingestion          │
│   - Anomaly detection       │
│   - Alert processing        │
└───────────┬──────────────┘
            │
┌───────────▼──────────────┐
│   SQLite Database          │
└─────────────────────────┘
```

---

## 🚀 Getting Started (Docker — Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Start the application

```bash
docker-compose up --build
```

This builds and starts both containers:
- Backend (Django) → `http://localhost:8000`
- Frontend (Streamlit) → `http://localhost:8501`

### 2. Create a superuser (one-time)

```bash
docker-compose exec backend python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
```

Login at `http://localhost:8000/admin/` with:
- **Username:** `admin`
- **Password:** `admin123`

### 3. Create a log source (one-time)

A log source must exist before you can upload logs.

```bash
docker-compose exec backend python manage.py shell -c "from logs.models import LogSource; LogSource.objects.create(name='my-logs', source_type='file', description='Sample log source')"
```

### 4. Upload logs

Go to `http://localhost:8501` → **Upload Logs**, select the source, and upload a `.log`/`.txt` file.

### 5. Explore

- **Dashboard** — overview stats & charts (set Time Range to "All Time" to see all uploaded logs)
- **Logs** — search and filter
- **Rules** — create alert rules
- **Alerts** — view, acknowledge, or resolve triggered alerts

---

## 🛑 Stopping the Application

```bash
docker-compose down
```

Data (database, superuser, logs, alerts) **persists** across restarts via a named Docker volume (`db_data`).

To completely reset all data:

```bash
docker-compose down -v
```

---

## 📝 Sample Log Format

```
[2024-01-15T10:30:00Z] [INFO] [web-server] Server started successfully
[2024-01-15T10:31:00Z] [WARNING] [web-server] High memory usage: 85%
[2024-01-15T10:32:00Z] [ERROR] [web-server] Connection timeout on port 8080
[2024-01-15T10:33:00Z] [CRITICAL] [auth-service] Too many failed login attempts
```

---

## 🔧 Running Without Docker (Manual Setup)

<details>
<summary>Click to expand manual setup instructions</summary>

### Backend

```bash
cd backend
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend (in a separate terminal)

```bash
cd frontend
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
streamlit run dashboard.py
```

</details>

---

## 📁 Project Structure

```
log-aggregation-dashboard/
├── backend/                  # Django REST backend
│   ├── settings.py
│   ├── views.py
│   ├── urls.py
│   ├── log_ingestion.py      # Log parsing
│   ├── anomaly_detection.py  # Z-score anomaly detection
│   ├── logs/                 # Django app: models, migrations
│   ├── alerts/               # Django app
│   ├── core/                 # Project config (urls, wsgi)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                  # Streamlit dashboard
│   ├── dashboard.py
│   ├── Dockerfile
│   └── requirements.txt
├── docs/                       # Architecture & API docs
├── .github/workflows/ci.yml   # CI pipeline
├── docker-compose.yml
└── README.md
```

---

## 🧪 CI/CD

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR to `main`:
- Django system checks & migration checks
- Frontend compile check
- Docker image builds for both services

---

## 📚 Additional Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture details
- [`docs/API.md`](docs/API.md) — REST API reference
- [`docs/ANOMALY_DETECTION.md`](docs/ANOMALY_DETECTION.md) — anomaly detection methodology
