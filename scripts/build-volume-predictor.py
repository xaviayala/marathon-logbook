import pandas as pd
import os
from datetime import datetime, timedelta
import re

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Corrected to match your actual filename
LOGBOOK_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed_logbook.csv')
README_PATH = os.path.join(PROJECT_ROOT, 'README.md')

def predict_sunday_volume():
    # 1. Load Data
    if not os.path.exists(LOGBOOK_PATH):
        print(f"❌ Error: {LOGBOOK_PATH} not found.")
        return

    df = pd.read_csv(LOGBOOK_PATH)
    
    # 🟢 CLINICAL FIX: Clean headers and match CSV exactly
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 2. Analyze the Last 7 Days (The 'Pain Audit')
    # Using March 3, 2026 as 'today' based on current project timeline
    today = pd.to_datetime('2026-03-03') 
    last_7_days = df[df['Date'] > (today - timedelta(days=7))]
    
    # Corrected field: 'Pain_Score' 
    max_pain = last_7_days['Pain_Score'].max() if not last_7_days.empty else 0
    
    # 3. Get Last Sunday's Volume
    # Filter for Sunday and specifically for 'Running' activities to avoid bike interference
    sundays = df[(df['Date'].dt.dayofweek == 6) & (df['Activity Type'] == 'Running')].sort_values('Date', ascending=False)
    
    # Corrected field: 'Distance' 
    last_sunday_km = sundays.iloc[0]['Distance'] if not sundays.empty else 21.1

    # 4. Calculation Logic (Progressive Overload)
    if max_pain > 0:
        target_km = last_sunday_km
        status = f"HOLD (Pain: {int(max_pain)}/10)"
        color = "#FFD700" # Warning Yellow
    else:
        target_km = round(last_sunday_km * 1.1, 1)
        status = "PROGRESS (0/10 Pain)"
        color = "#FCA311" # 🟧 Easy-on-the-eyes Orange

    print(f"📊 Last Sunday: {last_sunday_km}km | Max Pain (7d): {max_pain}/10")
    print(f"🚀 Target for March 8: {target_km}km ({status})")

    update_readme_chart(target_km, status, color)

def update_readme_chart(km, status, color):
    with open(README_PATH, 'r') as f:
        content = f.read()

    # The Mermaid structure with proper new lines for VS Code syntax
    new_chart = f"""```mermaid
graph LR
    Mon["Mon (Core)"] --> Tue["Tue (Rest)"]
    Tue --> Wed["Wed (Run)"]
    Wed --> Thu["Thu (Core)"]
    Thu --> Fri["Fri (Rest)"]
    Fri --> Sat["Sat (Run)"]
    Sat --> Sun["Sun ({km}km - {status})"]
    style Sun fill:{color},stroke:#fff,stroke-width:2px;
"""
    # Replace content between markers
    pattern = r"[\s\S]*?"
    if re.search(pattern, content):
        updated_content = re.sub(pattern, new_chart, content)
        with open(README_PATH, 'w') as f:
            f.write(updated_content)
        print("🏠 README.md chart updated successfully.")
    else:
        print("⚠️ Warning: Markers not found. Updating entire file (check README for syntax).")

    if __name__ == "__main__":
        predict_sunday_volume()