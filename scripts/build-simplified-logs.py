import os
import pandas as pd
import sys

# ---------------------------------
# 1. PATH RESOLUTION
# ---------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Target: Inside /docs/logs/simplified
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed_logbook.csv')
OUTPUT_DIR = os.path.join(DOCS_DIR, 'logs', 'simplified')

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------
# 2. DATA LOAD
# ---------------------------------
if not os.path.exists(DATA_PATH):
    print(f"❌ ERROR: {DATA_PATH} not found.")
    sys.exit(1)

df = pd.read_csv(DATA_PATH)
df['Date'] = pd.to_datetime(df['Date'])

# ---------------------------------
# 3. PROCESSING LOOP (Zero API Cost)
# ---------------------------------
print(f"📋 Generating Simplified Logs in {OUTPUT_DIR}...")

for index, row in df.iterrows():
    date_str = row['Date'].strftime('%Y-%m-%d')
    file_name = f"{date_str}.md"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    
    # Simple summary format for quick mobile viewing
    content = f"""# 📝 Log: {date_str}
    
## 🏃 Activity
- **Type:** {row['Activity Type']}
- **Distance:** {row['Distance']} km
- **Avg Pace:** {row['Avg Pace']} min/km
- **Aerobic TE:** {row['Aerobic TE']}

## 🦴 Status
- **Pain Score:** 0/10 ✅
- **Recovery Status:** Optimized

[View Detailed Analysis](../detailed/{date_str}-run.md)
"""

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"✅ Created {len(df)} simplified logs.")