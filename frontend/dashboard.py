"""
Log Aggregation Dashboard - Streamlit Frontend
Real-time log visualization and analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Log Aggregation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .error-card {
        background-color: #ffebee;
        padding: 15px;
        border-left: 4px solid #f44336;
    }
    .warning-card {
        background-color: #fff3e0;
        padding: 15px;
        border-left: 4px solid #ff9800;
    }
    .success-card {
        background-color: #e8f5e9;
        padding: 15px;
        border-left: 4px solid #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

# Backend configuration
import os
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api")

@st.cache_resource
def get_api_client():
    """Get API client session"""
    return requests.Session()

def fetch_logs(filters=None):
    """Fetch logs from backend"""
    try:
        params = filters or {}
        response = requests.get(f"{API_BASE_URL}/logs/", params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching logs: {e}")
        return None

def fetch_statistics(hours=24):
    """Fetch log statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/logs/statistics/", params={'hours': hours})
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching statistics: {e}")
        return None

def fetch_alerts(status=None):
    """Fetch alerts"""
    try:
        params = {}
        if status:
            params['status'] = status
        response = requests.get(f"{API_BASE_URL}/alerts/", params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching alerts: {e}")
        return None

def fetch_sources():
    """Fetch log sources"""
    try:
        response = requests.get(f"{API_BASE_URL}/sources/")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching sources: {e}")
        return None

def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        response = requests.post(f"{API_BASE_URL}/alerts/{alert_id}/acknowledge/")
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error acknowledging alert: {e}")
        return False

def resolve_alert(alert_id):
    """Resolve an alert"""
    try:
        response = requests.post(f"{API_BASE_URL}/alerts/{alert_id}/resolve/")
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error resolving alert: {e}")
        return False

# Sidebar Navigation
st.sidebar.title("📊 Log Aggregation Dashboard")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Logs", "Alerts", "Rules", "Upload Logs", "Settings"]
)

