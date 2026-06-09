import os
import sqlite3
import time
from datetime import datetime
import psutil

# Setup dynamic paths relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
db_path = os.path.join(project_root, "data", "sap_system.db")
log_path = os.path.join(project_root, "sapmnt", "PRD", "logs", "SM21_log.txt")
reports_dir = os.path.join(project_root, "reports")

def check_server_resources():
    print("\n[Running: Server Resource Check]")
    # Get stats using psutil
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Convert bytes to GB for readability
    ram_total_gb = ram.total / (1024**3)
    ram_used_gb = ram.used / (1024**3)
    ram_avail_gb = ram.available / (1024**3)
    
    disk_total_gb = disk.total / (1024**3)
    disk_used_gb = disk.used / (1024**3)
    disk_free_gb = disk.free / (1024**3)

    # Evaluate thresholds
    alerts = []
    if cpu > 80:
        alerts.append('CPU_CRITICAL')
    elif cpu > 60:
        alerts.append('CPU_WARNING')

    if ram.percent > 85:
        alerts.append('RAM_CRITICAL')
    elif ram.percent > 70:
        alerts.append('RAM_WARNING')

    if disk.percent > 90:
        alerts.append('DISK_CRITICAL')
    elif disk.percent > 75:
        alerts.append('DISK_WARNING')

    # Print formatted output
    print(f"  CPU Usage:  {cpu}%")
    print(f"  RAM Usage:  {ram.percent}% ({ram_used_gb:.2f} GB used / {ram_total_gb:.2f} GB total, {ram_avail_gb:.2f} GB available)")
    print(f"  Disk Usage: {disk.percent}% ({disk_used_gb:.2f} GB used / {disk_total_gb:.2f} GB total, {disk_free_gb:.2f} GB free)")
    
    return {
        'cpu_percent': cpu,
        'ram_percent': ram.percent,
        'disk_percent': disk.percent,
        'alerts': alerts
    }

def check_database_connectivity(db_path):
    print("\n[Running: Database Connectivity Check]")
    start_time = time.time()
    result = {'status': 'OK', 'latency_ms': 0, 'user_count': 0, 'error': None}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM USR02")
        result['user_count'] = cursor.fetchone()[0]
        conn.close()
    except Exception as e:
        result['status'] = 'CRITICAL'
        result['error'] = str(e)
        print(f"  CRITICAL ERROR: {e}")
        return result

    latency = (time.time() - start_time) * 1000
    result['latency_ms'] = latency

    if latency > 1000:
        result['status'] = 'DB_LATENCY_CRITICAL'
    elif latency > 500:
        result['status'] = 'DB_LATENCY_WARNING'

    print(f"  Status:     {result['status']}")
    print(f"  Latency:    {latency:.2f} ms")
    print(f"  User Count: {result['user_count']}")

    return result

def parse_sap_system_log(log_file_path):
    print("\n[Running: System Log Analysis (SM21)]")
    keywords = ['CRITICAL', 'DB_ERROR', 'MEMORY_LOW', 'WARNING', 'Workprocess restart', 'Database connection lost', 'INFO']
    counts = {kw: {'count': 0, 'lines': []} for kw in keywords}

    try:
        with open(log_file_path, 'r') as file:
            for line in file:
                for kw in keywords:
                    if kw in line:
                        counts[kw]['count'] += 1
                        if kw in ['CRITICAL', 'DB_ERROR', 'MEMORY_LOW']:
                            counts[kw]['lines'].append(line.strip())
    except Exception as e:
        print(f"  Error reading log file: {e}")

    for kw, data in counts.items():
        if kw != 'INFO': # Skip printing INFO to match phase 3 requirements, but keep in dict for later phases
            print(f"  {kw}: {data['count']} occurrences")

    return counts

