# SAP Basis Infrastructure & Monitoring Automation Tool

This tool simulates and automates the critical daily tasks of an SAP Basis Administrator. It generates a mock SAP folder structure, evaluates live system resources (CPU, RAM, Disk), monitors database latency, analyzes mock SAP system logs (SM21), audits user accounts for security violations, auto-locks compromised accounts, and serves all this data via an interactive local web dashboard and automated PDF reports.

## Live Demo
<img width="800" height="450" alt="SAPBasisInfrastructureMonitorStreamlit-GoogleChrome2026-06-0916-23-20-ezgif com-video-to-gif-converter" src="https://github.com/user-attachments/assets/12715388-da36-453d-a084-02feeb410c4d" />


## Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

## Setup Instructions (5 Steps to Run)
1. **Clone/Download** this project folder to your local machine.
2. **Open a terminal** and navigate into the `sap_basis_monitor` directory.
3. **Create a virtual environment:** run `python -m venv venv`.
4. **Activate the virtual environment:** run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux).
5. **Install dependencies:** run `pip install -r requirements.txt`.

## How to Run Modes
- **Single Run:** `python main.py --once` (Runs one health check, one audit, generates PDF, and exits).
- **Scheduled Run:** `python main.py --schedule` (Runs automatically every 30 minutes in the background).
- **Dashboard:** `python main.py --dashboard` (Launches the interactive web UI).
- **Default:** `python main.py` (Same as `--once`).

## Folder Structure
```text
sap_basis_monitor/
├── data/                  # Contains the SQLite database (sap_system.db)
├── reports/               # Output folder for text and PDF daily reports
├── sapmnt/                # Mock SAP landscape (DEV, QAS, PRD configurations and logs)
├── scripts/               # Core Python automation scripts and dashboard logic
├── usr/                   # Mock SAP system executable paths
├── main.py                # Master entry point and scheduler
├── requirements.txt       # Locked Python dependencies
└── README.md              # Project documentation
