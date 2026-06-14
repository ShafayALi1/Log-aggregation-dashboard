# 🤖 Anomaly Detection System

## Overview

The anomaly detection system uses **statistical methods** to identify unusual patterns in log data. It operates on the principle that deviations from historical patterns indicate potential problems.

## Core Concept: Z-Score Analysis

### What is a Z-Score?

A Z-score measures how many standard deviations a data point is from the mean:

```
Z = (X - μ) / σ

Where:
  X  = Current value (recent error count)
  μ  = Mean (average historical error count)
  σ  = Standard Deviation (variability)
```

### Interpretation

```
Z-Score  │ Interpretation
─────────┼──────────────────────────────────────
  < 0    │ Below average (fewer errors)
  0      │ Exactly average
  +1.0   │ 1 std dev above average
  +2.5   │ 2.5 std dev above average (Anomaly!)
  +3.5   │ 3.5 std dev above (Critical!)
  > +4   │ Extremely rare event
```

### Why Z-Score Works

```
Normal Distribution (Bell Curve)

           │
           │    ╱╲
           │   ╱  ╲
           │  ╱    ╲
       ┌───┼─────────┐
       │   │         │
     68%  │  Z=±1
     95%  │  Z=±2
     99.7%│  Z=±3
       └───┼─────────┘
           │
     Normal  Anomalous
     Region  Region
```

---

## Implementation Details

### 1. Baseline Calculation

The system builds a **24-hour rolling baseline** for each service:

```python
# Get past 24 hours of logs
past_24h = timezone.now() - timedelta(hours=24)

# Count errors per hour
hourly_errors = {
    "hour_1": 5,
    "hour_2": 8,
    "hour_3": 4,
    "hour_4": 9,
    ...
}

# Calculate statistics
mean = statistics.mean(hourly_errors)        # e.g., 6.5
std_dev = statistics.stdev(hourly_errors)    # e.g., 2.1
```

### 2. Real-time Detection

For incoming logs:

```python
# Count recent errors (last 5 minutes)
recent_errors = 25

# Get baseline stats
baseline_mean = 6.5
baseline_std = 2.1

# Calculate Z-score
z_score = (25 - 6.5) / 2.1 = 8.8

# Evaluate
if abs(z_score) > THRESHOLD (2.5):
    is_anomaly = True
```

### 3. Severity Calculation

```python
def calculate_severity(z_score):
    abs_z = abs(z_score)
    
    if abs_z > 3.5:
        return "critical"     # Extremely rare
    elif abs_z > 3.0:
        return "high"         # Very unusual
    elif abs_z > 2.5:
        return "medium"       # Unusual
    else:
        return "low"          # Normal
```

---

## Detection Methods

### Method 1: Error Rate Anomaly

**What it detects:** Unusual spikes in error frequency

**How it works:**
```
Step 1: Get last 24 hours of errors
        [5, 6, 4, 7, 5, 6, 8, 5, ...]

Step 2: Calculate baseline
        Mean = 6 errors/hour
        StdDev = 1.5 errors/hour

Step 3: Count recent errors (last 5 min)
        Recent = 25 errors

Step 4: Calculate Z-score
        Z = (25 - 6) / 1.5 = 12.67 ← ANOMALY!

Step 5: Trigger alert
        Alert severity = CRITICAL
        Reason = "Error rate spike detected"
```

**Configuration:**
```python
detector = AnomalyDetector(
    threshold_std=2.5,      # Number of std devs
    window_hours=24         # Baseline period
)
```

**Example Alert:**
```
Service: api-gateway
Current errors: 25 (in 5 minutes)
Expected: 6.5 (average)
Z-score: 2.8 (28x normal)
Status: ANOMALY DETECTED ⚠️
```

### Method 2: Error Rate Spike Detection

**What it detects:** Significant percentage increase in errors

**How it works:**
```
Hour 1-2 (Baseline):
  Errors: 10
  Total logs: 200
  Error rate: 5%

Hour 2-3 (Current):
  Errors: 45
  Total logs: 150
  Error rate: 30%

Increase: (45-10)/10 × 100 = 350%
Threshold: 50%

Trigger: YES (350% > 50%)
```

**Parameters:**
```python
detector.detect_error_rate_spike(
    logs=query_set,
    service_name="api-gateway",
    threshold_percentage=50  # 50% increase
)
```

### Method 3: Service Silence Detection

**What it detects:** Services that stopped sending logs

**How it works:**
```
Monitor: api-gateway service

Last log: 10:30 AM
Current time: 11:15 AM
Silent duration: 45 minutes

Threshold: 30 minutes silence

Trigger: YES (45 > 30)
Alert: Service may have crashed!
```

**Parameters:**
```python
detector.detect_service_silence(
    logs=query_set,
    service_name="api-gateway",
    silence_minutes=30
)
```

