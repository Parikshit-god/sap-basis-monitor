import argparse
import schedule
import time
import os
import sys
import subprocess
from datetime import datetime

# Add the current directory to sys.path so we can import from the scripts folder
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import our custom modules
from scripts.basis_health_check import run_full_health_check
from scripts.user_access_auditor import run_full_audit
from scripts.generate_pdf_report import generate_pdf

def print_banner():
    banner = """
  ╔════════════════════════════════════════════════╗
  ║   SAP BASIS INFRASTRUCTURE AUTOMATION TOOL     ║
  ║   Version 1.0 | SAP ERP Monitoring System      ║
  ╚════════════════════════════════════════════════╝
    """
    print(banner)

def run_once():
    print(f"\n🚀 [STARTING MANUAL RUN] - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    run_full_health_check()
    run_full_audit()
    generate_pdf()
    print("\n✅ All manual tasks completed successfully.")

def scheduled_job():
    print("\n\n" + "="*50)
    print(f"=== ⏰ SCHEDULED AUTOMATION RUN STARTING === ")
    print(f"=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print("="*50)
    run_full_health_check()
    run_full_audit()
    generate_pdf()
    print("\n✅ Scheduled run completed.")

def run_schedule():
    print("\n⏳ Starting background scheduler...")
    print("⚙️  Tasks will run immediately, and then every 30 minutes.")
    
    # Schedule the job every 30 minutes
    schedule.every(30).minutes.do(scheduled_job)
    
    # Run it once immediately upon startup
    scheduled_job()
    
    # Keep the script running and print a live countdown
    try:
        while True:
            idle_seconds = schedule.idle_seconds()
            if idle_seconds is None:
                break
            elif idle_seconds > 0:
                mins, secs = divmod(int(idle_seconds), 60)
                # Use \r to overwrite the same line in the terminal for a live countdown
                print(f"\r⏳ Next scheduled run in: {mins:02d}:{secs:02d} (Press Ctrl+C to stop) ... ", end="")
                time.sleep(1)
            schedule.run_pending()
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped by user. Exiting gracefully.")
        sys.exit(0)

def launch_dashboard():
    print("\n🌐 Launching Streamlit Web Dashboard...")
    dashboard_path = os.path.join(project_root, "scripts", "dashboard.py")
    try:
        # Run streamlit as a subprocess
        subprocess.run(["streamlit", "run", dashboard_path])
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user.")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="SAP Basis Infrastructure & Monitoring Automation Tool")
    
    # Define the command-line flags
    parser.add_argument("--once", action="store_true", help="Run one health check + one audit, generate PDF, then exit")
    parser.add_argument("--dashboard", action="store_true", help="Launch the Streamlit web dashboard")
    parser.add_argument("--schedule", action="store_true", help="Run health checks every 30 minutes continuously")
    
    args = parser.parse_args()
    
    print_banner()

    # Determine which mode to run based on arguments
    if args.schedule:
        run_schedule()
    elif args.dashboard:
        launch_dashboard()
    elif args.once:
        run_once()
    else:
        # Default behavior if no arguments are provided
        print("ℹ️  No mode specified. Defaulting to '--once' mode.\n")
        run_once()

if __name__ == "__main__":
    main()