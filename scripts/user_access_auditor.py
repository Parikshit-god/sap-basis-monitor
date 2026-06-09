import os
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta

# Setup dynamic paths relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
db_path = os.path.join(project_root, "data", "sap_system.db")
reports_dir = os.path.join(project_root, "reports")

def get_all_users(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM USR02", conn)
    conn.close()
    print(f"  Loaded {len(df)} total users from the database.")
    return df

def find_inactive_users(df, days_threshold=90):
    cutoff_date = (date.today() - timedelta(days=days_threshold)).strftime('%Y-%m-%d')
    
    # Condition: Inactive > 90 days OR never logged in (TRDAT is empty string)
    inactive_mask = (df['TRDAT'] < cutoff_date) | (df['TRDAT'] == '')
    # Condition: Not already locked
    unlocked_mask = ~df['UFLAG'].isin([64, 128])
    
    inactive_users = df[inactive_mask & unlocked_mask]['BNAME'].tolist()
    print(f"  Found {len(inactive_users)} inactive users (last login > {days_threshold} days ago or never).")
    return inactive_users

def find_excessive_failed_logins(df, max_attempts=5):
    failed_mask = df['BCODE'] > max_attempts
    unlocked_mask = ~df['UFLAG'].isin([64, 128])
    
    # Extract as a list of tuples: [(username, attempts), ...]
    failed_users = df[failed_mask & unlocked_mask][['BNAME', 'BCODE']].values.tolist()
    failed_users = [(row[0], int(row[1])) for row in failed_users]
    
    print(f"  Found {len(failed_users)} users with excessive failed login attempts.")
    return failed_users

def find_expired_accounts(df):
    today_str = date.today().strftime('%Y-%m-%d')
    
    expired_mask = (df['GLTGB'] != '') & (df['GLTGB'] < today_str)
    unlocked_mask = ~df['UFLAG'].isin([64, 128])
    
    expired_users = df[expired_mask & unlocked_mask]['BNAME'].tolist()
    print(f"  Found {len(expired_users)} expired accounts.")
    return expired_users

def auto_lock_inactive_users(db_path, inactive_usernames):
    if not inactive_usernames:
        return 0
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0
    
    for username in inactive_usernames:
        cursor.execute("UPDATE USR02 SET UFLAG = 64 WHERE BNAME = ?", (username,))
        cursor.execute("""
            INSERT INTO SECURITY_AUDIT (TIMESTAMP, USERNAME, VIOLATION_TYPE, ACTION_TAKEN, SEVERITY, RESOLVED)
            VALUES (?, ?, 'INACTIVE_90_DAYS', 'AUTO_LOCKED', 'MEDIUM', 0)
        """, (timestamp, username))
        print(f"  LOCKED: {username} — Reason: No login for 90+ days")
        count += 1
        
    conn.commit()
    conn.close()
    print(f"  Auto-locked {count} user accounts.")
    return count

def flag_suspicious_logins(db_path, failed_login_users):
    if not failed_login_users:
        return 0
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0
    
    for username, attempts in failed_login_users:
        cursor.execute("""
            INSERT INTO SECURITY_AUDIT (TIMESTAMP, USERNAME, VIOLATION_TYPE, ACTION_TAKEN, SEVERITY, RESOLVED)
            VALUES (?, ?, 'FAILED_LOGIN_ATTEMPTS', 'FLAGGED_FOR_REVIEW', 'HIGH', 0)
        """, (timestamp, username))
        print(f"  FLAGGED: {username} — Reason: {attempts} failed login attempts")
        count += 1
        
    conn.commit()
    conn.close()
    print(f"  Flagged {count} accounts for review (Failed Logins).")
    return count

def flag_expired_accounts(db_path, expired_usernames):
    if not expired_usernames:
        return 0
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0
    
    for username in expired_usernames:
        cursor.execute("""
            INSERT INTO SECURITY_AUDIT (TIMESTAMP, USERNAME, VIOLATION_TYPE, ACTION_TAKEN, SEVERITY, RESOLVED)
            VALUES (?, ?, 'EXPIRED_ACCOUNT', 'FLAGGED_FOR_REVIEW', 'MEDIUM', 0)
        """, (timestamp, username))
        print(f"  FLAGGED: {username} — Reason: Account validity date expired")
        count += 1
        
    conn.commit()
    conn.close()
    print(f"  Flagged {count} accounts for review (Expired).")
    return count

def generate_audit_report(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get user statistics
    cursor.execute("SELECT COUNT(*) FROM USR02")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM USR02 WHERE UFLAG = 0")
    active_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM USR02 WHERE UFLAG IN (64, 128)")
    locked_users = cursor.fetchone()[0]
    
    # Get unresolved violations
    cursor.execute("SELECT USERNAME, VIOLATION_TYPE, ACTION_TAKEN, SEVERITY, TIMESTAMP FROM SECURITY_AUDIT WHERE RESOLVED = 0")
    violations = cursor.fetchall()
    
    conn.close()
    
    timestamp_for_file = datetime.now().strftime("%Y-%m-%d")
    timestamp_for_header = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    filename = f"audit_report_{timestamp_for_file}.txt"
    filepath = os.path.join(reports_dir, filename)

    active_pct = (active_users / total_users * 100) if total_users > 0 else 0
    locked_pct = (locked_users / total_users * 100) if total_users > 0 else 0

    lines = []
    lines.append("SAP BASIS SECURITY AUDIT REPORT")
    lines.append(f"Generated: {timestamp_for_header}")
    lines.append("==================================================")
    
    lines.append("\nUSER ACCOUNT SUMMARY")
    lines.append(f"  Total Users:  {total_users}")
    lines.append(f"  Active Users: {active_users} ({active_pct:.1f}%)")
    lines.append(f"  Locked Users: {locked_users} ({locked_pct:.1f}%)")
    
    lines.append("\nSECURITY VIOLATIONS DETECTED THIS RUN")
    if violations:
        lines.append(f"{'USERNAME':<15} | {'VIOLATION TYPE':<25} | {'ACTION':<20} | {'SEVERITY':<10}")
        lines.append("-" * 80)
        for v in violations:
            lines.append(f"{v[0]:<15} | {v[1]:<25} | {v[2]:<20} | {v[3]:<10}")
    else:
        lines.append("  No unresolved security violations found.")

    lines.append("\n==================================================")
    lines.append("End of Audit Report")

    with open(filepath, 'w') as file:
        file.write('\n'.join(lines))
        
    print(f"📄 Audit Report saved to: {os.path.relpath(filepath, project_root)}")
    return filepath

def run_full_audit():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n  ================================================")
    print("  === SAP BASIS USER ACCESS SECURITY AUDIT     ===")
    print(f"  === {current_time:<40} ===")
    print("  ================================================")

    df = get_all_users(db_path)
    
    print("\n[Running: Violation Detection]")
    inactive_users = find_inactive_users(df)
    failed_logins = find_excessive_failed_logins(df)
    expired_users = find_expired_accounts(df)
    
    print("\n[Running: Automated Mitigation]")
    locked_count = auto_lock_inactive_users(db_path, inactive_users)
    flagged_fail_count = flag_suspicious_logins(db_path, failed_logins)
    flagged_exp_count = flag_expired_accounts(db_path, expired_users)
    
    print("\n[Running: Report Generation]")
    report_path = generate_audit_report(db_path)
    
    total_actions = locked_count + flagged_fail_count + flagged_exp_count
    print(f"\n🎯 FINAL AUDIT SUMMARY: {total_actions} security actions taken.\n")
    
    return {
        'inactive': inactive_users,
        'failed': failed_logins,
        'expired': expired_users,
        'actions_taken': total_actions,
        'report_path': report_path
    }

if __name__ == "__main__":
    run_full_audit()