---

## Configuration

### Adjusting Sensitivity

#### More Sensitive (More alerts)
```python
# Lower threshold → More anomalies detected
detector = AnomalyDetector(threshold_std=1.5)

# Result: Detects subtle deviations
# Risk: False positives increase
```

#### Less Sensitive (Fewer alerts)
```python
# Higher threshold → Only extreme anomalies
detector = AnomalyDetector(threshold_std=3.5)

# Result: Only critical issues
# Risk: Might miss important problems
```

#### Optimal Balance (Default)
```python
# Sweet spot: 2.5 standard deviations
detector = AnomalyDetector(threshold_std=2.5)

# Result: ~0.6% false positive rate
# Catches: 99% of real problems
```

### Baseline Window

```python
# Short baseline: Adapts quickly to changes
detector = AnomalyDetector(window_hours=4)

# Long baseline: Stable but slow to adapt
detector = AnomalyDetector(window_hours=72)

# Default: Balanced
detector = AnomalyDetector(window_hours=24)
```

---

## Anomaly Scoring

Each log is assigned an **anomaly score** (0-10):

```python
anomaly_score = abs(z_score)

Score Range:
0.0 - 1.0: Normal     (green)   ✓
1.0 - 2.5: Unusual    (yellow)  ⚠️
2.5 - 3.5: Anomalous  (orange)  ⚠️⚠️
3.5+     : Critical   (red)     🔴
```

### Visualization

```
Dashboard shows:
┌─────────────────────────────────────┐
│ Service: payment-service            │
│ Anomalies in last 24h: 15           │
│                                     │
│ Distribution:                       │
│ Normal      ████████████ (200)      │
│ Unusual     ████ (60)               │
│ Anomalous   ██ (25)                 │
│ Critical    █ (5)                   │
└─────────────────────────────────────┘
```

---

## Machine Learning Perspective

### Current Approach (Statistical)
```
Advantages:
✓ Simple and interpretable
✓ No training data needed
✓ Fast computation
✓ Works with small datasets

Disadvantages:
✗ Assumes normal distribution
✗ Can't learn complex patterns
✗ Struggles with multi-variate analysis
```

### Future Approach (ML-based)
```
Isolation Forest:
├─ Detects outliers without baseline
├─ Handles multi-dimensional data
└─ Better for complex patterns

LSTM Networks:
├─ Learns temporal patterns
├─ Predicts expected values
└─ Detects deviations from prediction

Clustering (K-means):
├─ Groups similar log patterns
├─ Detects pattern shifts
└─ Identifies new behaviors
```

---

## Real-world Examples

### Example 1: Database Connection Pool Exhaustion

```
Timeline:
09:00 AM - Normal operations
          Connections/hour: 50-60
          Errors: 2-3 per hour

09:15 AM - Slow increase
          Connections/hour: 70
          Errors: 5 per hour
          Z-score: 1.2 (Not anomaly yet)

09:30 AM - Spike begins
          Connections/hour: 120
          Errors: 15 per hour
          Z-score: 2.8 ⚠️ ALERT TRIGGERED

09:45 AM - Peak
          Connections/hour: 150
          Errors: 45 per hour
          Z-score: 8.1 🔴 CRITICAL ALERT

10:00 AM - Auto-recovery/fix applied
          Connections/hour: 55
          Errors: 2 per hour
          Alert: RESOLVED
```

### Example 2: Memory Leak in Service

```
Day 1:
Memory errors: 0
Z-score: 0 (Normal)

Day 2:
Memory errors: 2
Z-score: 0.5 (Still normal)

Day 3:
Memory errors: 5
Z-score: 1.2 (Trending up)

Day 4:
Memory errors: 12
Z-score: 2.3 (Getting close)

Day 5:
Memory errors: 25
Z-score: 3.1 🔴 ANOMALY
Alert: "Memory error rate spike in service-x"
Action: Restart service, investigate leak

Day 6:
Memory errors: 1
Z-score: -0.9 (Back to normal)
```

### Example 3: DDoS Attack

```
Normal traffic:
Requests/minute: 500-600
Error rate: 0.5%
Response time: 100ms

Attack starts:
Requests/minute: 5000 (8x increase)
Error rate: 15% (30x increase)
Response time: 2000ms (20x increase)

Z-scores:
Requests: Z = 12.5 (CRITICAL) 🔴
Errors: Z = 9.2 (CRITICAL) 🔴
Response: Z = 11.0 (CRITICAL) 🔴

Alert severity: CRITICAL
Action: Activate DDoS mitigation
```

---

## Best Practices

### 1. Baseline Warmup Period
```
After first deployment:
- First 24 hours: Collect baseline
- First week: Refine baseline
- Two weeks: Start anomaly detection

Why? Need representative data
```