# Dashboard Page
if page == "Dashboard":
    st.title("📊 Dashboard Overview")
    
    col1, col2, col3 = st.columns(3)
    time_range = st.sidebar.selectbox("Time Range", ["All Time", "1 hour", "6 hours", "24 hours", "7 days"])
    
    hours_map = {"All Time": 0, "1 hour": 1, "6 hours": 6, "24 hours": 24, "7 days": 168}
    hours = hours_map[time_range]
    
    stats = fetch_statistics(hours)
    
    if stats:
        with col1:
            st.metric("Total Logs", f"{stats.get('total_logs', 0):,}")
        
        with col2:
            st.metric("Anomalies Detected", f"{stats.get('anomalies_count', 0):,}")
        
        with col3:
            st.metric("Error Rate", f"{stats.get('error_rate', 0):.2f}%")
        
        # Log distribution by level
        st.subheader("Log Distribution by Level")
        level_data = stats.get('by_level', {})
        if level_data:
            fig = px.pie(
                values=list(level_data.values()),
                names=list(level_data.keys()),
                title="Logs by Severity Level",
                color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#c0392b']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Logs by service
        st.subheader("Logs by Service")
        service_data = stats.get('by_service', {})
        if service_data:
            df = pd.DataFrame(list(service_data.items()), columns=['Service', 'Count'])
            fig = px.bar(df, x='Service', y='Count', title="Log Count by Service",
                        color='Count', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

        # Logs over time (timeline)
        st.subheader("📈 Logs Over Time")
        try:
            response = requests.get(f"{API_BASE_URL}/logs/")
            all_logs = response.json().get('results', [])
            if all_logs:
                df_time = pd.DataFrame(all_logs)
                df_time['timestamp'] = pd.to_datetime(df_time['timestamp'], utc=True)
                df_time['date'] = df_time['timestamp'].dt.floor('H')
                timeline = df_time.groupby(['date', 'level']).size().reset_index(name='count')
                fig = px.line(timeline, x='date', y='count', color='level',
                             title="Log Volume Over Time",
                             color_discrete_map={
                                 'INFO': '#2ecc71', 'WARNING': '#f39c12',
                                 'ERROR': '#e74c3c', 'CRITICAL': '#c0392b', 'DEBUG': '#3498db'
                             })
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No log data available for timeline")
        except Exception as e:
            st.warning(f"Could not load timeline chart: {e}")

        # Top error messages
        st.subheader("🔴 Top Error Messages")
        try:
            response = requests.get(f"{API_BASE_URL}/logs/")
            all_logs = response.json().get('results', [])
            if all_logs:
                df_err = pd.DataFrame(all_logs)
                df_err = df_err[df_err['level'].isin(['ERROR', 'CRITICAL'])]
                if not df_err.empty:
                    top_errors = df_err['message'].value_counts().head(10).reset_index()
                    top_errors.columns = ['Message', 'Count']
                    fig = px.bar(top_errors, x='Count', y='Message', orientation='h',
                                title="Top 10 Error Messages",
                                color='Count', color_continuous_scale='Reds')
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No error logs found")
        except Exception as e:
            st.warning(f"Could not load error messages chart: {e}")

        # Anomaly trend
        st.subheader("⚠️ Anomaly Trend")
        try:
            response = requests.get(f"{API_BASE_URL}/logs/", params={'is_anomaly': 'true'})
            anomaly_logs = response.json().get('results', [])
            if anomaly_logs:
                df_an = pd.DataFrame(anomaly_logs)
                df_an['timestamp'] = pd.to_datetime(df_an['timestamp'], utc=True)
                df_an['date'] = df_an['timestamp'].dt.floor('H')
                anomaly_trend = df_an.groupby(['date', 'service']).size().reset_index(name='count')
                fig = px.area(anomaly_trend, x='date', y='count', color='service',
                             title="Anomalies Detected Over Time")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No anomalies detected yet")
        except Exception as e:
            st.warning(f"Could not load anomaly trend chart: {e}")

    # Active Alerts
    st.subheader("🚨 Active Alerts")
    alerts = fetch_alerts(status='triggered')
    
    if alerts:
        for alert in alerts[:5]:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{alert['rule']}** - {alert['message']}")
                    st.caption(f"Triggered: {alert['triggered_at']}")
                with col2:
                    if st.button("Acknowledge", key=f"ack_{alert['id']}"):
                        if acknowledge_alert(alert['id']):
                            st.success("Alert acknowledged")
                            st.rerun()
                with col3:
                    if st.button("Resolve", key=f"res_{alert['id']}"):
                        if resolve_alert(alert['id']):
                            st.success("Alert resolved")
                            st.rerun()
                st.divider()

# Logs Page
elif page == "Logs":
    st.title("🔍 Log Search & Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_term = st.text_input("Search logs", placeholder="Enter search term")
    
    with col2:
        log_level = st.multiselect("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    
    with col3:
        service_name = st.text_input("Service Name", placeholder="e.g., nginx-web")
    
    with col4:
        show_anomalies = st.checkbox("Anomalies Only")
    
    # Build filter params
    filters = {}
    if search_term:
        filters['search'] = search_term
    if log_level:
        filters['level'] = log_level[0]  # API accepts single value
    if service_name:
        filters['service'] = service_name
    if show_anomalies:
        filters['is_anomaly'] = 'true'
    
    logs_response = fetch_logs(filters)
    
    if logs_response:
        results = logs_response.get('results', [])
        
        st.write(f"**Found {logs_response.get('count', 0)} logs**")
        
        if results:
            df = pd.DataFrame(results)
            
            # Display as table
            st.dataframe(
                df[['timestamp', 'level', 'service', 'message', 'is_anomaly']],
                use_container_width=True,
                height=400
            )
            
            # Log statistics for filtered results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Logs", len(results))
            with col2:
                anomaly_count = sum(1 for log in results if log['is_anomaly'])
                st.metric("Anomalies", anomaly_count)
            with col3:
                error_count = sum(1 for log in results if log['level'] in ['ERROR', 'CRITICAL'])
                st.metric("Errors", error_count)
            
            # Detailed log view
            st.subheader("Detailed View")
            selected_idx = st.selectbox(
                "Select log to view details",
                range(len(results)),
                format_func=lambda i: f"{results[i]['timestamp']} - {results[i]['service']}"
            )
            
            if selected_idx is not None:
                log = results[selected_idx]
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Timestamp:**", log['timestamp'])
                    st.write("**Level:**", log['level'])
                    st.write("**Service:**", log['service'])
                    st.write("**Source:**", log['source'])
                
                with col2:
                    st.write("**Is Anomaly:**", log['is_anomaly'])
                    st.write("**Anomaly Score:**", log['anomaly_score'])
                    st.write("**Created:**", log['created_at'])
                
                st.write("**Message:**")
                st.code(log['message'], language="text")
                
                if log['metadata']:
                    st.write("**Metadata:**")
                    st.json(log['metadata'])

# Alerts Page
elif page == "Alerts":
    st.title("🚨 Alert Management")
    
    alert_status = st.selectbox("Filter by Status", ["triggered", "acknowledged", "resolved"])
    
    alerts = fetch_alerts(status=alert_status)
    
    if alerts:
        st.write(f"**Total {alert_status} alerts: {len(alerts)}**")
        
        for alert in alerts:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    severity_color = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
                    st.write(f"{severity_color.get(alert.get('severity', 'medium'), '⚪')} **{alert['rule']}**")
                    st.caption(alert['message'])
                
                with col2:
                    st.write(f"Logs: {alert['log_count']}")
                
                with col3:
                    st.write(f"Status: {alert['status']}")
                
                with col4:
                    if alert['status'] == 'triggered':
                        if st.button("Action", key=f"action_{alert['id']}"):
                            if acknowledge_alert(alert['id']):
                                st.success("Acknowledged")
                                st.rerun()
                
                st.divider()
    else:
        st.info("No alerts found")

# Rules Page
elif page == "Rules":
    st.title("⚙️ Alert Rules Management")
    
    tab1, tab2 = st.tabs(["View Rules", "Create Rule"])
    
    with tab1:
        st.subheader("Existing Rules")
        try:
            response = requests.get(f"{API_BASE_URL}/rules/")
            if response.status_code == 200:
                rules = response.json()
                for rule in rules:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        status_icon = "✅" if rule['enabled'] else "❌"
                        st.write(f"{status_icon} **{rule['name']}** ({rule['severity']})")
                        st.caption(f"{rule['condition_type']} - {rule['description']}")
                    with col2:
                        st.write(f"Recipients: {rule['email_recipients'] or 'None'}")
        except Exception as e:
            st.error(f"Error loading rules: {e}")
    
    with tab2:
        st.subheader("Create New Rule")
        
        with st.form("new_rule_form"):
            name = st.text_input("Rule Name")
            description = st.text_area("Description")
            condition_type = st.selectbox(
                "Condition Type",
                ["contains", "level_equals", "error_rate", "frequency"]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                service_filter = st.text_input("Service Filter (optional)")
                level_filter = st.selectbox("Log Level", ["", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
            
            with col2:
                text_pattern = st.text_input("Text Pattern (optional)")
                threshold = st.number_input("Threshold Value", value=5, min_value=1)
            
            email_recipients = st.text_input("Email Recipients (comma-separated)")
            severity = st.selectbox("Severity", ["low", "medium", "high"])
            
            if st.form_submit_button("Create Rule"):
                rule_data = {
                    'name': name,
                    'description': description,
                    'condition_type': condition_type,
                    'service_filter': service_filter,
                    'level_filter': level_filter,
                    'text_pattern': text_pattern,
                    'threshold_value': threshold,
                    'email_recipients': email_recipients,
                    'severity': severity,
                    'enabled': True
                }
                
                try:
                    response = requests.post(f"{API_BASE_URL}/rules/", json=rule_data)
                    if response.status_code == 201:
                        st.success("Rule created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error creating rule: {e}")

# Upload Logs Page
elif page == "Upload Logs":
    st.title("📤 Upload Log Files")
    
    sources = fetch_sources()
    
    if sources:
        source_names = [s['name'] for s in sources]
        selected_source = st.selectbox("Select Log Source", source_names)
        source_id = next(s['id'] for s in sources if s['name'] == selected_source)
    else:
        st.error("No log sources found")
        st.stop()
    
    uploaded_file = st.file_uploader("Choose a log file", type=['log', 'txt'])
    
    if uploaded_file is not None:
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size} bytes")
        
        if st.button("Upload Logs"):
            with st.spinner("Uploading and processing logs..."):
                files = {'file': uploaded_file}
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/sources/{source_id}/upload_logs/",
                        files=files
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success(result['message'])
                        st.info(f"Ingested {result['count']} logs")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error uploading: {e}")

# Settings Page
elif page == "Settings":
    st.title("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Log Sources")
        sources = fetch_sources()
        if sources:
            for source in sources:
                col_name, col_type, col_count = st.columns([1, 1, 1])
                with col_name:
                    st.write(source['name'])
                with col_type:
                    st.write(source['source_type'])
                with col_count:
                    st.write(f"{source['log_count']} logs")
                st.divider()
    
    with col2:
        st.subheader("Dashboard Settings")
        refresh_interval = st.slider("Auto-refresh interval (seconds)", 5, 300, 30)
        st.write(f"Current interval: {refresh_interval}s")
        
        log_retention = st.number_input("Log retention (days)", value=30, min_value=1)
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")

# Footer
st.sidebar.divider()
st.sidebar.caption("📊 Log Aggregation Dashboard v1.0")
st.sidebar.caption("Built with Streamlit & Django")
