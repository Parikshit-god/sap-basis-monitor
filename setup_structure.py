import os

# Get the directory where this script is located (sap_basis_monitor)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Step 1.2: Define the folder structure
folders_to_create = [
    "sapmnt/PRD/profile",
    "sapmnt/PRD/trans",
    "sapmnt/PRD/logs",
    "sapmnt/QAS/profile",
    "sapmnt/QAS/logs",
    "sapmnt/DEV/profile",
    "sapmnt/DEV/logs",
    "usr/sap/PRD/SYS",
    "usr/sap/PRD/work",
    "data",
    "reports",
    "scripts",
    "templates"
]

for folder in folders_to_create:
    folder_path = os.path.join(base_dir, *folder.split('/'))
    os.makedirs(folder_path, exist_ok=True)

# Step 1.3: Create dummy SAP System Log file
log_content = """2024-01-15 08:00:00 [PRD] [INFO] System startup initiated.
2024-01-15 08:05:12 [PRD] [INFO] Background jobs scheduler started.
2024-01-15 08:10:00 [PRD] [INFO] User logon load balancer active.
2024-01-15 08:15:33 [PRD] [WARNING] High CPU usage detected on app server 1.
2024-01-15 08:20:11 [PRD] [WARNING] Spool queue filling up.
2024-01-15 08:21:05 [PRD] [WARNING] Long running dialog step detected.
2024-01-15 08:23:11 [PRD] [CRITICAL] Database connection lost - reconnecting attempt 1 of 5.
2024-01-15 08:23:15 [PRD] [CRITICAL] Database connection lost - reconnecting attempt 2 of 5.
2024-01-15 08:23:20 [PRD] [CRITICAL] Database connection lost - reconnecting attempt 3 of 5.
2024-01-15 08:24:01 [PRD] [DB_ERROR] ORA-03113: end-of-file on communication channel.
2024-01-15 08:24:05 [PRD] [DB_ERROR] TNS-12540: TNS:internal limit restriction exceeded.
2024-01-15 08:24:10 [PRD] [DB_ERROR] SQL error 1034 occurred while accessing program SAPMSSY1.
2024-01-15 08:25:00 [PRD] [INFO] Database reconnected successfully.
2024-01-15 08:30:00 [PRD] [MEMORY_LOW] Extended memory usage above 90%.
2024-01-15 08:35:00 [PRD] [MEMORY_LOW] Heap memory allocation failed - entering PRIV mode.
2024-01-15 08:40:00 [PRD] [MEMORY_LOW] Roll buffer exhausted.
2024-01-15 08:45:00 [PRD] [INFO] System memory garbage collection completed.
2024-01-15 08:50:00 [PRD] [INFO] Workprocess restart - WP 0 restarted by dispatcher.
2024-01-15 08:55:00 [PRD] [INFO] Workprocess restart - WP 5 restarted after crash.
2024-01-15 09:00:00 [PRD] [INFO] Workprocess restart - WP 12 restarted gracefully.
2024-01-15 09:05:00 [PRD] [INFO] System checkpoint written to database.
2024-01-15 09:10:00 [PRD] [INFO] Transport tp process completed.
2024-01-15 09:15:00 [PRD] [INFO] Buffer synchronization triggered.
2024-01-15 09:20:00 [PRD] [CRITICAL] Update process failed - records stuck in SM13.
2024-01-15 09:25:00 [PRD] [WARNING] Certificate expiring in 14 days for STRUST.
2024-01-15 09:30:00 [PRD] [DB_ERROR] Table locks exceeded maximum limit.
2024-01-15 09:35:00 [PRD] [MEMORY_LOW] OS paging space critical.
2024-01-15 09:40:00 [PRD] [INFO] Archiving session completed.
2024-01-15 09:45:00 [PRD] [WARNING] Background job SAP_COLLECTOR_FOR_PERFMON failed.
2024-01-15 09:50:00 [PRD] [INFO] Workprocess restart - WP 2 terminated by administrator.
2024-01-15 09:55:00 [PRD] [CRITICAL] Database connection lost - network timeout.
2024-01-15 10:00:00 [PRD] [INFO] User lock table cleanup started.
2024-01-15 10:05:00 [PRD] [INFO] Security audit log saved.
2024-01-15 10:10:00 [PRD] [WARNING] Failed logon attempt for user SAP* from terminal T1.
2024-01-15 10:15:00 [PRD] [CRITICAL] Database connection lost - node failover initiated.
2024-01-15 10:20:00 [PRD] [DB_ERROR] Deadlock detected during update transaction.
2024-01-15 10:25:00 [PRD] [MEMORY_LOW] Out of memory error in ABAP program SAPLSMTR_NAVIGATION.
2024-01-15 10:30:00 [PRD] [INFO] Temporary files cleared from /usr/sap/PRD/work.
2024-01-15 10:35:00 [PRD] [INFO] Standard jobs completed successfully.
2024-01-15 10:40:00 [PRD] [INFO] System log switched to new file.
"""

log_path = os.path.join(base_dir, "sapmnt", "PRD", "logs", "SM21_log.txt")
with open(log_path, "w") as log_file:
    log_file.write(log_content)

# Step 1.4: Create mock SAP profile config file
profile_content = """# DEFAULT.PFL - SAP System Profile
system/type = ABAP
SAPSYSTEMNAME = PRD
SAPSYSTEM = 00
INSTANCE_NAME = DVEBMGS00
DIR_PROFILE = /sapmnt/PRD/profile
DIR_EXECUTABLE = /usr/sap/PRD/SYS/exe/run
rdisp/wp_no_dia = 30
rdisp/wp_no_btc = 10
rdisp/wp_no_enq = 1
rdisp/wp_no_spo = 2
rdisp/wp_no_vb = 4
rdisp/wp_no_vb2 = 2
icm/server_port_0 = PROT=HTTP,PORT=8000,TIMEOUT=60,PROCTIMEOUT=600
icm/max_conn = 500
login/min_password_lng = 8
login/fails_to_session_end = 3
login/fails_to_user_lock = 5
ztta/roll_extension = 2000000000
em/initial_size_MB = 4096
"""

profile_path = os.path.join(base_dir, "sapmnt", "PRD", "profile", "DEFAULT.PFL")
with open(profile_path, "w") as profile_file:
    profile_file.write(profile_content)

print("✅ SAP structure and mock files successfully created!")