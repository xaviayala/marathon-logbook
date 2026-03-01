import pandas as pd
import os

def load_and_clean():
    # Input: The file with Aerobic TE restored
    input_file = '../data/garmin-activities-last6M.csv'
    output_file = '../data/processed_logbook.csv'

    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found.")
        return

    df = pd.read_csv(input_file)
    
    # 1. Mandatory Performance Columns
    columns_to_keep = [
        'Date', 'Title', 'Activity Type', 'Distance', 'Calories', 
        'Time', 'Avg HR', 'Max HR', 'Avg Pace', 'Best Pace', 'Aerobic TE'
    ]
    df = df[[c for c in columns_to_keep if c in df.columns]]
    
    # 2. Date Setup
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day_of_Week'] = df['Date'].dt.day_name()
    
    # 3. Effort-Based Hierarchy (The "No Bullshit" Logic)
    def label_activity(row):
        activity = str(row.get('Activity Type', '')).lower()
        title = str(row.get('Title', '')).lower()
        te = float(row.get('Aerobic TE', 0))
        
        # PRIORITY 1: Running is Performance
        # If you are on the road, you are training for the Sub-3:15.
        if 'run' in activity or 'run' in title:
            return 'Running / Performance'
            
        # PRIORITY 2: Cycling is defined by Intensity (TE)
        # 3.0+ = Improving/Overreaching (Performance Replacement)
        # < 3.0 = Maintenance/Recovery (Recovery)
        if 'cycling' in activity or 'spinning' in title:
            if te >= 3.0:
                return 'Indoor Cycling / Performance Replacement'
            else:
                return 'Indoor Cycling / Recovery'
        
        # PRIORITY 3: Default Strength Requirement
        # For entries on Mon, Tue, Fri that aren't runs or rides.
        return 'Isometrics / Core / Glutes'
            
    df['Category'] = df.apply(label_activity, axis=1)
    
    # 4. Export for AI Analysis
    df.to_csv(output_file, index=False)
    
    print("✅ Logic Corrected: Effort (TE) and Activity now drive categories.")
    print("-" * 45)
    print(df['Category'].value_counts())
    print("-" * 45)

if __name__ == "__main__":
    load_and_clean()