import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# 1. LOAD KEY
# This looks for a .env file locally. 
# If it doesn't find one (like on GitHub), it looks at the System Secrets.
load_dotenv() 
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: No API Key found in .env or GitHub Secrets.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')

def analyze_training():
    df = pd.read_csv('data/processed_logbook.csv')
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
    
    try:
        response = model.generate_content(prompt)
        report_header = "# 🏃 Sub-1:30 & Sub-3:15 Performance Dashboard\n\n## 🧠 Gemini Brutal Audit\n"
        
        with open('README.md', 'w') as f:
            f.write(report_header + response.text)
        print("Report Generated.")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    analyze_training()