def save_health_snapshot(db_path, resources, db_check):
    all_alerts = resources['alerts'].copy()
    if db_check['status'] != 'OK':
        all_alerts.append(db_check['status'])

    # Determine overall status
    if any('CRITICAL' in a for a in all_alerts):
        overall_status = 'CRITICAL'
    elif any('WARNING' in a for a in all_alerts):
        overall_status = 'WARNING'
    else:
        overall_status = 'OK'

    alert_flags = ','.join(all_alerts) if all_alerts else 'NONE'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO SMSLOG (TIMESTAMP, SYSTEM_ID, CPU_USAGE, RAM_USAGE, DISK_USAGE, DB_LATENCY_MS, ALERT_FLAGS, STATUS)
            VALUES (?, 'PRD', ?, ?, ?, ?, ?, ?)
        """, (timestamp, resources['cpu_percent'], resources['ram_percent'], resources['disk_percent'], db_check['latency_ms'], alert_flags, overall_status))
        conn.commit()
        conn.close()
        print(f"\n✅ Health snapshot saved to database successfully.")
        return True
    except Exception as e:
        print(f"\n❌ Failed to save snapshot: {e}")
        return False

def generate_health_report(resources, db_check, log_analysis):
    timestamp_for_file = datetime.now().strftime("%Y-%m-%d_%H-%M")
    timestamp_for_header = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    filename = f"health_report_{timestamp_for_file}.txt"
    filepath = os.path.join(reports_dir, filename)

    lines = []
    lines.append("SAP BASIS HEALTH CHECK REPORT")
    lines.append(f"Generated: {timestamp_for_header}")
    lines.append("==================================================")
    
    lines.append("\nSERVER RESOURCES")
    lines.append(f"CPU Usage:  {resources['cpu_percent']}%")
    lines.append(f"RAM Usage:  {resources['ram_percent']}%")
    lines.append(f"Disk Usage: {resources['disk_percent']}%")
    
    lines.append("\nDATABASE STATUS")
    lines.append(f"Status:     {db_check['status']}")
    lines.append(f"Latency:    {db_check['latency_ms']:.2f} ms")
    lines.append(f"User Count: {db_check['user_count']}")
    
    lines.append("\nSYSTEM LOG ANALYSIS (SM21)")
    lines.append("Keyword Counts:")
    for kw, data in log_analysis.items():
        if kw != 'INFO':
            lines.append(f"  - {kw}: {data['count']}")
    
    lines.append("\nCritical Log Lines Found:")
    for kw in ['CRITICAL', 'DB_ERROR', 'MEMORY_LOW']:
        for line in log_analysis[kw]['lines'][:10]:
            lines.append(f"  {line}")

    lines.append("\nACTIVE ALERTS")
    all_alerts = resources['alerts'].copy()
    if db_check['status'] != 'OK':
        all_alerts.append(db_check['status'])
        
    if all_alerts:
        for alert in all_alerts:
            lines.append(f"  [!] {alert}")
    else:
        lines.append("  NO ACTIVE ALERTS")
        
    lines.append("\n==================================================")

    with open(filepath, 'w') as file:
        file.write('\n'.join(lines))
        
    print(f"📄 Report saved to: {os.path.relpath(filepath, project_root)}")
    return filepath

def run_full_health_check():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n  ================================================")
    print("  === SAP BASIS HEALTH CHECK MONITOR           ===")
    print(f"  === {current_time:<40} ===")
    print("  ================================================")

    resources = check_server_resources()
    db_check = check_database_connectivity(db_path)
    log_analysis = parse_sap_system_log(log_path)
    
    save_health_snapshot(db_path, resources, db_check)
    generate_health_report(resources, db_check, log_analysis)
    
    # Calculate overall status for the final print
    all_alerts = resources['alerts'].copy()
    if db_check['status'] != 'OK':
        all_alerts.append(db_check['status'])
        
    if any('CRITICAL' in a for a in all_alerts):
        overall_status = 'CRITICAL 🔴'
    elif any('WARNING' in a for a in all_alerts):
        overall_status = 'WARNING 🟡'
    else:
        overall_status = 'OK 🟢'
        
    print(f"\n🎯 FINAL SYSTEM STATUS: {overall_status}\n")
    return {'resources': resources, 'db': db_check, 'logs': log_analysis}

if __name__ == "__main__":
    run_full_health_check()