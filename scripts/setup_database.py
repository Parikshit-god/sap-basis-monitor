import os
import sqlite3
from datetime import date, timedelta

# Get the directory where this script is located (scripts folder)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the main sap_basis_monitor folder
project_root = os.path.dirname(script_dir) 

# Step 2.2: Define the exact path for the SQLite database
db_path = os.path.join(project_root, "data", "sap_system.db")

# Connect to SQLite and create the file
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Step 2.3: Create all three tables with required schemas
cursor.executescript("""
CREATE TABLE IF NOT EXISTS USR02 (
    MANDT TEXT DEFAULT '100',
    BNAME TEXT PRIMARY KEY,
    GLTGV TEXT,
    GLTGB TEXT,
    USTYP TEXT,
    CLASS TEXT,
    UFLAG INTEGER DEFAULT 0,
    TRDAT TEXT,
    LTIME TEXT,
    ERDAT TEXT,
    BCODE INTEGER DEFAULT 0,
    DEPARTMENT TEXT,
    EMAIL TEXT
);

CREATE TABLE IF NOT EXISTS SMSLOG (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    TIMESTAMP TEXT,
    SYSTEM_ID TEXT,
    CPU_USAGE REAL,
    RAM_USAGE REAL,
    DISK_USAGE REAL,
    DB_LATENCY_MS REAL,
    ALERT_FLAGS TEXT,
    STATUS TEXT
);

CREATE TABLE IF NOT EXISTS SECURITY_AUDIT (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    TIMESTAMP TEXT,
    USERNAME TEXT,
    VIOLATION_TYPE TEXT,
    ACTION_TAKEN TEXT,
    SEVERITY TEXT,
    RESOLVED INTEGER DEFAULT 0
);
""")

# Clear existing user data if this script is run more than once
cursor.execute("DELETE FROM USR02")

# Step 2.4: Prepare dynamic date calculations so data is always relevant to "today"
today = date.today()
future_date = (today + timedelta(days=365)).strftime('%Y-%m-%d')
expired_date = (today - timedelta(days=5)).strftime('%Y-%m-%d')

past_100 = (today - timedelta(days=100)).strftime('%Y-%m-%d') # >90 days ago
past_60 = (today - timedelta(days=60)).strftime('%Y-%m-%d')   # 30-89 days ago
past_10 = (today - timedelta(days=10)).strftime('%Y-%m-%d')   # <30 days ago
created_date = (today - timedelta(days=200)).strftime('%Y-%m-%d')

