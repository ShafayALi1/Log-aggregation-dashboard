# 📡 API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
Currently, no authentication is required. In production, implement JWT or token-based auth.

---

## Log Sources API

### List All Sources
```
GET /sources/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "production-api",
    "source_type": "syslog",
    "description": "Production API server logs",
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z",
    "log_count": 1250
  }
]
```

### Get Specific Source
```
GET /sources/{id}/
```

### Create New Source
```
POST /sources/
Content-Type: application/json

{
  "name": "new-service",
  "source_type": "api",
  "description": "New microservice logs"
}
```

**Response:** 201 Created

### Upload Log File
```
POST /sources/{id}/upload_logs/
Content-Type: multipart/form-data

file=@logs.txt
```

**Response:**
```json
{
  "message": "Successfully ingested 150 logs",
  "count": 150
}
```

---

## Logs API

### List Logs
```
GET /logs/?page=1&page_size=100
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Logs per page (default: 100)
- `service` (optional): Filter by service name
- `level` (optional): Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `is_anomaly` (optional): Filter anomalies (true/false)
- `search` (optional): Full-text search

**Example:**
```
GET /logs/?service=nginx-web&level=ERROR&page=1&page_size=50
```

**Response:**
```json
{
  "count": 1250,
  "page": 1,
  "page_size": 100,
  "results": [
    {
      "id": 1,
      "source": "production-api",
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "ERROR",
      "service": "api-gateway",
      "message": "Connection timeout after 30s",
      "metadata": {
        "endpoint": "/api/users",
        "response_time_ms": 30000
      },
      "is_anomaly": true,
      "anomaly_score": 3.2,
      "created_at": "2024-01-15T10:30:05Z"
    }
  ]
}
```

### Get Specific Log
```
GET /logs/{id}/
```

### Ingest Logs via API
```
POST /logs/ingest_api/
Content-Type: application/json

{
  "source": "api-source",
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "ERROR",
      "service": "payment-service",
      "message": "Payment processing timeout",
      "metadata": {
        "transaction_id": "TXN-123456",
        "amount": 99.99
      }
    },
    {
      "timestamp": "2024-01-15T10:31:00Z",
      "level": "WARNING",
      "service": "payment-service",
      "message": "Retry attempt 1/3"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Ingested 2 logs",
  "ingested_count": 2,
  "triggered_alerts": [
    {
      "id": 5,
      "rule": "Payment Service Errors",
      "message": "Alert triggered: Payment Service Errors"
    }
  ]
}
```

### Get Log Statistics
```
GET /logs/statistics/?hours=24
```

**Query Parameters:**
- `hours` (optional): Time range in hours (default: 24)

**Response:**
```json
{
  "total_logs": 5420,
  "by_level": {
    "DEBUG": 1200,
    "INFO": 2100,
    "WARNING": 800,
    "ERROR": 280,
    "CRITICAL": 40
  },
  "by_service": {
    "api-gateway": 2000,
    "nginx-web": 1500,
    "payment-service": 980,
    "database": 940
  },
  "anomalies_count": 15,
  "error_rate": 5.92
}
```

---

## Alert Rules API

### List All Rules
```
GET /rules/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Critical Errors",
    "description": "Alert on any CRITICAL level logs",
    "condition_type": "level_equals",
    "service_filter": "",
    "level_filter": "CRITICAL",
    "text_pattern": "",
    "threshold_value": 1,
    "threshold_window_minutes": 5,
    "enabled": true,
    "email_recipients": "admin@example.com,ops@example.com",
    "severity": "high",
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### Create Alert Rule
```
POST /rules/
Content-Type: application/json

{
  "name": "High Error Rate Alert",
  "description": "Alert when API service has >25% error rate",
  "condition_type": "error_rate",
  "service_filter": "api-gateway",
  "level_filter": "",
  "text_pattern": "",
  "threshold_value": 25,
  "threshold_window_minutes": 5,
  "enabled": true,
  "email_recipients": "team-lead@example.com",
  "severity": "high"
}
```

