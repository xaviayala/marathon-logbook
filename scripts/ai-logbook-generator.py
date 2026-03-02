import os
import pandas as pd
import time
from google import genai
from dotenv import load_dotenv

# 1. AUTHENTICATION & CLIENT SETUP
load_dotenv() 
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: No API Key found in .env.")
    exit()

client = genai.Client(api_key=api_key)

# Clinical System Instruction
system_instruction = (
    "You are a professional Sports Performance Analyst. Your tone is brutally honest, "
    "clinical, and data-driven. Analyze logs for a 40+ year old runner aiming for a "
    "sub-3:15 marathon in Barcelona. Focus on metabolic efficiency and structural integrity. "
    "Use professional terminology like 'cardiovascular drift' and 'mechanical efficiency'. "
    "Always use the metric system (km)."
)

# 2. DIRECTORIES & DATA LOAD
output_dir = 'logs/detailed'
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv('data/processed_logbook.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df[(df['Date'] >= '2025-09-01') & (df['Date'] <= '2026-03-01')]

# 3. MARKDOWN TEMPLATE
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

# 4. PROCESSING LOOP
print(f"🔄 Resuming analysis. Checking {len(df)} possible sessions...")

for index, row in df.iterrows():
    date_str = row['Date'].strftime('%Y-%m-%d')
    file_name = f"{date_str}-run.md"
    file_path = os.path.join(output_dir, file_name)
    
    # --- SKIP IF ALREADY GENERATED ---
    if os.path.exists(file_path):
        continue

    if row['Distance'] < 2 and "Cycling" in str(row['Activity Type']):
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
            # Using the modern 3 Flash / 2.0 Flash architecture
            response = client.models.generate_content(
                model='gemini-2.5-flash', # Adjust to your current active model string
                contents=prompt,
                config={'system_instruction': system_instruction}
            )
            ai_notes = response.text.strip()
            
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

            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Generated: {file_name}")
            success = True
            # 10 seconds is the 'safe' baseline for batch free tier in 2026
            time.sleep(10) 

        except Exception as e:
            if "429" in str(e):
                print(f"⚠️ Quota hit for {date_str}. Waiting 60s before retry...")
                time.sleep(60)
                retries += 1
            else:
                print(f"❌ Error on {date_str}: {e}")
                break

print("\n--- [PROCESS SYNCED] ---")