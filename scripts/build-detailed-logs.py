import os
import pandas as pd
import time
import sys
from google import genai
from dotenv import load_dotenv

# ---------------------------------
# 1. PATH RESOLUTION (The Sub-3:15 Standard)
# ---------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# New Target: Inside /docs/logs/detailed
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed_logbook.csv')
OUTPUT_DIR = os.path.join(DOCS_DIR, 'logs', 'detailed')

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------
# 2. AUTHENTICATION & CLIENT SETUP
# ---------------------------------
load_dotenv() 
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: No API Key found in .env.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# Clinical System Instruction
system_instruction = (
    "You are a professional Sports Performance Analyst. Your tone is brutally honest, "
    "clinical, and data-driven. Analyze logs for a 45+ year old runner aiming for a "
    "sub-3:15 marathon. Focus on metabolic efficiency and structural integrity. "
    "Always use the metric system (km)."
)

# ---------------------------------
# 3. DATA LOAD & TEMPLATE
# ---------------------------------
if not os.path.exists(DATA_PATH):
    print(f"❌ ERROR: {DATA_PATH} not found.")
    sys.exit(1)

df = pd.read_csv(DATA_PATH)
df['Date'] = pd.to_datetime(df['Date'])
# Filter for your specific research window
df = df[(df['Date'] >= '2025-09-01') & (df['Date'] <= '2026-03-01')]

detailed_tpl = """# 🏃 Session: {title}
**Date:** {date}
**Phase:** {phase}

## 📊 Quantitative Data (Metric)
- **Distance:** {distance} km
- **Target Pace:** {target_pace} min/km
- **Actual Pace:** {actual_pace} min/km
- **Avg Heart Rate:** {hr} bpm
- **Shoe Rotation:** {shoes}
- **Surface:** {surface}

## 🧘 Structural Integrity (The "Pain-Free" Proof)
- **Pre-Run Activation:** [x] 5 min Soleus Iso | [x] Glute Medius Bridges
- **Pain Score (Start):** 0/10
- **Pain Score (Finish):** 0/10

## 🧠 Qualitative Notes (GenAI Clinical Analysis)
* {ai_notes}

## 🛠 Integration Check
- [x] Garmin Data Exported
- [x] Soleus Isometrics scheduled (Mon/Tue/Fri)
"""

# ---------------------------------
# 4. PROCESSING LOOP
# ---------------------------------
print(f"🔄 Resuming analysis. Checking {len(df)} possible sessions...")

for index, row in df.iterrows():
    date_str = row['Date'].strftime('%Y-%m-%d')
    file_name = f"{date_str}-run.md"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    
    # SKIP IF ALREADY GENERATED
    if os.path.exists(file_path):
        continue

    # Filter out non-running activities
    if row['Distance'] < 2 or "Cycling" in str(row['Activity Type']):
        continue

    prompt = (
        f"Analyze this run: {row['Distance']}km at {row['Avg Pace']} min/km. "
        f"Avg HR: {row['Avg HR']}, Aerobic TE: {row['Aerobic TE']}. "
        "Provide a 2-sentence clinical assessment of metabolic cost and structural load."
    )

    success = False
    retries = 0

    while not success and retries < 3:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={'system_instruction': system_instruction}
            )
            ai_notes = response.text.strip()
            
            # Logic for Phase and Targets
            phase = "Marathon Build-Up" if row['Date'] > pd.to_datetime('2026-01-01') else "Base Maintenance"
            target = "4:37" if row['Distance'] > 15 else "5:15"
            
            content = detailed_tpl.format(
                title=row['Title'], date=date_str, phase=phase, 
                distance=row['Distance'], target_pace=target, 
                actual_pace=row['Avg Pace'], hr=row['Avg HR'], 
                shoes="Nike Alphafly 3" if row['Distance'] > 20 else "Nike Pegasus 41",
                surface="Treadmill" if "Treadmill" in str(row['Activity Type']) else "Road",
                ai_notes=ai_notes
            )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Generated: {file_name}")
            success = True
            time.sleep(10) # Protect Rate Limit

        except Exception as e:
            if "429" in str(e):
                print(f"⚠️ Quota hit for {date_str}. Waiting 60s...")
                time.sleep(60)
                retries += 1
            else:
                print(f"❌ Error on {date_str}: {e}")
                break

print("\n--- [PROCESS SYNCED] ---")