# Define exactly 25 users meeting all the precise security scenarios
users = [
    # 6 users inactive > 90 days (Includes 2 expired accounts and 2 technical users)
    ('JSMITH',      future_date, expired_date, 'A', 'ENDUSER', 0, past_100, '08:00:00', created_date, 0, 'Finance', 'jsmith@company.com'),
    ('ABAUER',      future_date, expired_date, 'A', 'ENDUSER', 0, past_100, '09:15:00', created_date, 0, 'HR', 'abauer@company.com'),
    ('RFC_CONNECT', future_date, future_date,  'B', 'BASIS',   0, past_100, '23:00:00', created_date, 0, 'IT', 'rfc@company.com'),
    ('BATCH_USER',  future_date, future_date,  'B', 'BASIS',   0, past_100, '01:00:00', created_date, 0, 'Basis', 'batch@company.com'),
    ('MWILSON',     future_date, future_date,  'A', 'ENDUSER', 0, past_100, '10:30:00', created_date, 0, 'Logistics', 'mwilson@company.com'),
    ('PATEL_R',     future_date, future_date,  'A', 'ENDUSER', 0, past_100, '14:45:00', created_date, 0, 'Finance', 'rpatel@company.com'),
    
    # 4 users inactive 30-89 days
    ('HRUSER01',    future_date, future_date,  'A', 'ENDUSER', 0, past_60,  '08:30:00', created_date, 0, 'HR', 'hr01@company.com'),
    ('LCHEN',       future_date, future_date,  'A', 'ENDUSER', 0, past_60,  '11:20:00', created_date, 0, 'IT', 'lchen@company.com'),
    ('SRODRIGUEZ',  future_date, future_date,  'A', 'BASIS',   0, past_60,  '16:00:00', created_date, 0, 'Basis', 'srodriguez@company.com'),
    ('TJONES',      future_date, future_date,  'A', 'ENDUSER', 0, past_60,  '09:45:00', created_date, 0, 'Logistics', 'tjones@company.com'),
    
    # 5 active users logged in within the last 30 days
    ('KLEE',        future_date, future_date,  'A', 'ENDUSER', 0, past_10,  '08:05:00', created_date, 0, 'Finance', 'klee@company.com'),
    ('SAP_ADMIN',   future_date, future_date,  'A', 'SUPER',   0, past_10,  '07:30:00', created_date, 0, 'Basis', 'admin@company.com'),
    ('RWHITE',      future_date, future_date,  'A', 'ENDUSER', 0, past_10,  '09:10:00', created_date, 0, 'HR', 'rwhite@company.com'),
    ('MGARCIA',     future_date, future_date,  'A', 'ENDUSER', 0, past_10,  '10:15:00', created_date, 0, 'IT', 'mgarcia@company.com'),
    ('DCLARK',      future_date, future_date,  'A', 'ENDUSER', 0, past_10,  '13:20:00', created_date, 0, 'Logistics', 'dclark@company.com'),
    
    # 3 users who have NEVER logged in (TRDAT is an empty string)
    ('NEWUSER1',    future_date, future_date,  'A', 'ENDUSER', 0, '',       '',         created_date, 0, 'Finance', 'nu1@company.com'),
    ('NEWUSER2',    future_date, future_date,  'A', 'ENDUSER', 0, '',       '',         created_date, 0, 'HR', 'nu2@company.com'),
    ('NEWUSER3',    future_date, future_date,  'A', 'ENDUSER', 0, '',       '',         created_date, 0, 'IT', 'nu3@company.com'),
    
    # 4 users with excessive failed login attempts (BCODE > 5)
    ('BSMITH',      future_date, future_date,  'A', 'ENDUSER', 0, past_10,  '08:00:00', created_date, 6, 'Basis', 'bsmith@company.com'),
    ('ADAVIS',      future_date, future_date,  'A', 'ENDUSER', 0, past_10,  '08:00:00', created_date, 7, 'Logistics', 'adavis@company.com'),
    ('EMARTIN',     future_date, future_date,  'A', 'ENDUSER', 0, past_10,  '08:00:00', created_date, 8, 'Finance', 'emartin@company.com'),
    ('JTHOMAS',     future_date, future_date,  'A', 'ENDUSER', 0, past_10,  '08:00:00', created_date, 9, 'HR', 'jthomas@company.com'),
    
    # 3 users already marked as LOCKED (UFLAG = 64)
    ('LOCKED01',    future_date, future_date,  'A', 'ENDUSER', 64, past_10, '08:00:00', created_date, 0, 'IT', 'lock1@company.com'),
    ('LOCKED02',    future_date, future_date,  'A', 'ENDUSER', 64, past_10, '08:00:00', created_date, 0, 'Basis', 'lock2@company.com'),
    ('BAD_ACTOR',   future_date, future_date,  'A', 'ENDUSER', 64, past_10, '08:00:00', created_date, 0, 'Logistics', 'bad@company.com')
]

# Insert the data
for u in users:
    cursor.execute("""
        INSERT INTO USR02 (
            MANDT, BNAME, GLTGV, GLTGB, USTYP, CLASS, UFLAG, TRDAT, LTIME, ERDAT, BCODE, DEPARTMENT, EMAIL
        ) VALUES ('100', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, u)

# Save changes to the database
conn.commit()

# Step 2.5: Verification Summary
cursor.execute("SELECT COUNT(*) FROM USR02")
total_users = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM USR02 WHERE UFLAG = 64")
locked_users = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM USR02 WHERE BCODE > 5")
failed_logins = cursor.fetchone()[0]

print("✅ SAP Database successfully created at:", db_path)
print("📊 Summary of inserted data:")
print(f"   - Total Users Inserted: {total_users}")
print(f"   - Users currently Locked (UFLAG=64): {locked_users}")
print(f"   - Users with Excessive Failed Logins (BCODE>5): {failed_logins}")
print("   - All 3 tables (USR02, SMSLOG, SECURITY_AUDIT) created successfully.")

# Close connection
conn.close()