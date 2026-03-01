import pandas as pd
import os
from datetime import datetime

df = pd.read_csv('../data/processed_logbook.csv')
detailed_tpl = open('../templates/long-run-detailed-template.md').read()
simple_tpl = open('../templates/long-run-simplified-template.md').read()

def populate_templates():
    for _, row in df.iterrows():
        date_str = row['Date'].split(' ')[0]
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        is_weekend = dt.weekday() >= 5 # 5=Sat, 6=Sun
        
        # Select Template
        template = detailed_tpl if is_weekend else simple_tpl
        folder = "../logs/detailed/" if is_weekend else "../logs/simplified/"
        
        # Mapping Data
        output = template.replace("____ km", f"{row['Distance']} km")
        output = output.replace("____ min/km", f"{row['Avg Pace']} min/km")
        output = output.replace("____ bpm", f"{row['Avg HR']} bpm")
        output = output.replace("YYYY-MM-DD", date_str)
        
        # Save File
        filename = f"{folder}{date_str}-run.md"
        with open(filename, 'w') as f:
            f.write(output)

populate_templates()