**Condition Types:**
- `contains`: Triggers if message contains text pattern
- `level_equals`: Triggers if log level matches
- `error_rate`: Triggers if error percentage exceeds threshold
- `frequency`: Triggers if error count exceeds threshold in time window

**Response:** 201 Created

### Get Specific Rule
```
GET /rules/{id}/
```

---

## Alerts API

### List Alerts
```
GET /alerts/?status=triggered
```

**Query Parameters:**
- `status` (optional): Filter by status (triggered, acknowledged, resolved)

**Response:**
```json
[
  {
    "id": 1,
    "rule": "High Error Rate Alert",
    "status": "triggered",
    "log_count": 45,
    "message": "Alert triggered: High Error Rate Alert",
    "details": {
      "error_rate": 32.5,
      "time_window": "5 minutes"
    },
    "triggered_at": "2024-01-15T10:30:00Z",
    "acknowledged_at": null,
    "resolved_at": null
  }
]
```

### Get Specific Alert
```
GET /alerts/{id}/
```

### Acknowledge Alert
```
POST /alerts/{id}/acknowledge/
```

**Response:**
```json
{
  "id": 1,
  "rule": "High Error Rate Alert",
  "status": "acknowledged",
  "log_count": 45,
  "message": "Alert triggered: High Error Rate Alert",
  "details": {},
  "triggered_at": "2024-01-15T10:30:00Z",
  "acknowledged_at": "2024-01-15T10:35:00Z",
  "resolved_at": null
}
```

### Resolve Alert
```
POST /alerts/{id}/resolve/
```

**Response:**
```json
{
  "id": 1,
  "rule": "High Error Rate Alert",
  "status": "resolved",
  "log_count": 45,
  "message": "Alert triggered: High Error Rate Alert",
  "details": {},
  "triggered_at": "2024-01-15T10:30:00Z",
  "acknowledged_at": "2024-01-15T10:35:00Z",
  "resolved_at": "2024-01-15T10:40:00Z"
}
```

---

## Error Responses

### Bad Request (400)
```json
{
  "error": "Missing required fields"
}
```

### Not Found (404)
```json
{
  "detail": "Not found."
}
```

### Internal Server Error (500)
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting & Pagination

- **Default page size:** 100 logs
- **Max page size:** 1000
- **Rate limit:** None (implement in production)

---

## Example Workflows

### Workflow 1: Upload and Analyze Logs
```bash
# 1. Create log source
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{"name": "web-server", "source_type": "file"}'

# 2. Upload log file
curl -X POST http://localhost:8000/api/sources/1/upload_logs/ \
  -F "file=@server.log"

# 3. Get statistics
curl http://localhost:8000/api/logs/statistics/?hours=24

# 4. Search for errors
curl 'http://localhost:8000/api/logs/?level=ERROR&service=web-server'
```

### Workflow 2: Create Alert and Monitor
```bash
# 1. Create alert rule
curl -X POST http://localhost:8000/api/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Errors",
    "condition_type": "error_rate",
    "service_filter": "api",
    "threshold_value": 10,
    "severity": "high",
    "email_recipients": "ops@company.com"
  }'

# 2. Ingest logs (will trigger if conditions met)
curl -X POST http://localhost:8000/api/logs/ingest_api/ \
  -H "Content-Type: application/json" \
  -d '{"source": "api", "logs": [...]}'

# 3. Check triggered alerts
curl http://localhost:8000/api/alerts/?status=triggered

# 4. Acknowledge alert
curl -X POST http://localhost:8000/api/alerts/1/acknowledge/

# 5. Resolve alert
curl -X POST http://localhost:8000/api/alerts/1/resolve/
```

---

## Testing with cURL

### Simple Test
```bash
# Check API availability
curl -X GET http://localhost:8000/api/logs/statistics/
```

### With jq for formatting
```bash
curl http://localhost:8000/api/logs/?page=1 | jq '.results[0]'
```

---

**Last Updated:** January 2024
**API Version:** 1.0
