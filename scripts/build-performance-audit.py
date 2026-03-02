import os
import sys
import pandas as pd
import ui_manager
from google import genai
from dotenv import load_dotenv
from datetime import datetime

# ---------------------------------
# 1. PATH RESOLUTION
# ---------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Directories
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
HISTORY_DIR = os.path.join(DOCS_DIR, 'history')
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed_logbook.csv')

# Files
LATEST_AUDIT_FILE = os.path.join(DOCS_DIR, 'audit.md')

# Ensure the history directory exists
os.makedirs(HISTORY_DIR, exist_ok=True)

# ---------------------------------
# 2. SETUP
# ---------------------------------
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_training(dry_run=False):
    try:
        if not os.path.exists(DATA_PATH):
            print(f"❌ Error: {DATA_PATH} not found.")
            return

        df = pd.read_csv(DATA_PATH)
        recent_data = df.head(7).to_string()

        if dry_run:
            print("🧪 DRY RUN MODE: Skipping API call.")
            audit_content = "### [DRY RUN AUDIT]\nThis is a mock response to test file saving and archiving logic. No API quota was consumed."
        else:
            # Load the data you uploaded        
            df = pd.read_csv(DATA_PATH)
            # Get last 7 days of data
            recent_data = df.head(7).to_string()

            prompt = f"""
            You are a brutally honest elite marathon coach. Analyze this training data:
            {recent_data}
            
            Context: Athlete 45+, targeting sub-3:15 marathon and sub-1:30 half. -10kg weight loss in last 6 months (due to training). 
            Constraint: Only trains Wed/Thu, Sat, Sun. Rest is Isometrics/Core/Glute.
            The goal is to prove 'Pain-Free' progress after a 10kg loss.
            
            Task: Write a 200-Word Status Update for the Project README
            Objective: Provide a transparent, data-driven update on recent training, emphasizing pain-free progress.
            Guidelines:
                - Report weekly or recent training, including distance (km), pace, heart rate, and perceived effort.
                - Be honest: call out if Aerobic Training Effect (TE) is too high for the pace.
                - Highlight the relationship between distance and lack of pain — zero pain scores (0/10).
                - Analyze pace versus heart rate efficiency, identifying where intensity may exceed sustainable levels.
                - Emphasize consistency and durability over speed when necessary.
                - Document lessons learned and actionable insights to guide future training.
                - Maintain a focus on sustainable, pain-free progress while tracking measurable metrics.
                - Deliverable: A 200-word update that balances honesty, performance analysis, and reflections on pain-free consistency.
            """

            # 3. GENERATE CONTENT (The modern syntax)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            audit_content = response.text

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        datestamp = datetime.now().strftime('%Y-%m-%d')

        # 4. PREPARE OUTPUTS
        now = datetime.now()
        timestamp_ui = now.strftime('%Y-%m-%d %H:%M')    # For inside the file
        timestamp_file = now.strftime('%Y-%m-%d_%H-%M')  # For the filename (YYYY-MM-DD_HH-MM)

        report_header = f"# 🧠 Performance Audit\n\n> **Last Updated:** {timestamp_ui}\n\n"
        full_report = report_header + audit_content

      # 5. WRITE OUTPUTS
        # A. Update Latest Dashboard
        with open(LATEST_AUDIT_FILE, 'w', encoding='utf-8') as f:
            f.write(full_report)

        # B. Archive with Unique Timestamp
        history_path = os.path.join(HISTORY_DIR, f"audit-{timestamp_file}.md")
        with open(history_path, 'w', encoding='utf-8') as f:
            f.write(f"# Historical Audit: {timestamp_ui}\n\n" + audit_content)

        print(f"✅ Dashboard updated: {LATEST_AUDIT_FILE}")
        print(f"📂 Archive created: {history_path}")
        
        # 6. REBUILD SIDEBAR
        ui_manager.update_sidebar()
    
    except FileNotFoundError:
        print("❌ Error: 'data/processed_logbook.csv' not found.")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    # Check if "--dry-run" was passed in the command line
    is_dry = "--dry-run" in sys.argv
    analyze_training(dry_run=is_dry)