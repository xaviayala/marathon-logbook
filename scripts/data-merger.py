"""
Script: Merge Quantitative and Qualitative Training Data

Description:
This script merges quantitative training data (e.g., Garmin or Technogym
Activity CSV exports) with qualitative training notes (manual logbook
text entries).

It reads:
    1. A Garmin Activity CSV file (structured workout data)
    2. A plain text file containing dated training notes

The script aligns and merges both datasets by date into a single
"Master Record" output file.

Purpose:
The resulting consolidated dataset can be ingested by AI systems
such as Gemini or GPT for advanced performance analysis, trend
detection, and training insights generation.

Author: Xavier Ayala
Date: 2026-03-01
"""


import pandas as pd
import re

# 1. LOAD YOUR DATA
# Ensure you have exported your Garmin Activities as CSV from Garmin Connect Web
garmin_file = '../data/garmin_activities-last6M.csv' 
notes_file = '../data/training_notes.txt'

def parse_manual_notes(file_path):
    """
    Parses a text file where notes are formatted as: [YYYY-MM-DD] Note text
    """
    notes_data = []
    with open(file_path, 'r') as f:
        for line in f:
            match = re.search(r'\[(\d{4}-\d{2}-\d{2})\] (.*)', line)
            if match:
                notes_data.append({'Date': match.group(1), 'Note': match.group(2)})
    return pd.DataFrame(notes_data)

# 2. CLEAN GARMIN DATA
df_garmin = pd.read_csv(garmin_file)

# Standardize column names (Garmin usually uses "Date")
df_garmin['Date'] = pd.to_datetime(df_garmin['Date']).dt.strftime('%Y-%m-%d')

# 3. CLEAN MANUAL NOTES
df_notes = parse_manual_notes(notes_file)

# 4. MERGE DATA
# This combines your run data with your 'pain-free' qualitative notes
master_bitacro = pd.merge(df_garmin, df_notes, on='Date', how='outer').sort_values('Date')

# 5. EXPORT FOR GEMINI
master_bitacro.to_csv('Master_PainFree_Logbook.csv', index=False)
print("Master Logbook Created: Upload 'Master_PainFree_Logbook.csv' to Gemini now.")