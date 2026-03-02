import pandas as pd
import os
from datetime import datetime, timedelta

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGBOOK_PATH = os.path.join(PROJECT_ROOT, 'data', 'logbook.csv')
README_PATH = os.path.join(PROJECT_ROOT, 'README.md')

def predict_sunday_volume():
    # 1. Load Data
    if not os.path.exists(LOGBOOK_PATH):
        print("❌ Error: logbook.csv not found.")
        return

    df = pd.read_csv(LOGBOOK_PATH)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 2. Analyze the Last 7 Days (The 'Pain Audit')
    today = pd.to_datetime('2026-03-02')
    last_7_days = df[df['Date'] > (today - timedelta(days=7))]
    
    max_pain = last_7_days['Pain Score'].max() if not last_7_days.empty else 0
    
    # 3. Get Last Sunday's Volume
    sundays = df[df['Date'].dt.dayofweek == 6].sort_values('Date', ascending=False)
    last_sunday_km = sundays.iloc[0]['Distance (km)'] if not sundays.empty else 10.0

    # 4. Calculation Logic (Brutally Honest)
    if max_pain > 0:
        # If there was pain, we do NOT increase. Safety first for Sub-3:15.
        target_km = last_sunday_km
        reason = f"HOLD (Pain detected: {max_pain}/10)"
        color = "#FFD700" # Warning Yellow
    else:
        # 10% Progressive Overload
        target_km = round(last_sunday_km * 1.1, 1)
        reason = "PROGRESS (0/10 Pain Zone)"
        color = "#FF3E3E" # Racing Red

    print(f"📊 Last Sunday: {last_sunday_km}km | Pain: {max_pain}/10")
    print(f"🚀 Target for March 8: {target_km}km ({reason})")

    update_readme_chart(target_km, reason, color)

def update_readme_chart(km, status, color):
    # This function finds the mermaid block and injects the new data
    with open(README_PATH, 'r') as f:
        content = f.read()

    # Simple text replacement for the Mermaid block labels (March 8 Focus)
    new_chart = f"""```mermaid
graph LR
    Mon["Mon (Core)"] --> Tue["Tue (Rest)"] --> Wed["Wed (Run)"] --> Thu["Thu (Core)"] --> Fri["Fri (Rest)"] --> Sat["Sat (Run)"] --> Sun["Sun ({km}km - {status})"]
    style Sun fill:{color},stroke:#fff,stroke-width:2px;
```"""

    # We use a marker or regex to replace the old block
    import re
    pattern = r"```mermaid[\s\S]*?```"
    updated_content = re.sub(pattern, new_chart, content)

    with open(README_PATH, 'w') as f:
        f.write(updated_content)
    print("🏠 README.md chart updated.")

if __name__ == "__main__":
    predict_sunday_volume()