### 2. Alert Tuning
```
Week 1: Threshold = 2.0 (Sensitive)
        → Discover noisy sources
        → Identify legitimate patterns

Week 2: Threshold = 2.5 (Balanced)
        → Filter false positives
        → Fine-tune per service

Week 3: Threshold = 3.0 (Conservative)
        → Focus on critical issues
        → Reduce alert fatigue
```

### 3. Multi-service Handling
```
✓ Calculate baseline per service
✓ Each service has different patterns
✓ api-gateway might have different
  normal error rate than payment-service

Example:
api-gateway errors/hour: 10-20 (normal range)
payment-service errors/hour: 0-2 (normal range)

If payment-service gets 5 errors → Z=2.5 (Alert!)
If api-gateway gets 5 errors → Z=-1.5 (Normal)
```

### 4. Time-aware Detection
```
Peak hours (9-17):
- Higher normal error rate
- Higher threshold
- Less sensitive

Off-hours (19-7):
- Lower expected traffic
- Lower threshold
- More sensitive
```

---

## Troubleshooting

### False Positives (Too Many Alerts)
```
Problem: Alerts for normal behavior

Solution 1: Increase threshold
    OLD: threshold_std = 2.0
    NEW: threshold_std = 3.0

Solution 2: Extend baseline window
    OLD: window_hours = 12
    NEW: window_hours = 48

Solution 3: Service-specific rules
    - Different thresholds per service
    - Account for service characteristics
```

### False Negatives (Missed Anomalies)
```
Problem: Real issues not detected

Solution 1: Decrease threshold
    OLD: threshold_std = 3.5
    NEW: threshold_std = 2.0

Solution 2: Shorter baseline
    OLD: window_hours = 48
    NEW: window_hours = 24

Solution 3: Add complementary detection
    - Spike detection
    - Silence detection
    - Pattern-based rules
```

### Cold Start Problem
```
Problem: No historical data

Solution: 
- Manually set initial baseline
- Or: Wait 24 hours for warmup
- Or: Import historical logs

Code:
baseline_stats = {
    'mean': 5.0,
    'std_dev': 1.5
}
```

---

## Performance Considerations

### Computation Complexity

```
Operation          │ Complexity │ Time (1M logs)
─────────────────┼───────────┼───────────────
Parse baseline    │ O(n)      │ 50ms
Calculate Z-score │ O(1)      │ <1ms
Full detection    │ O(n)      │ 100ms
```

### Database Queries

```python
# Efficient baseline calculation
queryset.filter(
    service=service_name,
    level__in=['ERROR', 'CRITICAL'],
    timestamp__gte=past_24h
).count()

# Uses database indexing:
# INDEX (service, timestamp, level)
```

---

## Monitoring Anomaly Detection

### Metrics to Track

```
1. Detection Rate
   - Anomalies detected per day
   - Trend over time
   
2. False Positive Rate
   - % of alerts that were invalid
   - Should be < 5%
   
3. Detection Latency
   - Time from event to alert
   - Should be < 1 minute
   
4. Z-score Distribution
   - Normal: Most logs Z < 2
   - Healthy system: Few Z > 3
```

### Health Check Query

```python
# Query to verify system health
recent_logs = Log.objects.filter(
    timestamp__gte=timezone.now() - timedelta(hours=1)
)

stats = {
    'total': recent_logs.count(),
    'anomalies': recent_logs.filter(is_anomaly=True).count(),
    'anomaly_rate': (
        recent_logs.filter(is_anomaly=True).count() 
        / recent_logs.count() * 100
    )
}

# Healthy: anomaly_rate < 1%
# Warning: anomaly_rate 1-5%
# Critical: anomaly_rate > 5%
```

---

## Integration with Alert Rules

### How Anomaly Detection Powers Alerts

```
Log arrives
    ↓
Anomaly Detection scores it
    ↓
If is_anomaly = True
    └─→ Triggers rule: "Anomalies"
    └─→ Creates high-severity alert
    └─→ Notifies on-call engineer
```

### Example Alert Rule Using Anomaly

```python
rule = AlertRule(
    name="Anomaly Alert",
    condition_type="contains",
    text_pattern="is_anomaly=True",  # Implicit
    severity="high",
    email_recipients="ops@company.com"
)
```

---

## Future Enhancements

1. **Seasonal Decomposition**
   - Account for daily/weekly patterns
   - Different baselines for different days

2. **Contextual Anomalies**
   - Consider related metrics
   - Correlated events detection

3. **Prediction-based Detection**
   - Predict expected values
   - Alert on prediction errors

4. **User-defined Patterns**
   - Custom anomaly patterns
   - Domain-specific rules

---

**Last Updated:** January 2024
**Anomaly Detection Version:** 1.0
