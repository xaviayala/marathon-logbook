import pandas as pd
import time
import os
import re
from garminconnect import Garmin

# --- USER CONFIGURATION ---
EMAIL = "xavi.ayala@gmail.com"
PASSWORD = "Barc3l0na2026@garmin.com"
CSV_FILE = "../data/garmin-activities-last6M.csv"

# --- HELPER FUNCTIONS ---
def clean_val(val):
    if pd.isna(val) or str(val).strip() in ['--', '']:
        return None
    return re.sub(r'[^\d.]', '', str(val))

def pace_to_ms(pace_str):
    cleaned = str(pace_str).strip()
    if not cleaned or ':' not in cleaned or cleaned == '--': 
        return 0.0
    try:
        parts = cleaned.split(':')
        m, s = map(float, parts)
        seconds_per_km = (m * 60) + s
        return 1000 / seconds_per_km if seconds_per_km > 0 else 0.0
    except:
        return 0.0

def create_tcx(row):
    raw_type = str(row['Activity Type'])
    sport = "Biking" if "Cycling" in raw_type else "Running"
    dt_iso = str(row['Date']).replace(" ", "T") + "Z"
    
    dist_km = float(clean_val(row['Distance']) or 0.0)
    dist_m = dist_km * 1000
    
    t_parts = str(row['Time']).split(':')
    seconds = int(t_parts[0])*3600 + int(t_parts[1])*60 + float(t_parts[2])

    calories = clean_val(row['Calories']) or "0"
    avg_hr = clean_val(row['Avg HR'])
    max_hr = clean_val(row['Max HR'])
    cadence = clean_val(row['Avg Run Cadence'])
    max_speed = pace_to_ms(row['Best Pace'])
    
    # NEW: Aerobic TE handling
    te = clean_val(row.get('Aerobic TE', 0))
    event_type = row.get('Event Type', 'Training')
    
    # Force TE into Notes as a backup
    notes = f"Imported | Title: {row['Title']} | Type: {event_type} | Aerobic TE: {te} | TSS: {row['Training Stress Score®']}"

    # TCX with Garmin Extension v2 Namespace
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase 
  xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
  xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2">
  <Activities>
    <Activity Sport="{sport}">
      <Id>{dt_iso}</Id>
      <Lap StartTime="{dt_iso}">
        <TotalTimeSeconds>{seconds}</TotalTimeSeconds>
        <DistanceMeters>{dist_m:.2f}</DistanceMeters>
        <MaximumSpeed>{max_speed:.2f}</MaximumSpeed>
        <Calories>{calories}</Calories>"""
    if avg_hr: xml += f"\n        <AverageHeartRateBpm><Value>{avg_hr}</Value></AverageHeartRateBpm>"
    if max_hr: xml += f"\n        <MaximumHeartRateBpm><Value>{max_hr}</Value></MaximumHeartRateBpm>"
    if cadence: xml += f"\n        <Cadence>{cadence}</Cadence>"

    xml += f"""
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
      </Lap>
      <Notes>{notes}</Notes>
      <Extensions>
        <ns3:TPX>
          <ns3:TrainingEffect>{te}</ns3:TrainingEffect>
        </ns3:TPX>
      </Extensions>
    </Activity>
  </Activities>
</TrainingCenterDatabase>"""
    return xml

# --- MAIN EXECUTION ---
print("--- STARTING GARMIN SYNC WITH AEROBIC TE ---")
if not os.path.exists(CSV_FILE):
    print(f"CRITICAL ERROR: {CSV_FILE} not found.")
    exit()

try:
    df = pd.read_csv(CSV_FILE)
    client = Garmin(EMAIL, PASSWORD)
    client.login()
    print("✓ Login Successful.")

    for i, row in df.iterrows():
        xml_content = create_tcx(row)
        fname = f"temp_{i}.tcx"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(xml_content)
        
        # Consistent with your metric requirement: distance displayed in km
        print(f"[{i+1}/{len(df)}] Uploading: {row['Date']} | {row['Distance']} km | TE: {row.get('Aerobic TE', 'N/A')}...")
        try:
            client.upload_activity(fname)
            time.sleep(2) 
        except Exception as e:
            print(f"  × Error on row {i}: {e}")
        finally:
            if os.path.exists(fname): os.remove(fname)

    print("\n--- SYNC COMPLETE ---")
except Exception as e:
    print(f"CRITICAL FAILURE: {e}")