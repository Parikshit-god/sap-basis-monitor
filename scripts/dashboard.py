import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import psutil
from datetime import datetime, date, timedelta
import os
import sys

# Add parent directory to sys.path so we can import our other scripts
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

# Paths
db_path = os.path.join(project_root, "data", "sap_system.db")
log_path = os.path.join(project_root, "sapmnt", "PRD", "logs", "SM21_log.txt")

# ==========================================
# INITIALIZATION ENGINE (Cloud Deployment)
# ==========================================
def initialize_if_needed():
    if not os.path.exists(db_path):
        print("🔧 Initialization Triggered: Database not found. Building SAP architecture...")
        
        # 1. Create Folder Structure
        folders = [
            "sapmnt/PRD/profile", "sapmnt/PRD/trans", "sapmnt/PRD/logs",
            "sapmnt/QAS/profile", "sapmnt/QAS/logs", "sapmnt/DEV/profile", "sapmnt/DEV/logs",
            "usr/sap/PRD/SYS", "usr/sap/PRD/work", "data", "reports", "scripts", "templates"
        ]
        for f in folders:
            os.makedirs(os.path.join(project_root, *f.split('/')), exist_ok=True)
            
        # 2. Create Dummy Log File
        log_content = """2024-01-15 08:23:11 [PRD] [CRITICAL] Database connection lost - reconnecting attempt 1 of 5.
2024-01-15 08:24:01 [PRD] [DB_ERROR] ORA-03113: end-of-file on communication channel.
2024-01-15 08:30:00 [PRD] [MEMORY_LOW] Extended memory usage above 90%.
2024-01-15 08:50:00 [PRD] [INFO] Workprocess restart - WP 0 restarted by dispatcher.
2024-01-15 09:20:00 [PRD] [WARNING] Certificate expiring in 14 days for STRUST."""
        with open(log_path, "w") as lf:
            lf.write(log_content)
            
        # 3. Create Database and Tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS USR02 (MANDT TEXT DEFAULT '100', BNAME TEXT PRIMARY KEY, GLTGV TEXT, GLTGB TEXT, USTYP TEXT, CLASS TEXT, UFLAG INTEGER DEFAULT 0, TRDAT TEXT, LTIME TEXT, ERDAT TEXT, BCODE INTEGER DEFAULT 0, DEPARTMENT TEXT, EMAIL TEXT);
            CREATE TABLE IF NOT EXISTS SMSLOG (ID INTEGER PRIMARY KEY AUTOINCREMENT, TIMESTAMP TEXT, SYSTEM_ID TEXT, CPU_USAGE REAL, RAM_USAGE REAL, DISK_USAGE REAL, DB_LATENCY_MS REAL, ALERT_FLAGS TEXT, STATUS TEXT);
            CREATE TABLE IF NOT EXISTS SECURITY_AUDIT (ID INTEGER PRIMARY KEY AUTOINCREMENT, TIMESTAMP TEXT, USERNAME TEXT, VIOLATION_TYPE TEXT, ACTION_TAKEN TEXT, SEVERITY TEXT, RESOLVED INTEGER DEFAULT 0);
        """)
        
        # 4. Insert Dynamic Mock Data
        today = date.today()
        future = (today + timedelta(days=365)).strftime('%Y-%m-%d')
        expired = (today - timedelta(days=5)).strftime('%Y-%m-%d')
        past_100 = (today - timedelta(days=100)).strftime('%Y-%m-%d')
        past_60 = (today - timedelta(days=60)).strftime('%Y-%m-%d')
        past_10 = (today - timedelta(days=10)).strftime('%Y-%m-%d')
        created = (today - timedelta(days=200)).strftime('%Y-%m-%d')
        
        users = [
            ('JSMITH', future, expired, 'A', 'ENDUSER', 0, past_100, '08:00:00', created, 0, 'Finance', 'jsmith@company.com'),
            ('ABAUER', future, expired, 'A', 'ENDUSER', 0, past_100, '09:15:00', created, 0, 'HR', 'abauer@company.com'),
            ('RFC_CONNECT', future, future, 'B', 'BASIS', 0, past_100, '23:00:00', created, 0, 'IT', 'rfc@company.com'),
            ('BATCH_USER', future, future, 'B', 'BASIS', 0, past_100, '01:00:00', created, 0, 'Basis', 'batch@company.com'),
            ('MWILSON', future, future, 'A', 'ENDUSER', 0, past_100, '10:30:00', created, 0, 'Logistics', 'mwilson@company.com'),
            ('PATEL_R', future, future, 'A', 'ENDUSER', 0, past_100, '14:45:00', created, 0, 'Finance', 'rpatel@company.com'),
            ('HRUSER01', future, future, 'A', 'ENDUSER', 0, past_60, '08:30:00', created, 0, 'HR', 'hr01@company.com'),
            ('LCHEN', future, future, 'A', 'ENDUSER', 0, past_60, '11:20:00', created, 0, 'IT', 'lchen@company.com'),
            ('SRODRIGUEZ', future, future, 'A', 'BASIS', 0, past_60, '16:00:00', created, 0, 'Basis', 'srodriguez@company.com'),
            ('TJONES', future, future, 'A', 'ENDUSER', 0, past_60, '09:45:00', created, 0, 'Logistics', 'tjones@company.com'),
            ('KLEE', future, future, 'A', 'ENDUSER', 0, past_10, '08:05:00', created, 0, 'Finance', 'klee@company.com'),
            ('SAP_ADMIN', future, future, 'A', 'SUPER', 0, past_10, '07:30:00', created, 0, 'Basis', 'admin@company.com'),
            ('RWHITE', future, future, 'A', 'ENDUSER', 0, past_10, '09:10:00', created, 0, 'HR', 'rwhite@company.com'),
            ('MGARCIA', future, future, 'A', 'ENDUSER', 0, past_10, '10:15:00', created, 0, 'IT', 'mgarcia@company.com'),
            ('DCLARK', future, future, 'A', 'ENDUSER', 0, past_10, '13:20:00', created, 0, 'Logistics', 'dclark@company.com'),
            ('NEWUSER1', future, future, 'A', 'ENDUSER', 0, '', '', created, 0, 'Finance', 'nu1@company.com'),
            ('NEWUSER2', future, future, 'A', 'ENDUSER', 0, '', '', created, 0, 'HR', 'nu2@company.com'),
            ('NEWUSER3', future, future, 'A', 'ENDUSER', 0, '', '', created, 0, 'IT', 'nu3@company.com'),
            ('BSMITH', future, future, 'A', 'ENDUSER', 0, past_10, '08:00:00', created, 6, 'Basis', 'bsmith@company.com'),
            ('ADAVIS', future, future, 'A', 'ENDUSER', 0, past_10, '08:00:00', created, 7, 'Logistics', 'adavis@company.com'),
            ('EMARTIN', future, future, 'A', 'ENDUSER', 0, past_10, '08:00:00', created, 8, 'Finance', 'emartin@company.com'),
            ('JTHOMAS', future, future, 'A', 'ENDUSER', 0, past_10, '08:00:00', created, 9, 'HR', 'jthomas@company.com'),
            ('LOCKED01', future, future, 'A', 'ENDUSER', 64, past_10, '08:00:00', created, 0, 'IT', 'lock1@company.com'),
            ('LOCKED02', future, future, 'A', 'ENDUSER', 64, past_10, '08:00:00', created, 0, 'Basis', 'lock2@company.com'),
            ('BAD_ACTOR', future, future, 'A', 'ENDUSER', 64, past_10, '08:00:00', created, 0, 'Logistics', 'bad@company.com')
        ]
        cursor.executemany("INSERT INTO USR02 (BNAME, GLTGV, GLTGB, USTYP, CLASS, UFLAG, TRDAT, LTIME, ERDAT, BCODE, DEPARTMENT, EMAIL) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", users)
        conn.commit()
        conn.close()
        
        print("✅ Environment initialized. Running first automated checks...")
        from scripts.basis_health_check import run_full_health_check
        from scripts.user_access_auditor import run_full_audit
        run_full_health_check()
        run_full_audit()
        print("✅ Initial checks complete. Dashboard ready.")

# Run initialization before rendering UI
initialize_if_needed()

from scripts.basis_health_check import run_full_health_check
from scripts.user_access_auditor import run_full_audit

# Configuration
st.set_page_config(page_title="SAP Basis Infrastructure Monitor", layout="wide", page_icon="🖥️")

def get_db_connection():
    return sqlite3.connect(db_path)

st.title("🖥️ SAP Basis Infrastructure Monitor")
st.subheader("Production System (PRD) — Real-Time Monitoring Dashboard")
st.caption(f"Last Refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

conn = get_db_connection()
smslog_latest = pd.read_sql_query("SELECT * FROM SMSLOG ORDER BY TIMESTAMP DESC LIMIT 1", conn)

if smslog_latest.empty:
    st.info("No health check data yet — run a health check first using the sidebar.")
else:
    latest_status = smslog_latest.iloc[0]['STATUS']
    if 'CRITICAL' in latest_status:
        st.markdown("<h3 style='color: #ff4b4b;'>🔴 STATUS: CRITICAL</h3>", unsafe_allow_html=True)
    elif 'WARNING' in latest_status:
        st.markdown("<h3 style='color: #ffa421;'>🟡 STATUS: WARNING</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='color: #21c354;'>🟢 STATUS: OK</h3>", unsafe_allow_html=True)

st.divider()

st.markdown("### Live Server Resources")
col1, col2, col3 = st.columns(3)

cpu_usage = psutil.cpu_percent(interval=0.5)
ram_usage = psutil.virtual_memory().percent
disk_usage = psutil.disk_usage('/').percent

def create_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps' : [
                {'range': [0, 60], 'color': "lightgreen"},
                {'range': [60, 80], 'color': "gold"},
                {'range': [80, 100], 'color': "salmon"}
            ],
            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
    return fig

with col1:
    st.plotly_chart(create_gauge(cpu_usage, "CPU Usage %"), use_container_width=True)
with col2:
    st.plotly_chart(create_gauge(ram_usage, "RAM Usage %"), use_container_width=True)
with col3:
    st.plotly_chart(create_gauge(disk_usage, "Disk Usage %"), use_container_width=True)

st.divider()

st.markdown("### Database Connection Status")
db_col1, db_col2, db_col3, db_col4 = st.columns(4)

try:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM USR02")
    user_count = cursor.fetchone()[0]
    db_col1.markdown("#### 🟢 DATABASE CONNECTED")
except Exception:
    user_count = 0
    db_col1.markdown("#### 🔴 DATABASE DISCONNECTED")

if not smslog_latest.empty:
    db_col2.metric("Last Health Check", smslog_latest.iloc[0]['TIMESTAMP'])
    db_col3.metric("DB Latency (ms)", f"{smslog_latest.iloc[0]['DB_LATENCY_MS']:.2f}")
else:
    db_col2.metric("Last Health Check", "N/A")
    db_col3.metric("DB Latency (ms)", "N/A")

db_col4.metric("Total User Count", user_count)

st.divider()

st.markdown("### System Log Analysis (SM21)")
keywords = ['CRITICAL', 'DB_ERROR', 'MEMORY_LOW', 'WARNING', 'INFO']
keyword_counts = {kw: 0 for kw in keywords}
critical_lines = []

try:
    with open(log_path, 'r') as f:
        for line in f:
            for kw in keywords:
                if kw in line:
                    keyword_counts[kw] += 1
                    if kw in ['CRITICAL', 'DB_ERROR']:
                        critical_lines.append(line.strip())
except FileNotFoundError:
    st.warning("Log file not found.")

df_logs = pd.DataFrame(list(keyword_counts.items()), columns=['Keyword', 'Occurrences'])

def style_high_counts(val):
    color = 'red' if isinstance(val, int) and val > 0 else ''
    return f'color: {color}'

log_col1, log_col2 = st.columns([1, 2])
with log_col1:
    try:
        styled_df = df_logs.style.map(style_high_counts, subset=['Occurrences'])
    except AttributeError:
        styled_df = df_logs.style.applymap(style_high_counts, subset=['Occurrences'])
    st.dataframe(styled_df, use_container_width=True)

with log_col2:
    with st.expander("View Critical Log Lines (CRITICAL & DB_ERROR)"):
        if critical_lines:
            for line in critical_lines:
                st.code(line, language="text")
        else:
            st.success("No critical lines found!")

st.divider()

st.markdown("### User Access Overview")
df_users = pd.read_sql_query("SELECT * FROM USR02", conn)
df_audit = pd.read_sql_query("SELECT * FROM SECURITY_AUDIT WHERE RESOLVED = 0", conn)

u_col1, u_col2, u_col3, u_col4 = st.columns(4)
u_col1.metric("Total Users", len(df_users))
u_col2.metric("Active Users", len(df_users[df_users['UFLAG'] == 0]))
u_col3.metric("Locked Users", len(df_users[df_users['UFLAG'].isin([64, 128])]))
u_col4.metric("Security Violations", len(df_audit))

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    dept_options = ["All Departments"] + df_users['DEPARTMENT'].unique().tolist()
    selected_dept = st.selectbox("Filter by Department", dept_options)
with filter_col2:
    status_options = ["All", "Active only", "Locked only"]
    selected_status = st.selectbox("Filter by Status", status_options)

filtered_users = df_users.copy()
if selected_dept != "All Departments":
    filtered_users = filtered_users[filtered_users['DEPARTMENT'] == selected_dept]
if selected_status == "Active only":
    filtered_users = filtered_users[filtered_users['UFLAG'] == 0]
elif selected_status == "Locked only":
    filtered_users = filtered_users[filtered_users['UFLAG'].isin([64, 128])]

st.dataframe(filtered_users, use_container_width=True)

st.divider()

st.markdown("### Active Security Violations")
if not df_audit.empty:
    v_col1, v_col2 = st.columns([1, 1])
    with v_col1:
        st.dataframe(df_audit[['USERNAME', 'VIOLATION_TYPE', 'ACTION_TAKEN', 'SEVERITY', 'TIMESTAMP']], use_container_width=True)
    with v_col2:
        fig_bar = px.bar(df_audit, x='VIOLATION_TYPE', color='SEVERITY', title="Violations by Type and Severity",
                         color_discrete_map={'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'yellow'})
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No security violations on record. Run a security audit to populate this panel.")

st.divider()

st.markdown("### Historical Resource Trends")
df_history = pd.read_sql_query("SELECT TIMESTAMP, CPU_USAGE, RAM_USAGE, DISK_USAGE FROM SMSLOG ORDER BY TIMESTAMP", conn)

if len(df_history) >= 2:
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df_history['TIMESTAMP'], y=df_history['CPU_USAGE'], mode='lines+markers', name='CPU %'))
    fig_line.add_trace(go.Scatter(x=df_history['TIMESTAMP'], y=df_history['RAM_USAGE'], mode='lines+markers', name='RAM %'))
    fig_line.add_trace(go.Scatter(x=df_history['TIMESTAMP'], y=df_history['DISK_USAGE'], mode='lines+markers', name='Disk %'))
    
    fig_line.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Alert Threshold (80%)")
    fig_line.update_layout(height=400, yaxis_title="Usage Percentage", xaxis_title="Time")
    
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("Run the health check multiple times to see historical trends here.")

conn.close()

st.sidebar.title("⚡ Quick Actions")
if st.sidebar.button("▶ Run Health Check Now", use_container_width=True):
    with st.spinner("Running Health Check..."):
        run_full_health_check()
    st.sidebar.success("Health Check Complete!")
    st.rerun()

if st.sidebar.button("🔒 Run Security Audit Now", use_container_width=True):
    with st.spinner("Running Security Audit..."):
        run_full_audit()
    st.sidebar.success("Audit Complete!")
    st.rerun()

if st.sidebar.button("🔄 Refresh Dashboard", use_container_width=True):
    st.rerun()

st.sidebar.divider()
st.sidebar.title("ℹ️ System Info")
st.sidebar.text(f"Python: {sys.version.split()[0]}")
st.sidebar.text(f"Streamlit: {st.__version__}")
if os.path.exists(db_path):
    st.sidebar.text(f"DB Size: {(os.path.getsize(db_path) / 1024):.1f} KB")